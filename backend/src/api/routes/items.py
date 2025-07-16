from datetime import date
from typing import Any, Dict, Sequence
from uuid import UUID
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.engine import Result

from api.dependency.database import SessionDependency
from api.dependency.item import verify_item_ownership
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
price_history_router = APIRouter(prefix='/{item_id}/price-history', tags=['Price History'])


@router.get('/', response_model=list[ItemReadWithPurchasePrice])
async def get_user_items(
    session: SessionDependency,
    current_user: User = Depends(current_active_user),
) -> list[ItemReadWithPurchasePrice]:
    """Get all items for the current user with their purchase price information."""
    result: Result[Any] = await session.execute(
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
            ItemPriceHistory.date.label('purchase_date')
        )
        .join(ItemPriceHistory, Item.id == ItemPriceHistory.item_id)
        .where(
            Item.user_id == current_user.id,
            ItemPriceHistory.type == PriceType.PURCHASE
        )
        .order_by(Item.name)
    )

    return [ItemReadWithPurchasePrice(**dict(row._mapping)) for row in result]


@router.get('/{item_id}', response_model=ItemReadWithPriceHistory)
async def get_item(
    item_id: UUID,
    session: SessionDependency,
    current_user: User = Depends(current_active_user),
) -> Item:
    result: Result[Any] = await session.execute(
        select(Item)
        .options(selectinload(Item.price_history))
        .where(Item.id == str(item_id), Item.user_id == current_user.id)
    )
    item: Item | None = result.scalar_one_or_none()
    
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
) -> ItemReadWithPurchasePrice:
    item_dict: Dict[str, Any] = item_data.model_dump()
    purchase_price: int = item_dict.pop('purchase_price')
    purchase_date: date | None = item_dict.pop('purchase_date', None)

    item: Item = Item(**item_dict, user_id=current_user.id)
    session.add(item)
    await session.flush()

    price_history: ItemPriceHistory = ItemPriceHistory(
        item_id=item.id,
        price=purchase_price,
        type=PriceType.PURCHASE,
        date=purchase_date
    )
    session.add(price_history)
    
    await session.commit()
    await session.refresh(item)
    await session.refresh(price_history)

    return ItemReadWithPurchasePrice(
        id=item.id,
        name=item.name,
        year=item.year,
        description=item.description,
        images=item.images,
        material=item.material,
        weight=item.weight,
        user_id=item.user_id,
        collection_id=item.collection_id,
        purchase_price=price_history.price,
        purchase_date=price_history.date
    )


@router.patch('/{item_id}', response_model=ItemRead)
async def update_item(
    item_id: UUID,
    item_data: ItemUpdate,
    session: SessionDependency,
    current_user: User = Depends(current_active_user),
) -> Item:
    result: Result[Any] = await session.execute(
        select(Item).where(Item.id == str(item_id), Item.user_id == current_user.id)
    )
    item: Item | None = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )

    update_data: Dict[str, Any] = item_data.model_dump(exclude_unset=True)
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
) -> None:
    """Delete an item and all its price history."""
    result = await session.execute(
        delete(Item).where(Item.id == str(item_id), Item.user_id == current_user.id)
    )
    
    if result.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    await session.commit()


# Price History Endpoints

async def get_price_history_entry(
    item_id: str,
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
    history_result: Result[Any] = await session.execute(
        select(ItemPriceHistory)
        .where(
            ItemPriceHistory.id == history_id,
            ItemPriceHistory.item_id == item_id
        )
    )
    price_history: ItemPriceHistory | None = history_result.scalar_one_or_none()
    
    if not price_history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Price history entry not found"
        )
    
    return price_history


@price_history_router.get('/', response_model=list[ItemPriceHistoryRead])
async def get_item_price_history(
    session: SessionDependency,
    item: Item = Depends(verify_item_ownership),
) -> Sequence[ItemPriceHistory]:
    result: Result[Any] = await session.execute(
        select(ItemPriceHistory)
        .where(ItemPriceHistory.item_id == item.id)
        .order_by(ItemPriceHistory.date.desc())
    )
    return result.scalars().all()


@price_history_router.post('/', response_model=ItemPriceHistoryRead, status_code=status.HTTP_201_CREATED)
async def add_item_price_history(
    price_data: ItemPriceHistoryCreate,
    session: SessionDependency,
    item: Item = Depends(verify_item_ownership),
) -> ItemPriceHistory:
    price_history: ItemPriceHistory = ItemPriceHistory(
        item_id=item.id,
        price=price_data.price,
        type=PriceType.CURRENT,
        date=price_data.date
    )
    
    session.add(price_history)
    await session.commit()
    await session.refresh(price_history)
    return price_history


@price_history_router.patch('/{history_id}', response_model=ItemPriceHistoryRead)
async def update_item_price_history(
    history_id: int,
    price_data: ItemPriceHistoryUpdate,
    session: SessionDependency,
    item: Item = Depends(verify_item_ownership),
) -> ItemPriceHistory:
    price_history: ItemPriceHistory = await get_price_history_entry(item.id, history_id, session)

    update_data: Dict[str, Any] = price_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(price_history, field, value)
    
    await session.commit()
    await session.refresh(price_history)
    return price_history


@price_history_router.delete('/{history_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_item_price_history(
    history_id: int,
    session: SessionDependency,
    item: Item = Depends(verify_item_ownership),
) -> None:
    price_history: ItemPriceHistory = await get_price_history_entry(item.id, history_id, session)

    if price_history.type != PriceType.CURRENT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only current market price entries (type 'c') can be deleted. Purchase and sold prices are permanent records."
        )

    await session.delete(price_history)
    await session.commit()


router.include_router(price_history_router)
