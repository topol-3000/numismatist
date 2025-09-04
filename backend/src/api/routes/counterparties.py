from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from api.dependency.database import SessionDependency
from api.routes.fastapi_users import current_active_user
from models import Counterparty, User
from schemas.counterparty import CounterpartyCreate, CounterpartyRead, CounterpartyUpdate

router = APIRouter(prefix="/counterparties", tags=["Counterparties"])


@router.get("/", response_model=list[CounterpartyRead])
async def get_counterparties(session: SessionDependency, current_user: User = Depends(current_active_user)):
    result = await session.execute(
        select(Counterparty).where(Counterparty.user_id == current_user.id).order_by(Counterparty.name)
    )
    return result.scalars().all()


@router.get("/{counterparty_id}", response_model=CounterpartyRead)
async def get_counterparty(
    counterparty_id: int,
    session: SessionDependency,
    current_user: User = Depends(current_active_user),
):
    counterparty = await session.get(Counterparty, counterparty_id)
    if not counterparty or counterparty.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Counterparty not found")

    return counterparty


@router.post("/", response_model=CounterpartyRead, status_code=status.HTTP_201_CREATED)
async def create_counterparty(
    counterparty_data: CounterpartyCreate,
    session: SessionDependency,
    current_user: User = Depends(current_active_user),
):
    counterparty = Counterparty(**counterparty_data.model_dump(), user_id=current_user.id)
    session.add(counterparty)
    await session.commit()
    await session.refresh(counterparty)
    return counterparty


@router.put("/{counterparty_id}", response_model=CounterpartyRead)
async def update_counterparty(
    counterparty_id: int,
    counterparty_data: CounterpartyUpdate,
    session: SessionDependency,
    current_user: User = Depends(current_active_user),
):
    counterparty = await session.get(Counterparty, counterparty_id)
    if not counterparty or counterparty.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Counterparty not found")

    update_data = counterparty_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(counterparty, field, value)

    await session.commit()
    await session.refresh(counterparty)
    return counterparty


@router.delete("/{counterparty_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_counterparty(
    counterparty_id: int,
    session: SessionDependency,
    current_user: User = Depends(current_active_user),
):
    counterparty = await session.get(Counterparty, counterparty_id)
    if not counterparty or counterparty.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Counterparty not found")

    await session.delete(counterparty)
    await session.commit()
