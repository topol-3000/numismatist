from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Date, Float, Enum as SAEnum
from .base import Base
from .mixins.id_int_pk import IdIntPkMixin
from sqlalchemy import ForeignKey
from utils.enums_transaction import TransactionType


if TYPE_CHECKING:
    from .dealer import Dealer
    from .user import User
    from .transaction_item import TransactionItem


class Transaction(Base, IdIntPkMixin):
    """
    SQLAlchemy ORM model for Transaction.

    Attributes:
        dealer_id (int): Foreign key to the dealer.
        user_id (int): Foreign key to the user (owner of the transaction).
        date (Date): Date of the transaction.
        total_amount (Optional[float]): Total amount for the transaction.
        dealer (Dealer): Relationship to the Dealer model.
        user (User): Relationship to the User model.
        transaction_items (List[TransactionItem]): List of transaction items in this transaction.
    """
    __tablename__ = 'transactions'

    dealer_id: Mapped[int] = mapped_column(ForeignKey('dealers.id'), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    date: Mapped['Date'] = mapped_column(Date, nullable=False)
    total_amount: Mapped[float | None] = mapped_column(Float, nullable=True)
    type: Mapped[TransactionType] = mapped_column(SAEnum(TransactionType), nullable=False, default=TransactionType.PURCHASE)

    dealer: Mapped['Dealer'] = relationship('Dealer', back_populates='transactions', lazy='select')
    user: Mapped['User'] = relationship('User', lazy='select')
    transaction_items: Mapped[list['TransactionItem']] = relationship('TransactionItem', back_populates='transaction', lazy='selectin')
