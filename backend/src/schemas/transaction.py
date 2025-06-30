from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date
from .item import ItemRead


class TransactionBase(BaseModel):
    dealer_id: int
    date: date
    total_amount: Optional[float] = None


class TransactionCreate(TransactionBase):
    pass


class TransactionRead(TransactionBase):
    id: int
    user_id: int
