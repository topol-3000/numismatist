from datetime import datetime as dt
from typing import Annotated
from pydantic import Field

from schemas.base import SchemaConfigMixin
from utils.enums import PriceType


class ItemPriceHistoryBase(SchemaConfigMixin):
    """Base schema for item price history entries."""
    price: Annotated[int, Field(ge=0, description="Price in pennies/cents")]
    datetime: Annotated[dt, Field(description="When this price was recorded")]
    type: Annotated[PriceType, Field(description="Type of price entry")]


class ItemPriceHistoryCreate(SchemaConfigMixin):
    """Schema for creating a new price history entry."""
    price: Annotated[int, Field(ge=0, description="Price in pennies/cents")]
    datetime: Annotated[dt | None, Field(description="When this price was recorded")] = None


class ItemPriceHistoryRead(ItemPriceHistoryBase):
    """Schema for reading price history entries."""
    id: int
    item_id: str


class ItemPriceHistoryUpdate(SchemaConfigMixin):
    """Schema for updating price history entries."""
    price: Annotated[int | None, Field(ge=0, description="Price in pennies/cents")] = None
    datetime: Annotated[dt | None, Field(description="When this price was recorded")] = None
