from pydantic import BaseModel, Field
from typing import Optional, Annotated
from schemas.base import SchemaConfigMixin


class DealerBase(SchemaConfigMixin):
    """
    Base schema for Dealer.

    Attributes:
        name (str): Dealer name (category, seller, shop, etc.).
        contact_info (Optional[str]): Contact information for the dealer.
    """
    name: Annotated[str, Field(min_length=1, max_length=255, description="Dealer name (category, seller, shop, etc.)")]
    contact_info: Optional[str] = Field(None, max_length=255)


class DealerCreate(DealerBase):
    """
    Schema for creating a Dealer.
    Inherits all fields from DealerBase.
    """
    pass


class DealerUpdate(SchemaConfigMixin):
    """
    Schema for updating a Dealer.

    Attributes:
        name (Optional[str]): Dealer name.
        contact_info (Optional[str]): Contact information for the dealer.
    """
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    contact_info: Optional[str] = Field(None, max_length=255)


class DealerRead(DealerBase):
    """
    Schema for reading a Dealer.

    Attributes:
        id (int): Dealer ID.
        user_id (int): User (owner) ID of the dealer.
    """
    id: int
    user_id: int
