from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from api.dependency.database import SessionDependency
from api.routes.fastapi_users import current_active_user
from models import Transaction, Dealer, User, TransactionItem, Item
from schemas.transaction import TransactionCreate, TransactionRead
from schemas.transaction_item import TransactionItemCreate


router = APIRouter(prefix='/transactions', tags=['Transactions'])


@router.post('/', response_model=TransactionRead, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    transaction: TransactionCreate,
    session: SessionDependency,
    current_user: User = Depends(current_active_user),
):
    # Create a new transaction for the current user.
    # Check that the dealer exists and belongs to the current user
    dealer_id = getattr(transaction, 'dealer_id', None)
    dealer = None
    if dealer_id:
        result = await session.execute(
            select(Dealer).where(Dealer.id == dealer_id, Dealer.user_id == current_user.id)
        )
        dealer = result.scalar_one_or_none()

    if not dealer:
        dealer_data = getattr(transaction, 'dealer_data', None)
        if dealer_data and 'name' in dealer_data:
            dealer = Dealer(
                name=dealer_data['name'],
                contact_info=dealer_data.get('contact_info'),
                user_id=current_user.id
            )
            session.add(dealer)
            await session.flush()
            dealer_id = dealer.id

        else:
            raise HTTPException(status_code=404, detail='Dealer not found and no data to create')

    # Calculate total_amount if not provided and all item prices are present
    if transaction.total_amount is None:
        try:
            total = sum(float(item.price) for item in transaction.items if item.price is not None)
        except Exception:
            total = None

        # Only set if all prices are present
        if all(item.price is not None for item in transaction.items):
            db_transaction = Transaction(
                dealer_id=dealer_id,
                user_id=current_user.id,
                date=transaction.date,
                total_amount=total,
            )
        else:
            db_transaction = Transaction(
                dealer_id=dealer_id,
                user_id=current_user.id,
                date=transaction.date,
                total_amount=None,
            )
    else:
        db_transaction = Transaction(
            dealer_id=dealer_id,
            user_id=current_user.id,
            date=transaction.date,
            total_amount=transaction.total_amount,
        )

    session.add(db_transaction)
    await session.flush()  # Get transaction id before commit
    # Create TransactionItem for each item
    for item in transaction.items:
        item_id = getattr(item, 'item_id', None)
        db_item = None
        if item_id:
            item_result = await session.execute(
                select(Item).where(Item.id == item_id, Item.user_id == current_user.id)
            )
            db_item = item_result.scalar_one_or_none()

        if db_item:
            db_transaction_item = TransactionItem(
                transaction_id=db_transaction.id,
                item_id=db_item.id,
                price=item.price,
            )
            session.add(db_transaction_item)
        else:
            new_item = Item(
                name=getattr(item, 'name'),
                year=getattr(item, 'year'),
                material=getattr(item, 'material'),
                description=getattr(item, 'description', None),
                images=getattr(item, 'images', None),
                weight=getattr(item, 'weight', None),
                user_id=current_user.id
            )
            session.add(new_item)
            await session.flush()
            db_transaction_item = TransactionItem(
                transaction_id=db_transaction.id,
                item_id=new_item.id,
                price=item.price,
            )
            session.add(db_transaction_item)

    await session.commit()
    await session.refresh(db_transaction)
    # Load related transaction_items for serialization (selectinload)
    result = await session.execute(
        select(Transaction)
        .where(Transaction.id == db_transaction.id)
        .options(selectinload(Transaction.transaction_items))
    )
    db_transaction = result.scalar_one()
    return db_transaction

@router.get('/', response_model=List[TransactionRead])
async def get_transactions(
    session: SessionDependency,  # Remove = Depends()
    current_user: User = Depends(current_active_user),
    transaction_id: int | None = Query(None, description="Transaction ID to get a single transaction"),
):
    # Get all transactions for the current user, or a single transaction by id if transaction_id is provided.

    stmt = (
        select(Transaction)
        .where(Transaction.user_id == current_user.id)
        .options(selectinload(Transaction.transaction_items))
    )
    if transaction_id is not None:
        stmt = stmt.where(Transaction.id == transaction_id)

    result = await session.execute(stmt)
    transactions = result.scalars().all()
    if transaction_id is not None:
        if not transactions:
            raise HTTPException(status_code=404, detail='Transaction not found')

    return transactions

@router.patch('/{transaction_id}', response_model=TransactionRead)
async def update_transaction(
    transaction_id: int,
    transaction_update: TransactionCreate,  # You can create a separate TransactionUpdate schema for partial updates if needed
    session: SessionDependency,
    current_user: User = Depends(current_active_user),
):
    # Update a transaction by ID for the current user.
    result = await session.execute(
        select(Transaction)
        .where(Transaction.id == transaction_id, Transaction.user_id == current_user.id)
        .options(selectinload(Transaction.transaction_items))
    )
    db_transaction = result.scalar_one_or_none()
    if not db_transaction:
        raise HTTPException(status_code=404, detail='Transaction not found')

    # Update main fields
    db_transaction.date = transaction_update.date
    db_transaction.total_amount = transaction_update.total_amount
    db_transaction.dealer_id = transaction_update.dealer_id

    # Remove old TransactionItems
    # Instead of bulk delete, use ORM delete to avoid SQLAlchemy warnings
    result_items = await session.execute(
        select(TransactionItem).where(TransactionItem.transaction_id == transaction_id)
    )
    for ti in result_items.scalars().all():
        await session.delete(ti)

    # Add new TransactionItems
    for item in transaction_update.items:
        item_result = await session.execute(
            select(Item).where(Item.id == item.item_id, Item.user_id == current_user.id)
        )
        db_item = item_result.scalar_one_or_none()
        if not db_item:
            raise HTTPException(status_code=404, detail=f'Item {item.item_id} not found')

        db_transaction_item = TransactionItem(
            transaction_id=transaction_id,
            item_id=item.item_id,
            price=item.price,
        )
        session.add(db_transaction_item)

    await session.commit()
    await session.refresh(db_transaction)
    # Load related transaction_items
    result = await session.execute(
        select(Transaction)
        .where(Transaction.id == transaction_id)
        .options(selectinload(Transaction.transaction_items))
    )
    db_transaction = result.scalar_one()
    return db_transaction

@router.delete('/{transaction_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(
    transaction_id: int,
    session: SessionDependency,
    current_user: User = Depends(current_active_user),
):
    # Delete a transaction by ID for the current user.
    result = await session.execute(
        select(Transaction).where(Transaction.id == transaction_id, Transaction.user_id == current_user.id)
    )
    db_transaction = result.scalar_one_or_none()
    if not db_transaction:
        raise HTTPException(status_code=404, detail='Transaction not found')

    # ORM delete for all related TransactionItems to avoid warnings
    result_items = await session.execute(
        select(TransactionItem).where(TransactionItem.transaction_id == transaction_id)
    )
    for ti in result_items.scalars().all():
        await session.delete(ti)

    await session.delete(db_transaction)
    await session.commit()
    return None
