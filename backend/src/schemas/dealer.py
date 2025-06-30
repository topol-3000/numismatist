from pydantic import BaseModel, Field
from typing import Optional
from schemas.base import SchemaConfigMixin


class DealerBase(SchemaConfigMixin):
    name: str = Field(..., min_length=1, max_length=255)
    contact_info: Optional[str] = Field(None, max_length=255)


class DealerCreate(DealerBase):
    pass


class DealerUpdate(SchemaConfigMixin):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    contact_info: Optional[str] = Field(None, max_length=255)


class DealerRead(DealerBase):
    id: int
    user_id: int
