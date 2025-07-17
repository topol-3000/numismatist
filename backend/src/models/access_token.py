from fastapi_users_db_sqlalchemy.access_token import (
    SQLAlchemyAccessTokenDatabase,
    SQLAlchemyBaseAccessTokenTable,
)
from sqlalchemy import ForeignKey, Integer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base
from utils.types import UserIdType


class AccessToken(Base, SQLAlchemyBaseAccessTokenTable[UserIdType]):
    __tablename__ = "access_tokens"

    user_id: Mapped[UserIdType] = mapped_column(Integer, ForeignKey("users.id", ondelete="cascade"), nullable=False)

    @classmethod
    def get_db(cls, session: AsyncSession):
        return SQLAlchemyAccessTokenDatabase(session, cls)
