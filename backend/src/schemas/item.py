from datetime import date
from typing import Annotated

from pydantic import Field

from schemas.base import SchemaConfigMixin
from schemas.item_price_history import ItemPriceHistoryRead
from utils.enums import Material
from utils.types import UserIdType


class ItemBase(SchemaConfigMixin):
    name: Annotated[str, Field(min_length=1, max_length=255, description="Descriptive name")]
    year: Annotated[str, Field(min_length=1, max_length=10, description="Year of issue/mint")]
    description: Annotated[str | None, Field(description="Optional notes by user")] = None
    images: Annotated[str | None, Field(description="JSON string with image paths/urls")] = None
    material: Annotated[Material, Field(description="Metal/alloy material")]
    weight: Annotated[float | None, Field(gt=0, description="Weight in grams")] = None


class ItemCreate(ItemBase):
    purchase_price: Annotated[int, Field(ge=0, description="Purchase price in pennies/cents")]
    purchase_date: Annotated[date | None, Field(description="Date when the item was purchased")] = None


class ItemUpdate(SchemaConfigMixin):
    name: Annotated[str | None, Field(min_length=1, max_length=255, description="Descriptive name")] = None
    year: Annotated[str | None, Field(min_length=1, max_length=10, description="Year of issue/mint")] = None
    description: Annotated[str | None, Field(description="Optional notes by user")] = None
    images: Annotated[str | None, Field(description="JSON string with image paths/urls")] = None
    material: Annotated[Material | None, Field(description="Metal/alloy material")] = None
    weight: Annotated[float | None, Field(gt=0, description="Weight in grams")] = None


class ItemRead(ItemBase):
    id: str
    user_id: UserIdType
    collection_id: Annotated[str | None, Field(description="ID of the collection this item belongs to")] = None


class ItemReadWithPurchasePrice(ItemRead):
    """Extended item schema that includes purchase price and date."""

    purchase_price: Annotated[int, Field(ge=0, description="Purchase price in pennies/cents")]
    purchase_date: Annotated[date, Field(description="Date when the item was purchased")]


class ItemReadWithPriceHistory(ItemRead):
    """Extended item schema that includes complete price history for detailed views."""

    price_history: Annotated[
        list[ItemPriceHistoryRead],
        Field(
            description="Complete price history entries for this item",
            default_factory=list,
        ),
    ]
