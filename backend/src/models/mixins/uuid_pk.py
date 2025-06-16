from uuid import uuid4
from sqlalchemy import UUID
from sqlalchemy.orm import Mapped, mapped_column


class UuidPkMixin:
    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
