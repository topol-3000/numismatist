from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, Enum, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from utils.enums import Currency, TransactionStatus, TransactionType
from utils.types import UserIdType

from .base import Base
from .mixins.uuid_pk import UuidPkMixin

if TYPE_CHECKING:
    from .collection import Collection
    from .counterparty import Counterparty
    from .user import User


class Transaction(Base, UuidPkMixin):
    """
    Track transactions for buying and selling items or collections.

    Stores amounts as integers (pennies/cents) to avoid floating point precision issues.
    """

    __tablename__ = "transactions"

    transaction_type: Mapped[TransactionType] = mapped_column(
        Enum(TransactionType, validate_strings=True), nullable=False, index=True
    )
    status: Mapped[TransactionStatus] = mapped_column(
        Enum(TransactionStatus, validate_strings=True),
        nullable=False,
        default=TransactionStatus.PENDING,
        server_default="PENDING",
        index=True,
    )
    transaction_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    total_amount: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="Total amount in pennies/cents"
    )
    currency: Mapped[Currency] = mapped_column(
        Enum(Currency, validate_strings=True), nullable=False, default=Currency.USD
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Foreign keys
    user_id: Mapped[UserIdType] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    counterparty_id: Mapped[int] = mapped_column(ForeignKey("counterparties.id"), nullable=False, index=True)
    collection_id: Mapped[str | None] = mapped_column(ForeignKey("collections.id"), nullable=True, index=True)

    # Relationships
    user: Mapped["User"] = relationship("User", lazy="select")
    counterparty: Mapped["Counterparty"] = relationship("Counterparty", lazy="select")
    collection: Mapped["Collection | None"] = relationship("Collection", lazy="select")
