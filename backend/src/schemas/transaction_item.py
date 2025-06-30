from pydantic import BaseModel, Field
from typing import Annotated, Optional, Union


class TransactionItemRead(BaseModel):
    """
    Schema for reading a TransactionItem.

    Attributes:
        id (int): TransactionItem ID.
        transaction_id (int): Transaction ID.
        item_id (str): Item ID.
        price (float): Price for this item in transaction.
    """
    id: Annotated[int, Field(description="TransactionItem ID")]
    transaction_id: Annotated[int, Field(description="Transaction ID")]
    item_id: Annotated[str, Field(description="Item ID")]
    price: Annotated[float, Field(description="Price for this item in transaction")]


class TransactionItemCreateExisting(BaseModel):
    """
    Schema for creating a TransactionItem for an existing coin.

    Attributes:
        item_id (str): Item ID (existing).
        price (float): Price for this item in transaction.
    """
    item_id: Annotated[str, Field(description="Item ID (existing)")]
    price: Annotated[float, Field(description="Price for this item in transaction")]


class TransactionItemCreateNew(BaseModel):
    """
    Schema for creating a TransactionItem for a new coin.

    Attributes:
        name (str): Descriptive name.
        year (str): Year of issue/mint.
        material (str): Metal/alloy material.
        price (float): Price for this item in transaction.
        description (Optional[str]): Optional notes by user.
        images (Optional[str]): JSON string with image paths/urls.
        weight (Optional[float]): Weight in grams.
    """
    name: Annotated[str, Field(min_length=1, max_length=255, description="Descriptive name")]
    year: Annotated[str, Field(min_length=1, max_length=10, description="Year of issue/mint")]
    material: Annotated[str, Field(description="Metal/alloy material")]
    price: Annotated[float, Field(description="Price for this item in transaction")]
    description: Annotated[Optional[str], Field(description="Optional notes by user")] = None
    images: Annotated[Optional[str], Field(description="JSON string with image paths/urls")] = None
    weight: Annotated[Optional[float], Field(gt=0, description="Weight in grams")] = None

TransactionItemCreate = Union[TransactionItemCreateExisting, TransactionItemCreateNew]
