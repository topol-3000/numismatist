from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependency.database import get_session
from api.routes.fastapi_users import current_active_user
from models import Item, User


async def verify_item_ownership(
    item_id: UUID,
    current_user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_session),
) -> Item:
    """
    Dependency that verifies item ownership and returns the item.

    Args:
        item_id: The UUID of the item to check
        current_user: The current authenticated user
        session: Database session

    Returns:
        The verified item

    Raises:
        HTTPException: If item not found or not owned by current user
    """
    item: Item | None = await session.scalar(
        select(Item).where(Item.id == str(item_id), Item.user_id == current_user.id)
    )
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return item
