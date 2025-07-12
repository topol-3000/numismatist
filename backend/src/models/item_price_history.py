from datetime import datetime as dt
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.mixins.id_int_pk import IdIntPkMixin
from utils.enums import PriceType

from .base import Base

if TYPE_CHECKING:
    from .item import Item


class ItemPriceHistory(Base, IdIntPkMixin):
    """
    Track price history for items including purchase, sale, and current market prices.
    
    Stores prices as integers (pennies/cents) to avoid floating point precision issues.
    """
    __tablename__ = 'item_price_history'

    price: Mapped[int] = mapped_column(BigInteger, nullable=False, comment="Price in pennies/cents")
    datetime: Mapped[dt] = mapped_column(DateTime(timezone=True), nullable=False, default=dt.now)
    type: Mapped[PriceType] = mapped_column(nullable=False, index=True)

    # Foreign keys
    item_id: Mapped[str] = mapped_column(ForeignKey('items.id'), nullable=False, index=True)

    # Relationships
    item: Mapped['Item'] = relationship('Item', back_populates='price_history')
