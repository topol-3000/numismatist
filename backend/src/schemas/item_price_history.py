from datetime import date as dt_date
from typing import Annotated

from pydantic import Field

from schemas.base import SchemaConfigMixin
from utils.enums import Currency, PriceType


class ItemPriceHistoryBase(SchemaConfigMixin):
    """Base schema for item price history entries."""

    price: Annotated[int, Field(ge=0, description="Price in pennies/cents")]
    date: Annotated[dt_date, Field(description="When this price was recorded")]
    type: Annotated[PriceType, Field(description="Type of price entry")]
    currency: Annotated[Currency, Field(description="Currency of the price")]


class ItemPriceHistoryCreate(SchemaConfigMixin):
    """Schema for creating a new price history entry."""

    price: Annotated[int, Field(ge=0, description="Price in pennies/cents")]
    date: Annotated[dt_date | None, Field(description="When this price was recorded")] = None
    currency: Annotated[Currency, Field(description="Currency of the price")] = Currency.USD
    transaction_item_id: Annotated[int | None, Field(description="Related transaction item ID")] = None


class ItemPriceHistoryRead(ItemPriceHistoryBase):
    """Schema for reading price history entries."""

    id: int
    item_id: str
    transaction_item_id: int | None


class ItemPriceHistoryUpdate(SchemaConfigMixin):
    """Schema for updating price history entries."""

    price: Annotated[int | None, Field(ge=0, description="Price in pennies/cents")] = None
    date: Annotated[dt_date | None, Field(description="When this price was recorded")] = None
    currency: Annotated[Currency | None, Field(description="Currency of the price")] = None
    transaction_item_id: Annotated[int | None, Field(description="Related transaction item ID")] = None
