from typing import TYPE_CHECKING

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable, SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship, Mapped

from utils.types import UserIdType

from .base import Base
from .mixins.id_int_pk import IdIntPkMixin

if TYPE_CHECKING:
    from .item import Item
    from .collection import Collection


class User(Base, IdIntPkMixin, SQLAlchemyBaseUserTable[UserIdType]):
    __tablename__ = 'users'
    
    # Relationships
    items: Mapped[list['Item']] = relationship('Item', back_populates='user', lazy='select')
    collections: Mapped[list['Collection']] = relationship('Collection', back_populates='user', lazy='select')

    @classmethod
    def get_db(cls, session: AsyncSession):
        return SQLAlchemyUserDatabase(session, cls)
