from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from api.dependency.database import SessionDependency
from api.routes.fastapi_users import current_active_user
from models import Dealer, User
from schemas.dealer import DealerCreate, DealerRead, DealerUpdate

router = APIRouter(prefix="/dealers", tags=["Dealers"])


@router.get("/", response_model=list[DealerRead])
async def get_dealers(session: SessionDependency, current_user: User = Depends(current_active_user)):
    result = await session.execute(select(Dealer).where(Dealer.user_id == current_user.id).order_by(Dealer.name))
    return result.scalars().all()


@router.get("/{dealer_id}", response_model=DealerRead)
async def get_dealer(
    dealer_id: int,
    session: SessionDependency,
    current_user: User = Depends(current_active_user),
):
    dealer = await session.get(Dealer, dealer_id)
    if not dealer or dealer.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Dealer not found")

    return dealer


@router.post("/", response_model=DealerRead, status_code=status.HTTP_201_CREATED)
async def create_dealer(
    dealer_data: DealerCreate,
    session: SessionDependency,
    current_user: User = Depends(current_active_user),
):
    dealer = Dealer(**dealer_data.model_dump(), user_id=current_user.id)
    session.add(dealer)
    await session.commit()
    await session.refresh(dealer)
    return dealer


@router.put("/{dealer_id}", response_model=DealerRead)
async def update_dealer(
    dealer_id: int,
    dealer_data: DealerUpdate,
    session: SessionDependency,
    current_user: User = Depends(current_active_user),
):
    dealer = await session.get(Dealer, dealer_id)
    if not dealer or dealer.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Dealer not found")

    update_data = dealer_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(dealer, field, value)

    await session.commit()
    await session.refresh(dealer)
    return dealer


@router.delete("/{dealer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_dealer(
    dealer_id: int,
    session: SessionDependency,
    current_user: User = Depends(current_active_user),
):
    dealer = await session.get(Dealer, dealer_id)
    if not dealer or dealer.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Dealer not found")

    await session.delete(dealer)
    await session.commit()
