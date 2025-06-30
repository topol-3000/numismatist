from typing import TYPE_CHECKING
from sqlalchemy import Column, Integer, ForeignKey, Date, Float
from sqlalchemy.orm import relationship
from .base import Base


if TYPE_CHECKING:
    from .dealer import Dealer
    from .user import User
    from .item import Item


class Transaction(Base):
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True)
    dealer_id = Column(Integer, ForeignKey('dealers.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    date = Column(Date, nullable=False)
    total_amount = Column(Float, nullable=True)
    dealer = relationship('Dealer', back_populates='transactions')
    user = relationship('User')
    items = relationship('Item', back_populates='transaction')
