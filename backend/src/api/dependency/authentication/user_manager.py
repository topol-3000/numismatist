import logging
from typing import Annotated

from fastapi import Depends, Request
from fastapi_users import BaseUserManager, IntegerIDMixin
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase

from models import User
from settings import settings
from utils.types import UserIdType

from .users import get_users_db

log = logging.getLogger(__name__)


class UserManager(IntegerIDMixin, BaseUserManager[User, UserIdType]):
    reset_password_token_secret = settings.access_token.reset_password_token_secret
    verification_token_secret = settings.access_token.verification_token_secret

    async def on_after_register(self, user: User, request: Request | None = None):
        log.warning('User %r has registered.', user.id)

    async def on_after_request_verify(self, user: User, token: str, request: Request | None = None):
        log.warning('Verification requested for user %r. Verification token: %r', user.id, token)

    async def on_after_forgot_password(self, user: User, token: str, request: Request | None = None):
        log.warning('User %r has forgot their password. Reset token: %r', user.id, token)


async def get_user_manager(users_db: Annotated[SQLAlchemyUserDatabase, Depends(get_users_db)]):
    yield UserManager(users_db)
