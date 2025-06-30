from pydantic import BaseModel, Field
from typing import Optional, List, Annotated
from datetime import date
from .item import ItemRead
from .transaction_item import TransactionItemRead, TransactionItemCreate


class TransactionBase(BaseModel):
    """
    Base schema for Transaction.

    Attributes:
        dealer_id (int): Dealer ID (category, seller, shop, etc.).
        date (date): Date of the transaction.
        total_amount (Optional[float]): Total amount for the transaction.
    """
    dealer_id: Annotated[int, Field(description="Dealer ID (category, seller, shop, etc.)")]
    date: date
    total_amount: Optional[float] = None


class TransactionCreate(TransactionBase):
    """
    Schema for creating a Transaction.

    Attributes:
        items (List[TransactionItemCreate]): List of items in the transaction.
    """
    items: List[TransactionItemCreate]


class TransactionRead(TransactionBase):
    """
    Schema for reading a Transaction.

    Attributes:
        id (int): Transaction ID.
        user_id (int): User (owner) ID of the transaction.
        transaction_items (List[TransactionItemRead]): List of transaction items.
    """
    id: Annotated[int, Field(description="Transaction ID")]
    user_id: Annotated[int, Field(description="User (owner) ID of the transaction")]
    transaction_items: List[TransactionItemRead] = []
