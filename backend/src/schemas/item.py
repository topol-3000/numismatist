from typing import Annotated, Optional
from pydantic import Field

from schemas.base import SchemaConfigMixin
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
    price: Annotated[float | None, Field(None, description="Price for this item (optional, triggers transaction logic)")]
    dealer_id: Annotated[int | None, Field(None, description="Existing dealer ID (optional, triggers transaction logic)")]
    dealer_data: Annotated[dict | None, Field(None, description="New dealer data (optional, triggers dealer creation)")]
    transaction_id: Annotated[int | None, Field(None, description="Existing transaction ID (optional, to link item)")]


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
