from typing import Optional, TYPE_CHECKING

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
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    images: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON string with image paths/urls
    material: Mapped[Material] = mapped_column(nullable=False)
    weight: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Foreign key to user
    user_id: Mapped[UserIdType] = mapped_column(ForeignKey('users.id'), nullable=False)
    
    # Relationships
    user: Mapped['User'] = relationship('User', back_populates='items')
    collections: Mapped[list['Collection']] = relationship(
        'Collection', 
        secondary='collection_items', 
        back_populates='items',
        lazy='select'
    )
