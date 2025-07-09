from typing import Annotated
from pydantic import BaseModel, Field


class DealerBase(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=255, description="Dealer name")]
    email: Annotated[str | None, Field(description="Email address")]=None
    phone: Annotated[str | None, Field(description="Phone number")]=None
    address: Annotated[str | None, Field(description="Postal address")]=None
    website: Annotated[str | None, Field(description="Website")]=None
    note: Annotated[str | None, Field(description="Custom note")]=None


class DealerCreate(DealerBase):
    pass


class DealerUpdate(BaseModel):
    name: Annotated[str | None, Field(min_length=1, max_length=255, description="Dealer name")] = None
    email: Annotated[str | None, Field(description="Email address")] = None
    phone: Annotated[str | None, Field(description="Phone number")] = None
    address: Annotated[str | None, Field(description="Postal address")] = None
    website: Annotated[str | None, Field(description="Website")] = None
    note: Annotated[str | None, Field(description="Custom note")] = None


class DealerRead(DealerBase):
    id: int
    user_id: int
