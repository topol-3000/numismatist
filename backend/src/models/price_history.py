from datetime import datetime, timezone
from sqlalchemy import ForeignKey, Numeric, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from utils.enums import PriceType
from .base import Base
from .mixins.uuid_pk import UuidPkMixin


class PriceHistory(Base, UuidPkMixin):
    __tablename__ = 'price_history'

    item_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('items.id'), nullable=False)
    price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    price_type: Mapped[PriceType] = mapped_column(Enum(PriceType), nullable=False)
    note: Mapped[str | None] = mapped_column(nullable=True)

    item = relationship('Item', back_populates='price_history')