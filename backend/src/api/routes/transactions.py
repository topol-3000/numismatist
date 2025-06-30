from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from api.dependency.database import SessionDependency
from api.routes.fastapi_users import current_active_user
from models import Transaction, Dealer, User
from schemas.transaction import TransactionCreate, TransactionRead

router = APIRouter(prefix='/transactions', tags=['Transactions'])

@router.post('/', response_model=TransactionRead, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    transaction: TransactionCreate,
    session: SessionDependency,
    current_user: User = Depends(current_active_user),
):
    # Проверяем, что дилер существует и принадлежит пользователю
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
    await session.commit()
    await session.refresh(db_transaction)
    return db_transaction

@router.get('/', response_model=list[TransactionRead])
async def get_transactions(
    session: SessionDependency,
    current_user: User = Depends(current_active_user),
):
    result = await session.execute(
        select(Transaction).where(Transaction.user_id == current_user.id)
    )
    return result.scalars().all()
