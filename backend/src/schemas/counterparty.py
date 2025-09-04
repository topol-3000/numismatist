from typing import Annotated

from pydantic import BaseModel, Field

from utils.enums import CounterpartyRole


class CounterpartyBase(BaseModel):
    """Base schema for counterparty (person or organization involved in transactions)."""

    name: Annotated[str, Field(min_length=1, max_length=255, description="Counterparty name")]
    role: Annotated[CounterpartyRole, Field(description="Role in transactions (SELLER/BUYER/BOTH)")] = (
        CounterpartyRole.BOTH
    )
    email: Annotated[str | None, Field(description="Email address")] = None
    phone: Annotated[str | None, Field(description="Phone number")] = None
    address: Annotated[str | None, Field(description="Postal address")] = None
    website: Annotated[str | None, Field(description="Website")] = None
    note: Annotated[str | None, Field(description="Custom note")] = None


class CounterpartyCreate(CounterpartyBase):
    """Schema for creating a new counterparty."""

    pass


class CounterpartyUpdate(BaseModel):
    """Schema for updating an existing counterparty."""

    name: Annotated[str | None, Field(min_length=1, max_length=255, description="Counterparty name")] = None
    role: Annotated[CounterpartyRole | None, Field(description="Role in transactions (SELLER/BUYER/BOTH)")] = None
    email: Annotated[str | None, Field(description="Email address")] = None
    phone: Annotated[str | None, Field(description="Phone number")] = None
    address: Annotated[str | None, Field(description="Postal address")] = None
    website: Annotated[str | None, Field(description="Website")] = None
    note: Annotated[str | None, Field(description="Custom note")] = None


class CounterpartyRead(CounterpartyBase):
    """Schema for reading counterparty data with ID and user_id."""

    id: int
    user_id: int
