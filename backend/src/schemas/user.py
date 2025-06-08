from fastapi_users import schemas
from pydantic import BaseModel

from schemas.base import SchemaConfigMixin
from utils.types import UserIdType


class UserRead(SchemaConfigMixin, schemas.BaseUser[UserIdType]):
    pass


class UserCreate(SchemaConfigMixin, schemas.BaseUserCreate):
    pass


class UserUpdate(SchemaConfigMixin, schemas.BaseUserUpdate):
    pass


class UserRegisteredNotification(SchemaConfigMixin, BaseModel):
    user: UserRead
    ts: int
