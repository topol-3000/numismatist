from typing import Optional
from datetime import datetime
from pydantic import Field

from schemas.base import SchemaConfigMixin
from schemas.item import ItemRead
from utils.types import UserIdType


class CollectionBase(SchemaConfigMixin):
    """Base collection schema."""
    name: str = Field(..., min_length=1, max_length=255, description="Collection name")
    description: Optional[str] = Field(None, description="Collection description")


class CollectionCreate(CollectionBase):
    """Schema for creating a new collection."""
    pass


class CollectionUpdate(SchemaConfigMixin):
    """Schema for updating an existing collection."""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Collection name")
    description: Optional[str] = Field(None, description="Collection description")


class CollectionRead(CollectionBase):
    """Schema for reading collection data."""
    id: str
    user_id: UserIdType
    share_token: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class CollectionWithItems(CollectionRead):
    """Schema for collection with its items included."""
    items: list[ItemRead] = Field(default_factory=list, description="Items in the collection")


class CollectionAddItem(SchemaConfigMixin):
    """Schema for adding an item to a collection."""
    item_id: str = Field(..., description="ID of the item to add to collection")


class CollectionRemoveItem(SchemaConfigMixin):
    """Schema for removing an item from a collection."""
    item_id: str = Field(..., description="ID of the item to remove from collection")


class SharedCollectionRead(SchemaConfigMixin):
    """Schema for publicly shared collection view."""
    id: str
    name: str
    description: Optional[str] = None
    items: list[ItemRead] = Field(default_factory=list, description="Items in the collection")
    created_at: datetime
    updated_at: datetime
