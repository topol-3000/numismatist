from __future__ import annotations

from datetime import datetime
from typing import Annotated

from pydantic import Field

from schemas.base import SchemaConfigMixin
from schemas.item import ItemRead
from utils.types import UserIdType


class CollectionBase(SchemaConfigMixin):
    """Base collection schema."""

    name: Annotated[str, Field(min_length=1, max_length=255, description="Collection name")]
    description: Annotated[str | None, Field(description="Collection description")] = None


class CollectionCreate(CollectionBase):
    """Schema for creating a new collection."""

    parent_id: Annotated[str | None, Field(description="ID of the parent collection")] = None


class CollectionUpdate(SchemaConfigMixin):
    """Schema for updating an existing collection."""

    name: Annotated[str | None, Field(min_length=1, max_length=255, description="Collection name")] = None
    description: Annotated[str | None, Field(description="Collection description")] = None
    parent_id: Annotated[str | None, Field(description="ID of the parent collection")] = None


class CollectionRead(CollectionBase):
    """Schema for reading collection data."""

    id: str
    user_id: UserIdType
    parent_id: Annotated[str | None, Field(description="ID of the parent collection")] = None
    share_token: str | None = None
    created_at: datetime
    updated_at: datetime


class CollectionWithItems(CollectionRead):
    """Schema for collection with its items included."""

    items: Annotated[
        list[ItemRead],
        Field(default_factory=list, description="Items in the collection"),
    ]


class CollectionDetailed(CollectionRead):
    """Schema for collection with detailed hierarchy information."""

    is_leaf: bool
    is_root: bool
    direct_items_count: int


class CollectionAddItem(SchemaConfigMixin):
    """Schema for adding an item to a collection."""

    item_id: Annotated[str, Field(description="ID of the item to add to collection")]


class CollectionRemoveItem(SchemaConfigMixin):
    """Schema for removing an item from a collection."""

    item_id: Annotated[str, Field(description="ID of the item to remove from collection")]


class SharedCollectionRead(SchemaConfigMixin):
    """Schema for publicly shared collection view."""

    id: str
    name: str
    description: str | None = None
    items: Annotated[
        list[ItemRead],
        Field(default_factory=list, description="Items in the collection"),
    ]
    created_at: datetime
    updated_at: datetime


class CollectionTree(CollectionDetailed):
    """Schema for collection with its children included (tree structure)."""

    children: Annotated[
        list[CollectionTree],
        Field(default_factory=list, description="Child collections"),
    ]


class CollectionPath(SchemaConfigMixin):
    """Schema for collection path from root to current."""

    path: Annotated[
        list[CollectionRead],
        Field(description="Path from root collection to current collection"),
    ]


class CollectionMove(SchemaConfigMixin):
    """Schema for moving collection to new parent."""

    new_parent_id: Annotated[str | None, Field(description="ID of the new parent collection (null for root)")] = None
