from typing import Optional
from pydantic import Field

from schemas.base import SchemaConfigMixin
from utils.enums import Material
from utils.types import UserIdType


class ItemBase(SchemaConfigMixin):
    name: str = Field(..., min_length=1, max_length=255, description="Descriptive name")
    year: str = Field(..., min_length=1, max_length=10, description="Year of issue/mint")
    description: Optional[str] = Field(None, description="Optional notes by user")
    images: Optional[str] = Field(None, description="JSON string with image paths/urls")
    material: Material = Field(..., description="Metal/alloy material")
    weight: Optional[float] = Field(None, gt=0, description="Weight in grams")


class ItemCreate(ItemBase):
    pass


class ItemUpdate(SchemaConfigMixin):
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Descriptive name")
    year: Optional[str] = Field(None, min_length=1, max_length=10, description="Year of issue/mint")
    description: Optional[str] = Field(None, description="Optional notes by user")
    images: Optional[str] = Field(None, description="JSON string with image paths/urls")
    material: Optional[Material] = Field(None, description="Metal/alloy material")
    weight: Optional[float] = Field(None, gt=0, description="Weight in grams")


class ItemRead(ItemBase):
    id: str
    user_id: UserIdType
