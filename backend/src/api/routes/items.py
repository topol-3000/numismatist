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
    """Create a new item."""
    item = Item(**item_data.model_dump(), user_id=current_user.id)
    session.add(item)
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
