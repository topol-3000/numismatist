from typing import TYPE_CHECKING
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base


if TYPE_CHECKING:
    from .user import User
    from .transaction import Transaction


class Dealer(Base):
    __tablename__ = 'dealers'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    contact_info = Column(String(255), nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user = relationship('User', back_populates='dealers')
    transactions = relationship('Transaction', back_populates='dealer')
