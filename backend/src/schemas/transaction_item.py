from pydantic import BaseModel, Field
from typing import Annotated

class TransactionItemRead(BaseModel):
    """
    Schema for reading a TransactionItem.

    Attributes:
        id (int): TransactionItem ID.
        transaction_id (int): Transaction ID.
        item_id (str): Item ID.
        price (float): Price for this item in transaction.
        quantity (int): Quantity of this item in transaction.
    """
    id: Annotated[int, Field(description="TransactionItem ID")]
    transaction_id: Annotated[int, Field(description="Transaction ID")]
    item_id: Annotated[str, Field(description="Item ID")]
    price: Annotated[float, Field(description="Price for this item in transaction")]
    quantity: Annotated[int, Field(description="Quantity of this item in transaction")]

class TransactionItemCreate(BaseModel):
    """
    Schema for creating a TransactionItem.

    Attributes:
        item_id (str): Item ID.
        price (float): Price for this item in transaction.
        quantity (int): Quantity of this item in transaction.
    """
    item_id: Annotated[str, Field(description="Item ID")]
    price: Annotated[float, Field(description="Price for this item in transaction")]
    quantity: Annotated[int, Field(description="Quantity of this item in transaction")]
