from datetime import datetime as dt
from uuid import UUID
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from api.dependency.database import SessionDependency
from api.routes.fastapi_users import current_active_user
from models import Item, User, ItemPriceHistory
from schemas.item import ItemCreate, ItemRead, ItemReadWithPurchasePrice, ItemUpdate, ItemReadWithPriceHistory
from schemas.item_price_history import (
    ItemPriceHistoryCreate, 
    ItemPriceHistoryRead, 
    ItemPriceHistoryUpdate
)
from utils.enums import PriceType

router = APIRouter(prefix='/items', tags=['Items'])


@router.get('/', response_model=list[ItemReadWithPurchasePrice])
async def get_user_items(
    session: SessionDependency,
    current_user: User = Depends(current_active_user),
):
    """Get all items for the current user with their purchase price information."""
    result = await session.execute(
        select(
            Item.id,
            Item.name,
            Item.year,
            Item.description,
            Item.images,
            Item.material,
            Item.weight,
            Item.user_id,
            Item.collection_id,
            ItemPriceHistory.price.label('purchase_price'),
            ItemPriceHistory.datetime.label('purchase_date')
        )
        .join(ItemPriceHistory, Item.id == ItemPriceHistory.item_id)
        .where(
            Item.user_id == current_user.id,
            ItemPriceHistory.type == PriceType.PURCHASE
        )
        .order_by(Item.name)
    )

    return [dict(row._mapping) for row in result]


@router.get('/{item_id}', response_model=ItemReadWithPriceHistory)
async def get_item(
    item_id: UUID,
    session: SessionDependency,
    current_user: User = Depends(current_active_user),
):
    result = await session.execute(
        select(Item)
        .options(selectinload(Item.price_history))
        .where(Item.id == str(item_id), Item.user_id == current_user.id)
    )
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    return item


@router.post('/', response_model=ItemReadWithPurchasePrice, status_code=status.HTTP_201_CREATED)
async def create_item(
    item_data: ItemCreate,
    session: SessionDependency,
    current_user: User = Depends(current_active_user),
):
    item_dict = item_data.model_dump()
    purchase_price = item_dict.pop('purchase_price')
    purchase_date = item_dict.pop('purchase_date', None)

    item = Item(**item_dict, user_id=current_user.id)
    session.add(item)
    await session.flush()

    # Access the ID while the session is still active
    item_id = item.id
    
    price_history = ItemPriceHistory(
        item_id=item_id,
        price=purchase_price,
        type=PriceType.PURCHASE,
        datetime=purchase_date or dt.now()
    )
    session.add(price_history)
    
    # Access all attributes while the session is still active
    item_data_for_response = {
        'id': item_id,
        'name': item.name,
        'year': item.year,
        'description': item.description,
        'images': item.images,
        'material': item.material,
        'weight': item.weight,
        'user_id': item.user_id,
        'collection_id': item.collection_id,
    }
    
    await session.commit()
    await session.refresh(price_history)

    return ItemReadWithPurchasePrice(
        **item_data_for_response,
        purchase_price=price_history.price,
        purchase_date=price_history.datetime
    )


@router.patch('/{item_id}', response_model=ItemRead)
async def update_item(
    item_id: UUID,
    item_data: ItemUpdate,
    session: SessionDependency,
    current_user: User = Depends(current_active_user),
):
    result = await session.execute(
        select(Item).where(Item.id == str(item_id), Item.user_id == current_user.id)
    )
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )

    update_data = item_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)
    
    await session.commit()
    await session.refresh(item)
    return item


@router.delete('/{item_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    item_id: UUID,
    session: SessionDependency,
    current_user: User = Depends(current_active_user),
):
    """Delete an item and all its price history."""
    result = await session.execute(
        select(Item).where(Item.id == str(item_id), Item.user_id == current_user.id)
    )
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    await session.delete(item)
    await session.commit()


# Price History Endpoints

async def verify_item_ownership(
    item_id: UUID,
    current_user: User,
    session: AsyncSession
) -> None:
    """
    Verify that an item belongs to the current user.
    
    Args:
        item_id: The UUID of the item to check
        current_user: The current authenticated user
        session: Database session
        
    Raises:
        HTTPException: If item not found or not owned by current user
    """
    ownership_check = await session.scalar(
        select(
            exists().where(
                Item.id == str(item_id),
                Item.user_id == current_user.id
            )
        )
    )
    if not ownership_check:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found or not owned by current user"
        )


async def get_price_history_entry(
    item_id: UUID,
    history_id: int,
    session: AsyncSession
) -> ItemPriceHistory:
    """
    Get a specific price history entry for an item.
    
    Args:
        item_id: The UUID of the item
        history_id: The ID of the price history entry
        session: Database session
        
    Returns:
        The ItemPriceHistory object
        
    Raises:
        HTTPException: If price history entry not found
    """
    history_result = await session.execute(
        select(ItemPriceHistory)
        .where(
            ItemPriceHistory.id == history_id,
            ItemPriceHistory.item_id == str(item_id)
        )
    )
    price_history = history_result.scalar_one_or_none()
    
    if not price_history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Price history entry not found"
        )
    
    return price_history


@router.get('/{item_id}/price-history', response_model=list[ItemPriceHistoryRead])
async def get_item_price_history(
    item_id: UUID,
    session: SessionDependency,
    current_user: User = Depends(current_active_user),
):
    await verify_item_ownership(item_id, current_user, session)

    result = await session.execute(
        select(ItemPriceHistory)
        .where(ItemPriceHistory.item_id == str(item_id))
    )
    return result.scalars().all()


@router.post('/{item_id}/price-history', response_model=ItemPriceHistoryRead, status_code=status.HTTP_201_CREATED)
async def add_item_price_history(
    item_id: UUID,
    price_data: ItemPriceHistoryCreate,
    session: SessionDependency,
    current_user: User = Depends(current_active_user),
):
    await verify_item_ownership(item_id, current_user, session)

    price_history = ItemPriceHistory(
        item_id=str(item_id),
        price=price_data.price,
        type=PriceType.CURRENT,
        datetime=price_data.datetime or dt.now()
    )
    
    session.add(price_history)
    await session.commit()
    await session.refresh(price_history)
    return price_history


@router.patch('/{item_id}/price-history/{history_id}', response_model=ItemPriceHistoryRead)
async def update_item_price_history(
    item_id: UUID,
    history_id: int,
    price_data: ItemPriceHistoryUpdate,
    session: SessionDependency,
    current_user: User = Depends(current_active_user),
):
    await verify_item_ownership(item_id, current_user, session)
    price_history = await get_price_history_entry(item_id, history_id, session)

    update_data = price_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(price_history, field, value)
    
    await session.commit()
    await session.refresh(price_history)
    return price_history


@router.delete('/{item_id}/price-history/{history_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_item_price_history(
    item_id: UUID,
    history_id: int,
    session: SessionDependency,
    current_user: User = Depends(current_active_user),
):
    await verify_item_ownership(item_id, current_user, session)
    price_history = await get_price_history_entry(item_id, history_id, session)

    if price_history.type != PriceType.CURRENT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only current market price entries (type 'c') can be deleted. Purchase and sold prices are permanent records."
        )

    await session.delete(price_history)
    await session.commit()
