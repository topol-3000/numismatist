from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from api.dependency.database import SessionDependency
from api.routes.fastapi_users import current_active_user
from models import Dealer, User, Transaction
from schemas.dealer import DealerCreate, DealerRead, DealerUpdate
from schemas.transaction import TransactionRead

router = APIRouter(prefix='/dealers', tags=['Dealers'])

@router.get('/', response_model=list[DealerRead])
async def get_user_dealers(
    session: SessionDependency,
    current_user: User = Depends(current_active_user),
):
    # Get all dealers belonging to the current user.
    result = await session.execute(
        select(Dealer).where(Dealer.user_id == current_user.id).order_by(Dealer.name)
    )
    dealers = result.scalars().all()
    return dealers

@router.post('/', response_model=DealerRead, status_code=status.HTTP_201_CREATED)
async def create_dealer(
    dealer: DealerCreate,
    session: SessionDependency,
    current_user: User = Depends(current_active_user),
):
    # Create a new dealer for the current user.
    db_dealer = Dealer(**dealer.model_dump(), user_id=current_user.id)
    session.add(db_dealer)
    await session.commit()
    await session.refresh(db_dealer)
    return db_dealer

@router.get('/{dealer_id}', response_model=DealerRead)
async def get_dealer(
    dealer_id: int,
    session: SessionDependency,
    current_user: User = Depends(current_active_user),
):
    # Get a dealer by ID for the current user.
    result = await session.execute(
        select(Dealer).where(Dealer.id == dealer_id, Dealer.user_id == current_user.id)
    )
    dealer = result.scalar_one_or_none()
    if not dealer:
        raise HTTPException(status_code=404, detail='Dealer not found')

    return dealer

@router.patch('/{dealer_id}', response_model=DealerRead)
async def update_dealer(
    dealer_id: int,
    dealer_update: DealerUpdate,
    session: SessionDependency,
    current_user: User = Depends(current_active_user),
):
    # Update a dealer by ID for the current user.
    result = await session.execute(
        select(Dealer).where(Dealer.id == dealer_id, Dealer.user_id == current_user.id)
    )
    dealer = result.scalar_one_or_none()
    if not dealer:
        raise HTTPException(status_code=404, detail='Dealer not found')

    for key, value in dealer_update.model_dump(exclude_unset=True).items():
        setattr(dealer, key, value)

    await session.commit()
    await session.refresh(dealer)
    return dealer

@router.delete('/{dealer_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_dealer(
    dealer_id: int,
    session: SessionDependency,
    current_user: User = Depends(current_active_user),
):
    # Delete a dealer by ID for the current user.
    result = await session.execute(
        select(Dealer).where(Dealer.id == dealer_id, Dealer.user_id == current_user.id)
    )
    dealer = result.scalar_one_or_none()
    if not dealer:
        raise HTTPException(status_code=404, detail='Dealer not found')

    await session.delete(dealer)
    await session.commit()
    return None

@router.get('/{dealer_id}/transactions/', response_model=list[TransactionRead])
async def get_dealer_transactions(
    dealer_id: int,
    session: SessionDependency,
    current_user: User = Depends(current_active_user),
):
    # Get all transactions for a dealer belonging to the current user.
    result = await session.execute(
        select(Transaction)
        .options(joinedload(Transaction.dealer))
        .where(
            Transaction.dealer_id == dealer_id,
            Transaction.user_id == current_user.id
        )
    )
    transactions = result.scalars().all()
    return transactions
