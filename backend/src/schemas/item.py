from datetime import date
from typing import Annotated

from pydantic import Field, field_validator

from schemas.base import SchemaConfigMixin
from schemas.grading_info import GradingInfoRead
from schemas.item_price_history import ItemPriceHistoryRead
from utils.enums import Material
from utils.types import UserIdType


class ItemBase(SchemaConfigMixin):
    name: Annotated[str, Field(min_length=1, max_length=255, description="Descriptive name")]
    year: Annotated[str, Field(min_length=1, max_length=10, description="Year of issue/mint")]
    description: Annotated[str | None, Field(description="Optional notes by user")] = None
    material: Annotated[Material, Field(description="Metal/alloy material")]
    weight: Annotated[float | None, Field(gt=0, description="Weight in grams")] = None


class ItemCreate(ItemBase):
    purchase_price: Annotated[int, Field(ge=0, description="Purchase price in pennies/cents")]
    purchase_date: Annotated[date | None, Field(description="Date when the item was purchased")] = None

    grading_company_id: Annotated[str, Field(description="ID of the grading company")]
    certificate_number: Annotated[str, Field(min_length=1, max_length=64, description="Certificate number")]
    certificate_url: Annotated[str | None, Field(max_length=255, description="Certificate URL")] = None
    grade: Annotated[str | None, Field(max_length=32, description="Grade value")] = None
    grade_details: Annotated[str | None, Field(max_length=64, description="Grade details")] = None
    grading_note: Annotated[str | None, Field(max_length=255, description="Additional grading note")] = None

    @field_validator("certificate_number")
    @classmethod
    def validate_certificate_number(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Certificate number cannot be empty")

        return v.strip()


class ItemUpdate(SchemaConfigMixin):
    name: Annotated[str | None, Field(min_length=1, max_length=255, description="Descriptive name")] = None
    year: Annotated[str | None, Field(min_length=1, max_length=10, description="Year of issue/mint")] = None
    description: Annotated[str | None, Field(description="Optional notes by user")] = None
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
    grading_info: Annotated[
        GradingInfoRead | None,
        Field(
            description="Grading information for this item",
            default=None,
        ),
    ]
