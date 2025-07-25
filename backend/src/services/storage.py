"""Storage service for handling file uploads to S3-compatible storage."""

import uuid
from abc import ABC, abstractmethod
from pathlib import Path

import boto3
from botocore.exceptions import ClientError
from fastapi import HTTPException, UploadFile, status

from settings import StorageBackend, settings


class StorageService(ABC):
    """Abstract base class for storage services."""

    @abstractmethod
    async def upload_file(
        self,
        file: UploadFile,
        folder: str,
    ) -> tuple[str, int]:
        """
        Upload a file to storage.

        Args:
            file: The file to upload
            folder: The folder/prefix to store the file under

        Returns:
            Tuple of (file_path, file_size)
        """
        pass

    @abstractmethod
    async def delete_file(self, file_path: str) -> None:
        """Delete a file from storage."""
        pass

    @abstractmethod
    def get_file_url(self, file_path: str) -> str:
        """Get the public URL for a file."""
        pass


class S3StorageService(StorageService):
    """S3-compatible storage service."""

    def __init__(self):
        self.client = boto3.client(
            "s3",
            endpoint_url=settings.storage.endpoint_url,
            aws_access_key_id=settings.storage.access_key,
            aws_secret_access_key=settings.storage.secret_key,
            region_name=settings.storage.region,
        )
        self.bucket_name = settings.storage.bucket_name

    async def upload_file(
        self,
        file: UploadFile,
        folder: str,
    ) -> tuple[str, int]:
        """Upload file to S3-compatible storage."""
        # Generate filename
        file_extension = Path(file.filename or "image").suffix or ".jpg"
        filename = f"{uuid.uuid4()}{file_extension}"

        # Create the full file path
        file_path = f"{folder}/{filename}"

        try:
            # Read file content
            await file.seek(0)  # Reset file pointer
            content = await file.read()
            file_size = len(content)

            # Upload to S3
            self.client.put_object(
                Bucket=self.bucket_name,
                Key=file_path,
                Body=content,
                ContentType=file.content_type or "application/octet-stream",
            )

            return file_path, file_size

        except ClientError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to upload file: {str(e)}"
            ) from e

    async def delete_file(self, file_path: str) -> None:
        """Delete file from S3-compatible storage."""
        try:
            self.client.delete_object(Bucket=self.bucket_name, Key=file_path)
        except ClientError:
            # Log the error but don't fail the request
            # File might already be deleted or not exist
            pass

    def get_file_url(self, file_path: str) -> str:
        """Get public URL for the file."""
        if settings.storage.public_url:
            return f"{settings.storage.public_url.rstrip('/')}/{file_path}"
        else:
            # Generate presigned URL for private buckets
            return self.client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket_name, "Key": file_path},
                ExpiresIn=3600,  # 1 hour
            )


class LocalStorageService(StorageService):
    """Local file storage service."""

    def __init__(self):
        self.base_path = Path(settings.storage.local_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.public_url = (settings.storage.public_url or "").rstrip("/")

    async def upload_file(
        self,
        file: UploadFile,
        folder: str,
    ) -> tuple[str, int]:
        """Upload file to local storage."""
        # Generate filename
        file_extension = Path(file.filename or "image").suffix or ".jpg"
        filename = f"{uuid.uuid4()}{file_extension}"

        # Create the full file path
        file_path = f"{folder}/{filename}"
        full_path = self.base_path / file_path

        # Create directory if it doesn't exist
        full_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            # Read and save file
            await file.seek(0)  # Reset file pointer
            content = await file.read()
            file_size = len(content)

            with open(full_path, "wb") as buffer:
                buffer.write(content)

            return file_path, file_size

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to save file: {str(e)}"
            ) from e

    async def delete_file(self, file_path: str) -> None:
        """Delete file from local storage."""
        full_path = self.base_path / file_path
        if full_path.exists():
            full_path.unlink()

    def get_file_url(self, file_path: str) -> str:
        """Get URL for local file (assumes static file serving)."""
        return f"{self.public_url}/static/{file_path}"


# Storage service factory
def get_storage_service() -> StorageService:
    """Get the appropriate storage service based on settings."""
    if settings.storage.backend == StorageBackend.S3:
        return S3StorageService()
    elif settings.storage.backend == StorageBackend.LOCAL:
        return LocalStorageService()
    else:
        raise ValueError(f"Unknown storage backend: {settings.storage.backend}")
