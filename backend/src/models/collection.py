from typing import Optional, TYPE_CHECKING
from datetime import datetime

from sqlalchemy import ForeignKey, Text, String, DateTime, Table, Column, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from utils.types import UserIdType

from .base import Base
from .mixins.uuid_pk import UuidPkMixin

if TYPE_CHECKING:
    from .user import User
    from .item import Item


# Association table for many-to-many relationship between collections and items
collection_items = Table(
    'collection_items',
    Base.metadata,
    Column('collection_id', UUID(as_uuid=False), ForeignKey('collections.id'), primary_key=True),
    Column('item_id', UUID(as_uuid=False), ForeignKey('items.id'), primary_key=True),
)


class Collection(Base, UuidPkMixin):
    """User collection of numismatic items."""
    
    __tablename__ = 'collections'

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    share_token: Mapped[Optional[str]] = mapped_column(String(255), unique=True, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now()
    )
    
    # Foreign key to user
    user_id: Mapped[UserIdType] = mapped_column(ForeignKey('users.id'), nullable=False)
    
    # Relationships
    user: Mapped['User'] = relationship('User', back_populates='collections')
    items: Mapped[list['Item']] = relationship(
        'Item', 
        secondary=collection_items, 
        back_populates='collections',
        lazy='select'
    )
