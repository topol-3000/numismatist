import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, timezone
from models.price_history import PriceHistory
from models.item import Item
from schemas.price_history import PriceHistoryCreate, PriceHistoryRead, PriceHistoryBase
from api.dependency.database import get_session
from api.routes.fastapi_users import current_active_user
from models.user import User


router = APIRouter(prefix="/price-history", tags=["PriceHistory"])


@router.post("/", response_model=PriceHistoryRead)
async def create_price_history(
    item_id: str,
    price_history: PriceHistoryCreate,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(current_active_user),
):
    try:
        item_uuid = uuid.UUID(item_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid item_id format")

    item = await session.scalar(select(Item).where(Item.id == str(item_uuid), Item.user_id == user.id))
    if not item:
        raise HTTPException(status_code=404, detail="Item not found or not owned by user")

    # BUSINESS RULE: If there is already an OUT price, forbid adding new price history
    out_exists = await session.scalar(select(PriceHistory).where(PriceHistory.item_id == item_uuid, PriceHistory.price_type == 'out'))
    if out_exists:
        raise HTTPException(status_code=403, detail="Cannot add price history after sale (OUT price exists)")

    db_obj = PriceHistory(
        item_id=item_uuid,
        price=price_history.price,
        price_type=price_history.price_type,
        timestamp=price_history.timestamp or datetime.now(timezone.utc),
        note=price_history.note,
    )
    session.add(db_obj)
    await session.commit()
    await session.refresh(db_obj)
    return PriceHistoryRead.model_validate({
        "id": str(db_obj.id),
        "item_id": str(db_obj.item_id),
        "price": db_obj.price,
        "price_type": str(db_obj.price_type),
        "timestamp": db_obj.timestamp,
        "note": db_obj.note,
    })


@router.get("/item/{item_id}", response_model=list[PriceHistoryRead])
async def get_price_history_for_item(
    item_id: str,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(current_active_user),
):
    try:
        item_uuid = uuid.UUID(item_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid item_id format")

    item = await session.scalar(select(Item).where(Item.id == str(item_uuid), Item.user_id == user.id))
    if not item:
        raise HTTPException(status_code=404, detail="Item not found or not owned by user")

    result = await session.execute(select(PriceHistory).where(PriceHistory.item_id == item_uuid))
    items = result.scalars().all()
    return [
        PriceHistoryRead.model_validate({
            "id": str(obj.id),
            "item_id": str(obj.item_id),
            "price": obj.price,
            "price_type": str(obj.price_type),
            "timestamp": obj.timestamp,
            "note": obj.note,
        }) for obj in items
    ]


class PriceHistoryUpdate(PriceHistoryBase):
    pass


@router.patch("/{price_history_id}", response_model=PriceHistoryRead)
async def update_price_history(
    price_history_id: str,
    price_history: PriceHistoryUpdate = None,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(current_active_user),
):
    try:
        price_history_uuid = uuid.UUID(price_history_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid price_history_id format")

    db_obj = await session.get(PriceHistory, str(price_history_uuid))
    if not db_obj:
        raise HTTPException(status_code=404, detail="PriceHistory not found")

    # Check user owns the item
    item = await session.scalar(select(Item).where(Item.id == str(db_obj.item_id), Item.user_id == user.id))
    if not item:
        raise HTTPException(status_code=403, detail="Not allowed to edit this price history")

    # BUSINESS RULE: If there is an OUT price for this item, forbid any update
    out_exists = await session.scalar(select(PriceHistory).where(PriceHistory.item_id == db_obj.item_id, PriceHistory.price_type == 'out'))
    if out_exists:
        raise HTTPException(status_code=403, detail="Cannot update price history after sale (OUT price exists)")

    update_data = price_history.model_dump(exclude_unset=True)
    # BUSINESS RULE: For IN or OUT, forbid changing timestamp
    if db_obj.price_type in ('in', 'out') and 'timestamp' in update_data:
        raise HTTPException(status_code=403, detail="Cannot change timestamp for IN or OUT price history record")
    for field, value in update_data.items():
        setattr(db_obj, field, value)

    await session.commit()
    await session.refresh(db_obj)
    return PriceHistoryRead.model_validate({
        "id": str(db_obj.id),
        "item_id": str(db_obj.item_id),
        "price": db_obj.price,
        "price_type": str(db_obj.price_type),
        "timestamp": db_obj.timestamp,
        "note": db_obj.note,
    })


@router.delete("/{price_history_id}", status_code=204)
async def delete_price_history(
    price_history_id: str,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(current_active_user),
):
    try:
        price_history_uuid = uuid.UUID(price_history_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid price_history_id format")

    db_obj = await session.get(PriceHistory, str(price_history_uuid))
    if not db_obj:
        raise HTTPException(status_code=404, detail="PriceHistory not found")

    # Check user owns the item
    item = await session.scalar(select(Item).where(Item.id == str(db_obj.item_id), Item.user_id == user.id))
    if not item:
        raise HTTPException(status_code=403, detail="Not allowed to delete this price history")

    # BUSINESS RULE: If there is an OUT price for this item, forbid any delete
    out_exists = await session.scalar(select(PriceHistory).where(PriceHistory.item_id == db_obj.item_id, PriceHistory.price_type == 'out'))
    if out_exists:
        raise HTTPException(status_code=403, detail="Cannot delete price history after sale (OUT price exists)")

    await session.delete(db_obj)
    await session.commit()
