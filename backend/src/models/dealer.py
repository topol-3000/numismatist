from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey
from .base import Base
from .mixins.id_int_pk import IdIntPkMixin


if TYPE_CHECKING:
    from .user import User
    from .transaction import Transaction


class Dealer(Base, IdIntPkMixin):
    """
    SQLAlchemy ORM model for Dealer.

    Attributes:
        name (str): Dealer name (category, seller, shop, etc.).
        contact_info (Optional[str]): Contact information for the dealer.
        user_id (int): Foreign key to the user who owns this dealer.
        user (User): Relationship to the User model.
        transactions (List[Transaction]): List of transactions associated with this dealer.
    """
    __tablename__ = 'dealers'

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    contact_info: Mapped[str | None] = mapped_column(String(255), nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)

    user: Mapped['User'] = relationship('User', lazy='select')
    transactions: Mapped[list['Transaction']] = relationship(
        'Transaction', back_populates='dealer', lazy='select'
        )
