from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from utils.types import UserIdType

from .base import Base
from .mixins.uuid_pk import UuidPkMixin

if TYPE_CHECKING:
    from .item import Item
    from .user import User


class Collection(Base, UuidPkMixin):
    """User collection of numismatic items with hierarchical support."""

    __tablename__ = "collections"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    share_token: Mapped[str | None] = mapped_column(String(255), unique=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Foreign keys
    user_id: Mapped[UserIdType] = mapped_column(ForeignKey("users.id"), nullable=False)
    parent_id: Mapped[str | None] = mapped_column(
        ForeignKey("collections.id", ondelete="CASCADE"), nullable=True, index=True
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="collections")
    items: Mapped[list["Item"]] = relationship("Item", back_populates="collection", lazy="select")

    # Hierarchical relationships
    parent: Mapped["Collection | None"] = relationship(
        "Collection", remote_side="Collection.id", back_populates="children"
    )
    children: Mapped[list["Collection"]] = relationship(
        "Collection", back_populates="parent", cascade="all, delete-orphan"
    )

    @property
    def is_leaf(self) -> bool:
        """Check if this collection is a leaf (has no children)."""
        return len(self.children) == 0

    @property
    def is_root(self) -> bool:
        """Check if this collection is a root (has no parent)."""
        return self.parent_id is None

    def get_direct_items_count(self) -> int:
        """Get count of direct items in this collection (no descendants)."""
        return len(self.items)

    def get_all_descendant_items(self) -> list["Item"]:
        """Get all items from this collection and all its descendants."""
        all_items = list(self.items)
        for child in self.children:
            all_items.extend(child.get_all_descendant_items())

        return all_items

    def get_total_items_count(self) -> int:
        """Get total count of items in this collection and all its descendants."""
        return len(self.get_all_descendant_items())

    def get_path_to_root(self) -> list["Collection"]:
        """Get the path from this collection to the root collection."""
        path = [self]
        current = self.parent
        while current:
            path.insert(0, current)
            current = current.parent

        return path

    def validate_no_cycles(self, new_parent_id: str | None) -> bool:
        """Validate that setting new_parent_id would not create a cycle."""
        if new_parent_id is None:
            return True

        if new_parent_id == self.id:
            return False

        def check_descendants(collection_id: str) -> bool:
            for child in self.children:
                if child.id == collection_id:
                    return True
                if check_descendants(collection_id):
                    return True
            return False

        return not check_descendants(new_parent_id)
