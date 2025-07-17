from typing import TYPE_CHECKING

from sqlalchemy import Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from utils.enums import Material
from utils.types import UserIdType

from .base import Base
from .mixins.uuid_pk import UuidPkMixin

if TYPE_CHECKING:
    from .collection import Collection
    from .item_price_history import ItemPriceHistory
    from .user import User


class Item(Base, UuidPkMixin):
    __tablename__ = "items"

    name: Mapped[str] = mapped_column(String(255))
    year: Mapped[str] = mapped_column(String(10))
    description: Mapped[str | None] = mapped_column(Text)
    images: Mapped[str | None] = mapped_column(Text)  # JSON string with image paths/urls
    material: Mapped[Material] = mapped_column()
    weight: Mapped[float | None] = mapped_column(Float)

    # Foreign keys
    user_id: Mapped[UserIdType] = mapped_column(ForeignKey("users.id"))
    collection_id: Mapped[str | None] = mapped_column(ForeignKey("collections.id"))

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="items")
    collection: Mapped["Collection | None"] = relationship("Collection", back_populates="items", lazy="select")
    price_history: Mapped[list["ItemPriceHistory"]] = relationship(
        "ItemPriceHistory",
        back_populates="item",
        cascade="all, delete-orphan",
        order_by="ItemPriceHistory.date.desc()",
    )
