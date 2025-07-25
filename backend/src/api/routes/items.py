from collections.abc import Sequence
from datetime import date
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import delete, select
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from api.dependency.database import SessionDependency
from api.dependency.item import verify_item_ownership
from api.routes.fastapi_users import current_active_user
from models import Item, ItemImage, ItemPriceHistory, User
from schemas.item import (
    ItemCreate,
    ItemRead,
    ItemReadWithPriceHistory,
    ItemReadWithPurchasePrice,
    ItemUpdate,
)
from schemas.item_image import (
    ItemImageRead,
)
from schemas.item_price_history import (
    ItemPriceHistoryCreate,
    ItemPriceHistoryRead,
    ItemPriceHistoryUpdate,
)
from services.storage import StorageService, get_storage_service
from utils.enums import ImageType, PriceType

router = APIRouter(prefix="/items", tags=["Items"])
price_history_router = APIRouter(prefix="/{item_id}/price-history", tags=["Price History"])


@router.get("/", response_model=list[ItemReadWithPurchasePrice])
async def get_user_items(
    session: SessionDependency,
    current_user: User = Depends(current_active_user),
) -> list[ItemReadWithPurchasePrice]:
    """Get all items for the current user with their purchase price information."""
    result: Result[Any] = await session.execute(
        select(
            Item.id,
            Item.name,
            Item.year,
            Item.description,
            Item.material,
            Item.weight,
            Item.user_id,
            Item.collection_id,
            ItemPriceHistory.price.label("purchase_price"),
            ItemPriceHistory.date.label("purchase_date"),
        )
        .join(ItemPriceHistory, Item.id == ItemPriceHistory.item_id)
        .where(Item.user_id == current_user.id, ItemPriceHistory.type == PriceType.PURCHASE)
        .order_by(Item.name)
    )

    return [
        ItemReadWithPurchasePrice(
            id=str(row.id),
            name=row.name,
            year=row.year,
            description=row.description,
            material=row.material,
            weight=row.weight,
            user_id=row.user_id,
            collection_id=row.collection_id,
            purchase_price=row.purchase_price,
            purchase_date=row.purchase_date,
        )
        for row in result
    ]


@router.get("/{item_id}", response_model=ItemReadWithPriceHistory)
async def get_item(
    item_id: UUID,
    session: SessionDependency,
    current_user: User = Depends(current_active_user),
) -> Item:
    result: Result[Any] = await session.execute(
        select(Item)
        .options(selectinload(Item.price_history))
        .where(Item.id == str(item_id), Item.user_id == current_user.id)
    )
    item: Item | None = result.scalar_one_or_none()

    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    return item


@router.post("/", response_model=ItemReadWithPurchasePrice, status_code=status.HTTP_201_CREATED)
async def create_item(
    item_data: ItemCreate,
    session: SessionDependency,
    current_user: User = Depends(current_active_user),
) -> ItemReadWithPurchasePrice:
    item_dict: dict[str, Any] = item_data.model_dump()
    purchase_price: int = item_dict.pop("purchase_price")
    purchase_date: date | None = item_dict.pop("purchase_date", None)

    item: Item = Item(**item_dict, user_id=current_user.id)
    session.add(item)
    await session.flush()

    price_history: ItemPriceHistory = ItemPriceHistory(
        item_id=item.id,
        price=purchase_price,
        type=PriceType.PURCHASE,
        date=purchase_date,
    )
    session.add(price_history)

    await session.commit()
    await session.refresh(item)
    await session.refresh(price_history)

    return ItemReadWithPurchasePrice(
        id=item.id,
        name=item.name,
        year=item.year,
        description=item.description,
        material=item.material,
        weight=item.weight,
        user_id=item.user_id,
        collection_id=item.collection_id,
        purchase_price=price_history.price,
        purchase_date=price_history.date,
    )


@router.patch("/{item_id}", response_model=ItemRead)
async def update_item(
    item_id: UUID,
    item_data: ItemUpdate,
    session: SessionDependency,
    current_user: User = Depends(current_active_user),
) -> Item:
    result: Result[Any] = await session.execute(
        select(Item).where(Item.id == str(item_id), Item.user_id == current_user.id)
    )
    item: Item | None = result.scalar_one_or_none()

    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    update_data: dict[str, Any] = item_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)

    await session.commit()
    await session.refresh(item)
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    item_id: UUID,
    session: SessionDependency,
    current_user: User = Depends(current_active_user),
) -> None:
    """Delete an item and all its price history."""
    result = await session.execute(delete(Item).where(Item.id == str(item_id), Item.user_id == current_user.id))

    if result.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    await session.commit()


# Price History Endpoints


async def get_price_history_entry(item_id: str, history_id: int, session: AsyncSession) -> ItemPriceHistory:
    """
    Get a specific price history entry for an item.

    Args:
        item_id: The UUID of the item
        history_id: The ID of the price history entry
        session: Database session

    Returns:
        The ItemPriceHistory object

    Raises:
        HTTPException: If price history entry not found
    """
    history_result: Result[Any] = await session.execute(
        select(ItemPriceHistory).where(ItemPriceHistory.id == history_id, ItemPriceHistory.item_id == item_id)
    )
    price_history: ItemPriceHistory | None = history_result.scalar_one_or_none()

    if not price_history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Price history entry not found",
        )

    return price_history


@price_history_router.get("/", response_model=list[ItemPriceHistoryRead])
async def get_item_price_history(
    session: SessionDependency,
    item: Item = Depends(verify_item_ownership),
) -> Sequence[ItemPriceHistory]:
    result: Result[Any] = await session.execute(
        select(ItemPriceHistory).where(ItemPriceHistory.item_id == item.id).order_by(ItemPriceHistory.date.desc())
    )
    return result.scalars().all()


@price_history_router.post("/", response_model=ItemPriceHistoryRead, status_code=status.HTTP_201_CREATED)
async def add_item_price_history(
    price_data: ItemPriceHistoryCreate,
    session: SessionDependency,
    item: Item = Depends(verify_item_ownership),
) -> ItemPriceHistory:
    price_history: ItemPriceHistory = ItemPriceHistory(
        item_id=item.id,
        price=price_data.price,
        type=PriceType.CURRENT,
        date=price_data.date,
    )

    session.add(price_history)
    await session.commit()
    await session.refresh(price_history)
    return price_history


@price_history_router.patch("/{history_id}", response_model=ItemPriceHistoryRead)
async def update_item_price_history(
    history_id: int,
    price_data: ItemPriceHistoryUpdate,
    session: SessionDependency,
    item: Item = Depends(verify_item_ownership),
) -> ItemPriceHistory:
    price_history: ItemPriceHistory = await get_price_history_entry(item.id, history_id, session)

    update_data: dict[str, Any] = price_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(price_history, field, value)

    await session.commit()
    await session.refresh(price_history)
    return price_history


@price_history_router.delete("/{history_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item_price_history(
    history_id: int,
    session: SessionDependency,
    item: Item = Depends(verify_item_ownership),
) -> None:
    price_history: ItemPriceHistory = await get_price_history_entry(item.id, history_id, session)

    if price_history.type != PriceType.CURRENT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Only current market price entries (type 'current') can be deleted. "
                "Purchase and sold prices are permanent records."
            ),
        )

    await session.delete(price_history)
    await session.commit()


# =================================================
# ITEM IMAGES ENDPOINTS
# =================================================

images_router = APIRouter(prefix="/{item_id}/images", tags=["Item Images"])


@images_router.get("/", response_model=list[ItemImageRead])
async def get_item_images(
    session: SessionDependency,
    item: Item = Depends(verify_item_ownership),
) -> list[ItemImage]:
    """Get all images for an item."""
    result: Result[Any] = await session.execute(
        select(ItemImage).where(ItemImage.item_id == item.id).order_by(ItemImage.type)
    )

    return list(result.scalars().all())


@images_router.post("/", response_model=ItemImageRead, status_code=status.HTTP_201_CREATED)
async def upload_item_image(
    session: SessionDependency,
    item: Item = Depends(verify_item_ownership),
    storage_service: StorageService = Depends(get_storage_service),
    file: UploadFile = File(...),
    file_type: ImageType = Form(...),
) -> ItemImage:
    """Upload a new image file for an item."""

    # Validate file type, only allow images
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File must be an image")

    # Only allow unique image types to have one instance per item
    if file_type.is_unique():
        existing_image_result: Result[Any] = await session.execute(
            select(ItemImage).where(ItemImage.item_id == item.id, ItemImage.type == file_type)
        )
        existing_image: ItemImage | None = existing_image_result.scalar_one_or_none()

        if existing_image:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"An image of type '{file_type}' already exists for this item. "
                f"Please delete the existing image first.",
            )

    # Upload file to an external storage
    file_path, file_size = await storage_service.upload_file(file=file, folder=f"items/{item.id}")

    try:
        image = ItemImage(
            item_id=item.id,
            type=file_type,
            file_path=file_path,
            file_size=file_size,
            mime_type=file.content_type,
        )

        session.add(image)
        await session.commit()
        await session.refresh(image)

        return image

    except Exception as e:
        await storage_service.delete_file(file_path)
        raise e


@images_router.get("/{image_id}", response_model=ItemImageRead)
async def get_item_image(
    image_id: UUID,
    session: SessionDependency,
    item: Item = Depends(verify_item_ownership),
) -> ItemImage:
    """Get a specific image for an item."""
    result: Result[Any] = await session.execute(
        select(ItemImage).where(ItemImage.id == str(image_id), ItemImage.item_id == item.id)
    )
    image: ItemImage | None = result.scalar_one_or_none()

    if not image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")

    return image


@images_router.delete("/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item_image(
    image_id: UUID,
    session: SessionDependency,
    item: Item = Depends(verify_item_ownership),
    storage_service: StorageService = Depends(get_storage_service),
) -> None:
    """Delete an item image."""

    # First get the file path before deletion
    result: Result[Any] = await session.execute(
        select(ItemImage.file_path).where(ItemImage.id == str(image_id), ItemImage.item_id == item.id)
    )
    file_path: str | None = result.scalar_one_or_none()

    if not file_path:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")

    # Delete database record and check affected rows
    delete_result = await session.execute(
        delete(ItemImage).where(ItemImage.id == str(image_id), ItemImage.item_id == item.id)
    )

    if delete_result.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")

    await session.commit()

    # Delete file from storage after successful database deletion
    await storage_service.delete_file(file_path)


router.include_router(price_history_router)
router.include_router(images_router)
