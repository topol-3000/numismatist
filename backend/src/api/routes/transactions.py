from fastapi import APIRouter, Depends, HTTPException, status
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
    """
    Create a new transaction for the current user.

    Args:
        transaction (TransactionCreate): Transaction creation data.
        session (AsyncSession): Database session dependency.
        current_user (User): Current authenticated user.
    Returns:
        TransactionRead: Created transaction object.
    Raises:
        HTTPException: 404 if dealer or item not found or not owned by user.
    """
    # Check that the dealer exists and belongs to the current user
    result = await session.execute(
        select(Dealer).where(Dealer.id == transaction.dealer_id, Dealer.user_id == current_user.id)
    )
    dealer = result.scalar_one_or_none()
    if not dealer:
        raise HTTPException(status_code=404, detail='Dealer not found')
    db_transaction = Transaction(
        dealer_id=transaction.dealer_id,
        user_id=current_user.id,
        date=transaction.date,
        total_amount=transaction.total_amount,
    )
    session.add(db_transaction)
    await session.flush()  # Get transaction id before commit
    # Create TransactionItem for each item
    for item in transaction.items:
        # Check that the item belongs to the user
        item_result = await session.execute(
            select(Item).where(Item.id == item.item_id, Item.user_id == current_user.id)
        )
        db_item = item_result.scalar_one_or_none()
        if not db_item:
            raise HTTPException(status_code=404, detail=f'Item {item.item_id} not found')
        db_transaction_item = TransactionItem(
            transaction_id=db_transaction.id,
            item_id=item.item_id,
            price=item.price,
            quantity=item.quantity,
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

@router.get('/', response_model=list[TransactionRead])
async def get_transactions(
    session: SessionDependency,
    current_user: User = Depends(current_active_user),
):
    """
    Get all transactions belonging to the current user.

    Args:
        session (AsyncSession): Database session dependency.
        current_user (User): Current authenticated user.
    Returns:
        List[TransactionRead]: List of transactions for the user.
    """
    result = await session.execute(
        select(Transaction).where(Transaction.user_id == current_user.id).options(selectinload(Transaction.transaction_items))
    )
    return result.scalars().all()

@router.get('/{transaction_id}', response_model=TransactionRead)
async def get_transaction(
    transaction_id: int,
    session: SessionDependency,
    current_user: User = Depends(current_active_user),
):
    """
    Get a transaction by ID for the current user.

    Args:
        transaction_id (int): Transaction ID.
        session (AsyncSession): Database session dependency.
        current_user (User): Current authenticated user.
    Returns:
        TransactionRead: Transaction object if found.
    Raises:
        HTTPException: 404 if transaction not found or not owned by user.
    """
    result = await session.execute(
        select(Transaction)
        .where(Transaction.id == transaction_id, Transaction.user_id == current_user.id)
        .options(selectinload(Transaction.transaction_items))
    )
    transaction = result.scalar_one_or_none()
    if not transaction:
        raise HTTPException(status_code=404, detail='Transaction not found')

    return transaction
