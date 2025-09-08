from typing import Annotated

from pydantic import Field

from schemas.base import SchemaConfigMixin
from utils.enums import Currency


class TransactionItemBase(SchemaConfigMixin):
    """Base schema for transaction items."""

    price: Annotated[int, Field(ge=0, description="Item price in this transaction (pennies/cents)")]
    currency: Annotated[Currency, Field(description="Currency of the item price")]
    notes: Annotated[str | None, Field(description="Optional notes about this item in the transaction")] = None


class TransactionItemCreate(TransactionItemBase):
    """Schema for creating a new transaction item."""

    item_id: Annotated[str, Field(description="ID of the item")]


class TransactionItemUpdate(SchemaConfigMixin):
    """Schema for updating a transaction item."""

    price: Annotated[int | None, Field(ge=0, description="Item price in this transaction (pennies/cents)")] = None
    currency: Annotated[Currency | None, Field(description="Currency of the item price")] = None
    notes: Annotated[str | None, Field(description="Optional notes about this item in the transaction")] = None


class TransactionItemRead(TransactionItemBase):
    """Schema for reading transaction item data."""

    id: int
    transaction_id: Annotated[str, Field(description="ID of the transaction")]
    item_id: Annotated[str, Field(description="ID of the item")]
