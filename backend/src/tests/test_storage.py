"""Tests for storage services."""

from tempfile import TemporaryDirectory
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from fastapi import UploadFile
from botocore.exceptions import ClientError

from services.storage import S3StorageService, LocalStorageService, get_storage_service
from settings import StorageBackend


class TestStorageBackend:
    """Test StorageBackend enum."""
    
    def test_storage_backend_values(self):
        """Test that StorageBackend enum has correct values."""
        assert StorageBackend.S3.value == "s3"
        assert StorageBackend.LOCAL.value == "local"
        assert len(StorageBackend) == 2
    
    def test_storage_backend_string_comparison(self):
        """Test that StorageBackend can be compared with strings."""
        assert StorageBackend.S3 == "s3"
        assert StorageBackend.LOCAL == "local"


class TestStorageFactory:
    """Test storage service factory."""
    
    @patch('services.storage.settings')
    def test_get_storage_service_s3(self, mock_settings):
        """Test factory returns S3StorageService for S3 backend."""
        mock_settings.storage.backend = StorageBackend.S3
        mock_settings.storage.endpoint_url = "http://localhost:9099"
        mock_settings.storage.access_key = "test"
        mock_settings.storage.secret_key = "test"
        mock_settings.storage.bucket_name = "test"
        mock_settings.storage.region = "us-east-1"
        
        with patch('services.storage.boto3'):
            service = get_storage_service()
            assert isinstance(service, S3StorageService)
    
    @patch('services.storage.settings')
    def test_get_storage_service_local(self, mock_settings):
        """Test factory returns LocalStorageService for local backend."""
        mock_settings.storage.backend = StorageBackend.LOCAL
        mock_settings.storage.local_path = "uploads"
        
        service = get_storage_service()
        assert isinstance(service, LocalStorageService)
    
    @patch('services.storage.settings')
    def test_get_storage_service_invalid_backend(self, mock_settings):
        """Test factory raises error for invalid backend."""
        mock_settings.storage.backend = "invalid"
        
        with pytest.raises(ValueError, match="Unknown storage backend"):
            get_storage_service()


class TestS3StorageService:
    """Test S3 storage service."""
    
    @pytest.fixture
    def mock_s3_client(self):
        """Mock S3 client."""
        with patch('services.storage.boto3') as mock_boto3:
            mock_client = MagicMock()
            mock_boto3.client.return_value = mock_client
            yield mock_client

    @pytest.fixture
    def s3_service(self, mock_s3_client):
        """Create S3 storage service with mocked client."""
        with patch('services.storage.settings') as mock_settings:
            mock_settings.storage.endpoint_url = "http://localhost:9099"
            mock_settings.storage.access_key = "test"
            mock_settings.storage.secret_key = "test"
            mock_settings.storage.bucket_name = "test-bucket"
            mock_settings.storage.region = "us-east-1"
            mock_settings.storage.public_url = "http://localhost:9099/test-bucket"
            
            return S3StorageService()
    
    @pytest.mark.asyncio
    async def test_upload_file_success(self, s3_service, mock_s3_client):
        """Test successful file upload to S3."""
        # Mock file
        file_content = b"test file content"
        mock_file = AsyncMock(spec=UploadFile)
        mock_file.filename = "test.jpg"
        mock_file.content_type = "image/jpeg"
        mock_file.read.return_value = file_content
        
        # Mock S3 client
        mock_s3_client.put_object.return_value = None
        
        # Test upload
        file_path, file_size = await s3_service.upload_file(mock_file, "items")
        
        # Assertions
        assert file_path.startswith("items/")
        assert file_path.endswith(".jpg")
        assert file_size == len(file_content)
        mock_s3_client.put_object.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_upload_file_client_error(self, s3_service, mock_s3_client):
        """Test file upload with S3 client error."""
        # Mock file
        mock_file = AsyncMock(spec=UploadFile)
        mock_file.filename = "test.jpg"
        mock_file.read.return_value = b"test"
        
        # Mock S3 client error
        mock_s3_client.put_object.side_effect = ClientError(
            {"Error": {"Code": "AccessDenied"}}, "PutObject"
        )
        
        # Test upload fails
        with pytest.raises(Exception):  # Should raise HTTPException
            await s3_service.upload_file(mock_file, "items")
    
    @pytest.mark.asyncio
    async def test_delete_file_success(self, s3_service, mock_s3_client):
        """Test successful file deletion from S3."""
        mock_s3_client.delete_object.return_value = None
        
        await s3_service.delete_file("items/test.jpg")
        
        mock_s3_client.delete_object.assert_called_once_with(
            Bucket="test-bucket", Key="items/test.jpg"
        )
    
    @pytest.mark.asyncio
    async def test_delete_file_client_error(self, s3_service, mock_s3_client):
        """Test file deletion with S3 client error (should not raise)."""
        mock_s3_client.delete_object.side_effect = ClientError(
            {"Error": {"Code": "NoSuchKey"}}, "DeleteObject"
        )
        
        # Should not raise exception
        await s3_service.delete_file("items/test.jpg")
    
    def test_get_file_url_with_public_url(self, mock_s3_client):
        """Test URL generation with public URL."""
        with patch('services.storage.settings') as mock_settings:
            mock_settings.storage.endpoint_url = "http://localhost:9099"
            mock_settings.storage.access_key = "test"
            mock_settings.storage.secret_key = "test"
            mock_settings.storage.bucket_name = "test-bucket"
            mock_settings.storage.region = "us-east-1"
            mock_settings.storage.public_url = "http://localhost:9099/test-bucket"
            
            service = S3StorageService()
            url = service.get_file_url("items/test.jpg")
            assert url == "http://localhost:9099/test-bucket/items/test.jpg"
    
    def test_get_file_url_with_presigned_url(self, s3_service, mock_s3_client):
        """Test URL generation with presigned URL."""
        with patch('services.storage.settings') as mock_settings:
            mock_settings.storage.public_url = None
            mock_settings.storage.bucket_name = "test-bucket"
            
            mock_s3_client.generate_presigned_url.return_value = "https://presigned-url.com"
            
            service = S3StorageService()
            url = service.get_file_url("items/test.jpg")
            
            assert url == "https://presigned-url.com"
            mock_s3_client.generate_presigned_url.assert_called_once()


class TestLocalStorageService:
    """Test local storage service."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing."""
        with TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)
    
    @pytest.fixture
    def local_service(self, temp_dir):
        """Create local storage service with temporary directory."""
        with patch('services.storage.settings') as mock_settings:
            mock_settings.storage.local_path = str(temp_dir)
            mock_settings.storage.public_url = "http://localhost:8099"
            
            return LocalStorageService()
    
    @pytest.mark.asyncio
    async def test_upload_file_success(self, local_service, temp_dir):
        """Test successful file upload to local storage."""
        # Mock file
        file_content = b"test file content"
        mock_file = AsyncMock(spec=UploadFile)
        mock_file.filename = "test.jpg"
        mock_file.read.return_value = file_content
        
        # Test upload
        file_path, file_size = await local_service.upload_file(mock_file, "items")
        
        # Assertions
        assert file_path.startswith("items/")
        assert file_path.endswith(".jpg")
        assert file_size == len(file_content)
        
        # Check file exists
        full_path = temp_dir / file_path
        assert full_path.exists()
        assert full_path.read_bytes() == file_content
    
    @pytest.mark.asyncio
    async def test_upload_file_creates_directory(self, local_service, temp_dir):
        """Test that upload creates directory structure."""
        # Mock file
        mock_file = AsyncMock(spec=UploadFile)
        mock_file.filename = "test.jpg"
        mock_file.read.return_value = b"test"
        
        # Test upload to nested folder
        file_path, _ = await local_service.upload_file(mock_file, "items/subfolder")
        
        # Check directory was created
        full_path = temp_dir / file_path
        assert full_path.parent.exists()
        assert full_path.exists()
    
    @pytest.mark.asyncio
    async def test_delete_file_success(self, local_service, temp_dir):
        """Test successful file deletion from local storage."""
        # Create test file
        test_file = temp_dir / "items" / "test.jpg"
        test_file.parent.mkdir(parents=True)
        test_file.write_bytes(b"test content")
        
        # Delete file
        await local_service.delete_file("items/test.jpg")

        # Check file is deleted
        assert not test_file.exists()
    
    @pytest.mark.asyncio
    async def test_delete_file_not_exists(self, local_service):
        """Test deletion of non-existent file (should not raise)."""
        # Should not raise exception
        await local_service.delete_file("items/nonexistent.jpg")

    def test_get_file_url_with_public_url(self, local_service):
        """Test URL generation with public URL."""
        url = local_service.get_file_url("items/test.jpg")
        assert url == "http://localhost:8099/static/items/test.jpg"

    def test_get_file_url_without_public_url(self, temp_dir):
        """Test URL generation without public URL."""
        with patch('services.storage.settings') as mock_settings:
            mock_settings.storage.local_path = str(temp_dir)
            mock_settings.storage.public_url = None
            
            service = LocalStorageService()
            url = service.get_file_url("items/test.jpg")
            
            assert url == "/static/items/test.jpg"
