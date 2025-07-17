from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import database


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with database.get_session() as session:
        yield session


SessionDependency = Annotated[AsyncSession, Depends(get_session)]
