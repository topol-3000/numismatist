from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from logging import Logger

from sqlalchemy.exc import DBAPIError, SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from settings import DatabaseSettings, settings
from utils import exceptions
from utils.enums import ErrorCode
from utils.logger import get_logger

logger: Logger = get_logger(__name__)


class Database:
    def __init__(self, settings: DatabaseSettings) -> None:
        self.__engine: AsyncEngine = create_async_engine(
            url=settings.dsn,
            pool_size=settings.pool_size,
            max_overflow=settings.max_overflow,
        )
        self.__session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker[AsyncSession](
            bind=self.__engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
            class_=AsyncSession,
        )

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Provide an asynchronous context manager for an SQLAlchemy session.

        This method yields a SQLAlchemy `AsyncSession` object that can be used for
        performing database operations. In the event of an exception, it rolls back
        the session, logs the error, and raises a custom `DatabaseError` exception.
        Once the context manager exits, the session is safely closed.

        Yields:
            AsyncSession: An SQLAlchemy asynchronous session for database
                interaction.

        Raises:
            DatabaseError: Raised when database query execution fails due to an
                unhandled SQLAlchemy or DBAPI-related error.

        """
        session = self.__session_factory()
        try:
            yield session
        except (SQLAlchemyError, DBAPIError) as error:
            await session.rollback()
            logger.exception("Failed to execute a database query")
            raise exceptions.DatabaseError(
                message=f"Failed to execute a database query. Cause: {error}",
                code=ErrorCode.UNHANDLED_DATABASE_ERROR,
            ) from error
        finally:
            await session.close()

    async def close(self) -> None:
        """
        Asynchronously release all resources associated with the database engine,
        such as connection pools.
        """
        await self.__engine.dispose()


database = Database(settings.database)
