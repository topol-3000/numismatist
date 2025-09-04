from datetime import date as dt_date
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Date, Enum, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.mixins.id_int_pk import IdIntPkMixin
from utils.enums import Currency, PriceType

from .base import Base

if TYPE_CHECKING:
    from .item import Item
    from .transaction_item import TransactionItem


class ItemPriceHistory(Base, IdIntPkMixin):
    """
    Track price history for items including purchase, sale, and current market prices.

    Stores prices as integers (pennies/cents) to avoid floating point precision issues.
    Can be linked to specific transactions when the price change is from a transaction.
    """

    __tablename__ = "item_price_history"

    price: Mapped[int] = mapped_column(BigInteger, comment="Price in pennies/cents")
    date: Mapped[dt_date] = mapped_column(Date, server_default=func.current_date())
    type: Mapped[PriceType] = mapped_column(Enum(PriceType, validate_strings=True), index=True)
    currency: Mapped[Currency] = mapped_column(
        Enum(Currency, validate_strings=True), default=Currency.USD, server_default="USD"
    )

    # Foreign keys
    item_id: Mapped[str] = mapped_column(ForeignKey("items.id"), index=True)
    transaction_item_id: Mapped[int | None] = mapped_column(
        ForeignKey("transaction_items.id"), nullable=True, index=True
    )

    # Relationships
    item: Mapped["Item"] = relationship("Item", back_populates="price_history")
    transaction_item: Mapped["TransactionItem | None"] = relationship("TransactionItem", back_populates="price_history")
