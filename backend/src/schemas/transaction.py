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


class TransactionCreate(BaseModel):
    """
    Schema for creating a Transaction.

    Attributes:
        dealer_id (Optional[int]): Dealer ID (optional, if not present, dealer_data must be provided).
        dealer_data (Optional[dict]): Dealer data for creation if dealer_id is not provided. Should contain at least 'name' and optionally 'contact_info'.
        date (date): Date of the transaction.
        total_amount (Optional[float]): Total amount for the transaction.
        items (List[TransactionItemCreate]): List of items in the transaction.
    """
    dealer_id: Optional[int] = Field(None, description="Dealer ID (optional, if not present, dealer_data must be provided)")
    dealer_data: Optional[dict] = Field(None, description="Dealer data for creation if dealer_id is not provided. Should contain at least 'name' and optionally 'contact_info'.")
    date: date
    total_amount: Optional[float] = None
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
