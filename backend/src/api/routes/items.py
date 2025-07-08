from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependency.database import SessionDependency
from api.routes.fastapi_users import current_active_user
from models import Item, User
from schemas.item import ItemCreate, ItemRead, ItemUpdate

router = APIRouter(prefix='/items', tags=['Items'])


@router.get('/', response_model=list[ItemRead])
async def get_user_items(
    session: SessionDependency,
    current_user: User = Depends(current_active_user),
):
    """Get all items for the current user."""
    result = await session.execute(
        select(Item).where(Item.user_id == current_user.id).order_by(Item.name)
    )
    items = result.scalars().all()
    return items


@router.get('/{item_id}', response_model=ItemRead)
async def get_item(
    item_id: str,
    session: SessionDependency,
    current_user: User = Depends(current_active_user),
):
    """Get a specific item by ID."""
    result = await session.execute(
        select(Item)
        .where(Item.id == item_id, Item.user_id == current_user.id)
    )
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    return item


@router.post('/', response_model=ItemRead, status_code=status.HTTP_201_CREATED)
async def create_item(
    item_data: ItemCreate,
    session: SessionDependency,
    current_user: User = Depends(current_active_user),
):
    """Create a new item, optionally linking to a transaction and/or dealer."""
    # 1. Create the item itself
    item = Item(**{k: v for k, v in item_data.model_dump().items() if k in Item.__table__.columns.keys()}, user_id=current_user.id)
    session.add(item)
    await session.flush()  # get item.id

    # 2. Transaction logic
    price = getattr(item_data, 'price', None)
    dealer_id = getattr(item_data, 'dealer_id', None)
    dealer_data = getattr(item_data, 'dealer_data', None)
    transaction_id = getattr(item_data, 'transaction_id', None)
    transaction = None

    # If price is set but neither dealer_id nor dealer_data nor transaction_id, return error
    if price is not None and not (dealer_id or dealer_data or transaction_id):
        raise HTTPException(status_code=404, detail="Dealer info required for transaction")

    if price is not None and (dealer_id or dealer_data) and not transaction_id:
        # Create dealer if needed
        if not dealer_id and dealer_data and 'name' in dealer_data:
            from models.dealer import Dealer
            dealer = Dealer(
                name=dealer_data['name'],
                contact_info=dealer_data.get('contact_info'),
                user_id=current_user.id
            )
            session.add(dealer)
            await session.flush()
            dealer_id = dealer.id

        # Create new transaction
        from models.transaction import Transaction
        from datetime import date
        transaction = Transaction(
            dealer_id=dealer_id,
            user_id=current_user.id,
            date=date.today(),
            total_amount=price
        )
        session.add(transaction)
        await session.flush()
        transaction_id = transaction.id
    elif transaction_id:
        from models.transaction import Transaction
        transaction = await session.get(Transaction, transaction_id)
        if not transaction or transaction.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="Transaction not found or not yours")
        # Update total_amount
        transaction.total_amount = (transaction.total_amount or 0) + (price or 0)
        await session.flush()

    # 3. Link item to transaction if needed
    if transaction_id and price is not None:
        from models.transaction_item import TransactionItem
        ti = TransactionItem(transaction_id=transaction_id, item_id=item.id, price=price)
        session.add(ti)
        await session.flush()

    await session.commit()
    await session.refresh(item)
    return item


@router.put('/{item_id}', response_model=ItemRead)
async def update_item(
    item_id: str,
    item_data: ItemUpdate,
    session: SessionDependency,
    current_user: User = Depends(current_active_user),
):
    """Update an existing item."""
    result = await session.execute(
        select(Item).where(Item.id == item_id, Item.user_id == current_user.id)
    )
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    # Update only provided fields
    update_data = item_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)
    
    await session.commit()
    await session.refresh(item)
    return item


@router.delete('/{item_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    item_id: str,
    session: SessionDependency,
    current_user: User = Depends(current_active_user),
):
    """Delete an item."""
    result = await session.execute(
        select(Item).where(Item.id == item_id, Item.user_id == current_user.id)
    )
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    await session.delete(item)
    await session.commit()
