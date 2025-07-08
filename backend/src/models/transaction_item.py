from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Float, Integer
from .base import Base
from .mixins.id_int_pk import IdIntPkMixin


if TYPE_CHECKING:
    from .transaction import Transaction
    from .item import Item


class TransactionItem(Base, IdIntPkMixin):
    """
    SQLAlchemy ORM model for TransactionItem.

    Attributes:
        transaction_id (int): Foreign key to the transaction.
        item_id (str): Foreign key to the item.
        price (float): Price for this item in the transaction.
        transaction (Transaction): Relationship to the Transaction model.
        item (Item): Relationship to the Item model.
    """
    __tablename__ = 'transaction_items'
    transaction_id: Mapped[int] = mapped_column(ForeignKey('transactions.id'), nullable=False)
    item_id: Mapped[str] = mapped_column(ForeignKey('items.id'), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)

    transaction: Mapped['Transaction'] = relationship('Transaction', back_populates='transaction_items')
    item: Mapped['Item'] = relationship('Item', back_populates='transaction_items')
