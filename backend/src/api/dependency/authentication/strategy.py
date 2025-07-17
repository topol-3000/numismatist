from typing import Annotated

from fastapi import Depends
from fastapi_users.authentication.strategy import AccessTokenDatabase
from fastapi_users.authentication.strategy.db import DatabaseStrategy

from api.dependency.database import SessionDependency
from models import AccessToken
from settings import settings


async def get_access_tokens_db(session: SessionDependency):
    yield AccessToken.get_db(session=session)


def get_database_strategy(
    access_tokens_db: Annotated[AccessTokenDatabase[AccessToken], Depends(get_access_tokens_db)],
) -> DatabaseStrategy:
    return DatabaseStrategy(
        database=access_tokens_db,
        lifetime_seconds=settings.access_token.lifetime_seconds,
    )
