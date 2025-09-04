from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Enum, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from utils.enums import Currency

from .base import Base
from .mixins.id_int_pk import IdIntPkMixin

if TYPE_CHECKING:
    from .item import Item
    from .transaction import Transaction


class TransactionItem(Base, IdIntPkMixin):
    """
    Many-to-many relationship table between transactions and items.

    Stores prices as integers (pennies/cents) to avoid floating point precision issues.
    """

    __tablename__ = "transaction_items"

    price: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="Item price in this transaction (pennies/cents)"
    )
    currency: Mapped[Currency] = mapped_column(
        Enum(Currency, validate_strings=True), nullable=False, default=Currency.USD
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Foreign keys
    transaction_id: Mapped[str] = mapped_column(ForeignKey("transactions.id"), nullable=False, index=True)
    item_id: Mapped[str] = mapped_column(ForeignKey("items.id"), nullable=False, index=True)

    # Relationships
    transaction: Mapped["Transaction"] = relationship("Transaction", lazy="select")
    item: Mapped["Item"] = relationship("Item", lazy="select")
