from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from utils.enums import CounterpartyRole

from .base import Base
from .mixins.id_int_pk import IdIntPkMixin

if TYPE_CHECKING:
    from .user import User


class Counterparty(Base, IdIntPkMixin):
    __tablename__ = "counterparties"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[CounterpartyRole] = mapped_column(
        Enum(CounterpartyRole, validate_strings=True), nullable=False, default=CounterpartyRole.BOTH
    )
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    website: Mapped[str | None] = mapped_column(String(255), nullable=True)
    note: Mapped[str | None] = mapped_column(String(255), nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    user: Mapped["User"] = relationship("User", lazy="select")
