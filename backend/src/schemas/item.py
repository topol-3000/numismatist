from typing import Annotated
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
    pass


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
