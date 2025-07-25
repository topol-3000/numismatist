from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from utils.enums import ImageType

from .base import Base
from .mixins.uuid_pk import UuidPkMixin

if TYPE_CHECKING:
    from .item import Item


class ItemImage(Base, UuidPkMixin):
    """Model for storing item images with types."""

    __tablename__ = "item_images"

    # Fields
    type: Mapped[ImageType] = mapped_column(
        Enum(ImageType, validate_strings=True), index=True, comment="Type of the image (e.g., front, back)"
    )
    file_path: Mapped[str] = mapped_column(String(512), comment="Storage path (S3 key or local path)")
    file_size: Mapped[int | None] = mapped_column(comment="File size in bytes")
    mime_type: Mapped[str | None] = mapped_column(String(100), comment="MIME type (e.g., image/jpeg)")

    # Foreign keys
    item_id: Mapped[str] = mapped_column(ForeignKey("items.id", ondelete="CASCADE"))

    # Relationships
    item: Mapped["Item"] = relationship("Item", back_populates="images")

    # Constraints - Ensure only one front/back image per item
    __table_args__ = (
        Index(
            "idx_unique_front_back_per_item",
            "item_id",
            "type",
            unique=True,
            postgresql_where="type IN ('front', 'back')",
        ),
    )
