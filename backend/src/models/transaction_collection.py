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


class TransactionCollection(Base, IdIntPkMixin):
    """Represents a collection involved in a transaction with its price."""

    __tablename__ = "transaction_collections"

    transaction_id: Mapped[str] = mapped_column(
        ForeignKey("transactions.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    collection_id: Mapped[str] = mapped_column(
        ForeignKey("collections.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    price: Mapped[int] = mapped_column(BigInteger, nullable=False)
    currency: Mapped[Currency] = mapped_column(nullable=False)

    # Relationships
    transaction: Mapped["Transaction"] = relationship(
        back_populates="transaction_collections"
    )
    collection: Mapped["Collection"] = relationship()
