from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Text, String, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from utils.enums import Material
from utils.types import UserIdType

from .base import Base
from .mixins.uuid_pk import UuidPkMixin

if TYPE_CHECKING:
    from .user import User
    from .collection import Collection


class Item(Base, UuidPkMixin):
    __tablename__ = 'items'

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    year: Mapped[str] = mapped_column(String(10), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    images: Mapped[str | None] = mapped_column(Text)  # JSON string with image paths/urls
    material: Mapped[Material] = mapped_column(nullable=False)
    weight: Mapped[float | None] = mapped_column(Float)
    
    # Foreign key to user
    user_id: Mapped[UserIdType] = mapped_column(ForeignKey('users.id'), nullable=False)
    
    # Foreign key to collection (optional - an item may not be in any collection)
    collection_id: Mapped[str | None] = mapped_column(ForeignKey('collections.id'), nullable=True)
    
    # Relationships
    user: Mapped['User'] = relationship('User', back_populates='items')
    collection: Mapped['Collection | None'] = relationship(
        'Collection', 
        back_populates='items',
        lazy='select'
    )
    price_history = relationship('PriceHistory', back_populates='item', cascade='all, delete-orphan')
