from datetime import datetime, timezone
from typing import Annotated
from pydantic import BaseModel, Field, ConfigDict, field_serializer
from utils.enums import PriceType


class PriceHistoryBase(BaseModel):
    price: Annotated[float, Field(gt=0, description="Price value")]
    price_type: Annotated[PriceType, Field(description="Type of price (in, out, current)")]
    timestamp: Annotated[datetime | None, Field(description="Timestamp for the price record")] = None
    note: Annotated[str | None, Field(description="Comment or resource for the price (optional)")] = None


class PriceHistoryCreate(PriceHistoryBase):
    pass


class PriceHistoryRead(BaseModel):
    id: str
    item_id: str
    price: float
    price_type: str
    timestamp: datetime
    note: str | None

    model_config = ConfigDict(from_attributes=True)

    @field_serializer('timestamp')
    def serialize_timestamp(self, value: datetime, _info):
        if value is None:
            return None

        # Ensure ISO8601 output with timezone (if no tzinfo, add +00:00)
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)

        return value.isoformat()


class PriceHistoryUpdate(PriceHistoryBase):
    pass
