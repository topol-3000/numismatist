"""TransactionCollection model for many-to-many relationship between transactions and collections."""

from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base
from models.mixins.id_int_pk import IdIntPkMixin
from utils.enums import Currency

if TYPE_CHECKING:
    from .collection import Collection
    from .transaction import Transaction
    from .transaction_item import TransactionItem


class TransactionCollection(Base, IdIntPkMixin):
    """Represents a collection involved in a transaction with its price."""

    __tablename__ = "transaction_collections"

    transaction_id: Mapped[str] = mapped_column(
        ForeignKey("transactions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    collection_id: Mapped[str] = mapped_column(
        ForeignKey("collections.id", ondelete="CASCADE"), nullable=False, index=True
    )
    price: Mapped[int] = mapped_column(BigInteger, nullable=False)
    currency: Mapped[Currency] = mapped_column(nullable=False)

    # Hierarchical relationship for nested collection sales
    parent_transaction_collection_id: Mapped[int | None] = mapped_column(
        ForeignKey("transaction_collections.id", ondelete="CASCADE"), nullable=True, index=True
    )

    # Relationships
    transaction: Mapped["Transaction"] = relationship(back_populates="transaction_collections")
    collection: Mapped["Collection"] = relationship()

    # Hierarchical relationships for nested collection sales
    parent: Mapped["TransactionCollection | None"] = relationship(
        "TransactionCollection", remote_side="TransactionCollection.id", back_populates="children"
    )
    children: Mapped[list["TransactionCollection"]] = relationship(
        "TransactionCollection", back_populates="parent", cascade="all, delete-orphan"
    )

    # Direct relationship to transaction items (for leaf collections)
    transaction_items: Mapped[list["TransactionItem"]] = relationship(
        "TransactionItem", back_populates="transaction_collection", cascade="all, delete-orphan"
    )

    @property
    def is_leaf(self) -> bool:
        """Check if this transaction collection is a leaf (has no children)."""
        return len(self.children) == 0

    @property
    def is_root(self) -> bool:
        """Check if this transaction collection is a root (has no parent)."""
        return self.parent_transaction_collection_id is None

    def get_all_transaction_items(self) -> list["TransactionItem"]:
        """Get all transaction items from this collection and all its descendants."""
        all_items = list(self.transaction_items)
        for child in self.children:
            all_items.extend(child.get_all_transaction_items())
        return all_items

    def get_path_to_root(self) -> list["TransactionCollection"]:
        """Get the path from this transaction collection to the root."""
        path = [self]
        current = self.parent
        while current:
            path.insert(0, current)
            current = current.parent
        return path
