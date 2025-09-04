from datetime import datetime
from typing import Annotated

from pydantic import Field

from schemas.base import SchemaConfigMixin
from utils.enums import Currency, TransactionStatus, TransactionType
from utils.types import UserIdType


class TransactionBase(SchemaConfigMixin):
    """Base schema for transactions."""

    transaction_type: Annotated[TransactionType, Field(description="Type of transaction")]
    total_amount: Annotated[int, Field(ge=0, description="Total amount in pennies/cents")]
    currency: Annotated[Currency, Field(description="Currency of the transaction")]
    notes: Annotated[str | None, Field(description="Optional notes about the transaction")] = None


class TransactionCreate(TransactionBase):
    """Schema for creating a new transaction."""

    counterparty_id: Annotated[int, Field(description="ID of the counterparty")]
    collection_id: Annotated[str | None, Field(description="ID of the collection (if applicable)")] = None
    transaction_date: Annotated[datetime | None, Field(description="Date and time of transaction")] = None


class TransactionUpdate(SchemaConfigMixin):
    """Schema for updating a transaction."""

    status: Annotated[TransactionStatus | None, Field(description="Status of the transaction")] = None
    total_amount: Annotated[int | None, Field(ge=0, description="Total amount in pennies/cents")] = None
    currency: Annotated[Currency | None, Field(description="Currency of the transaction")] = None
    notes: Annotated[str | None, Field(description="Optional notes about the transaction")] = None
    transaction_date: Annotated[datetime | None, Field(description="Date and time of transaction")] = None


class TransactionRead(TransactionBase):
    """Schema for reading transaction data."""

    id: str
    status: Annotated[TransactionStatus, Field(description="Status of the transaction")]
    transaction_date: Annotated[datetime, Field(description="Date and time of transaction")]
    user_id: UserIdType
    counterparty_id: Annotated[int, Field(description="ID of the counterparty")]
    collection_id: Annotated[str | None, Field(description="ID of the collection (if applicable)")] = None
