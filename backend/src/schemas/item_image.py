from typing import Annotated

from pydantic import Field, computed_field

from schemas.base import SchemaConfigMixin
from utils.enums import ImageType


class ItemImageBase(SchemaConfigMixin):
    """Base schema for item images."""

    type: Annotated[ImageType, Field(description="Type of the image")]
    file_path: Annotated[str, Field(min_length=1, max_length=512, description="Path to the image file")]
    file_size: Annotated[int | None, Field(gt=0, description="File size in bytes")] = None
    mime_type: Annotated[str | None, Field(max_length=100, description="MIME type")] = None


class ItemImageRead(ItemImageBase):
    """Schema for reading an item image."""

    id: str
    item_id: str

    @computed_field
    @property
    def url(self) -> str:
        """Compute the URL for the image file."""
        from services.storage import get_storage_service

        storage_service = get_storage_service()
        return storage_service.get_file_url(self.file_path)
