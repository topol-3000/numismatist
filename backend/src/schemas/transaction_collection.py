from typing import Annotated

from pydantic import Field

from schemas.base import SchemaConfigMixin
from utils.enums import Currency


class TransactionCollectionBase(SchemaConfigMixin):
    """Base schema for transaction collections."""

    price: Annotated[int, Field(ge=0, description="Collection price in this transaction (pennies/cents)")]
    currency: Annotated[Currency, Field(description="Currency of the collection price")]


class TransactionCollectionCreate(TransactionCollectionBase):
    """Schema for creating a new transaction collection."""

    collection_id: Annotated[str, Field(description="ID of the collection")]
    parent_transaction_collection_id: Annotated[
        int | None, Field(description="ID of the parent transaction collection")
    ] = None


class TransactionCollectionUpdate(SchemaConfigMixin):
    """Schema for updating a transaction collection."""

    price: Annotated[int | None, Field(ge=0, description="Collection price in this transaction (pennies/cents)")] = None
    currency: Annotated[Currency | None, Field(description="Currency of the collection price")] = None


class TransactionCollectionRead(TransactionCollectionBase):
    """Schema for reading transaction collection data."""

    id: int
    transaction_id: Annotated[str, Field(description="ID of the transaction")]
    collection_id: Annotated[str, Field(description="ID of the collection")]
    parent_transaction_collection_id: Annotated[
        int | None, Field(description="ID of the parent transaction collection")
    ] = None
