"""Tests for item images functionality."""
import io
from typing import Any
from unittest.mock import AsyncMock, patch
from fastapi import status
from fastapi.testclient import TestClient
from httpx import Response

from models.user import User
from models.item import Item
from services.storage import StorageService
from utils.enums import ImageType


class TestItemImages:
    """Test item images functionality."""

    def test_get_empty_images_list(self, authenticated_client: TestClient, test_user: User, test_item: Item):
        """
        Flow: GET /api/items/{item_id}/images for new item with no images
        Expected: 200 OK with empty array []
        """
        response: Response = authenticated_client.get(f"/api/items/{test_item.id}/images")
        
        assert response.status_code == status.HTTP_200_OK
        images: list[dict[str, Any]] = response.json()
        assert images == []

    @patch('api.routes.items.get_storage_service')
    def test_upload_front_image(self, mock_get_storage, authenticated_client: TestClient, test_user: User, test_item: Item):
        """
        Flow: POST /api/items/{item_id}/images with front image
        Expected: 201 Created with image metadata
        """
        # Mock the storage service
        mock_storage_service = AsyncMock(spec=StorageService)
        mock_storage_service.upload_file.return_value = ("test/path/image.jpg", 1024)
        mock_get_storage.return_value = mock_storage_service
        
        # Create image file
        image_data = b"fake_image_data"
        
        response: Response = authenticated_client.post(
            f"/api/items/{test_item.id}/images",
            files={"file": ("test.jpg", io.BytesIO(image_data), "image/jpeg")},
            data={"file_type": ImageType.FRONT}
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        image_response: dict[str, Any] = response.json()
        assert image_response["type"] == ImageType.FRONT
        assert image_response["item_id"] == str(test_item.id)
        assert "id" in image_response

    @patch('api.routes.items.get_storage_service')
    def test_upload_back_image(self, mock_get_storage, authenticated_client: TestClient, test_user: User, test_item: Item):
        """
        Flow: POST /api/items/{item_id}/images with back image
        Expected: 201 Created with image metadata
        """
        # Mock the storage service
        mock_storage_service = AsyncMock(spec=StorageService)
        mock_storage_service.upload_file.return_value = ("test/path/back.jpg", 1024)
        mock_get_storage.return_value = mock_storage_service
        
        # Create image file
        image_data = b"fake_image_data"
        
        response: Response = authenticated_client.post(
            f"/api/items/{test_item.id}/images",
            files={"file": ("back.jpg", io.BytesIO(image_data), "image/jpeg")},
            data={"file_type": ImageType.BACK}
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        image_response: dict[str, Any] = response.json()
        assert image_response["type"] == ImageType.BACK
        assert image_response["item_id"] == str(test_item.id)

    @patch('api.routes.items.get_storage_service')
    def test_upload_additional_image(self, mock_get_storage, authenticated_client: TestClient, test_user: User, test_item: Item):
        """
        Flow: POST /api/items/{item_id}/images with additional image
        Expected: 201 Created with image metadata
        """
        # Mock the storage service
        mock_storage_service = AsyncMock(spec=StorageService)
        mock_storage_service.upload_file.return_value = ("test/path/additional.jpg", 1024)
        mock_get_storage.return_value = mock_storage_service
        
        # Create image file
        image_data = b"fake_image_data"
        
        response: Response = authenticated_client.post(
            f"/api/items/{test_item.id}/images",
            files={"file": ("additional.jpg", io.BytesIO(image_data), "image/jpeg")},
            data={"file_type": ImageType.ADDITIONAL}
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        image_response: dict[str, Any] = response.json()
        assert image_response["type"] == ImageType.ADDITIONAL
        assert image_response["item_id"] == str(test_item.id)

    @patch('api.routes.items.get_storage_service')
    def test_upload_duplicate_front_image_rejected(self, mock_get_storage, authenticated_client: TestClient, test_user: User, test_item: Item):
        """
        Flow: Upload front image, then try to upload another front image
        Expected: First succeeds, second returns 409 Conflict
        """
        # Mock the storage service
        mock_storage_service = AsyncMock(spec=StorageService)
        mock_storage_service.upload_file.return_value = ("test/path/front.jpg", 1024)
        mock_get_storage.return_value = mock_storage_service
        
        # Upload first front image
        image_data1 = b"fake_image_data_1"
        response1: Response = authenticated_client.post(
            f"/api/items/{test_item.id}/images",
            files={"file": ("front1.jpg", io.BytesIO(image_data1), "image/jpeg")},
            data={"file_type": ImageType.FRONT}
        )
        
        assert response1.status_code == status.HTTP_201_CREATED
        
        # Try to upload second front image
        image_data2 = b"fake_image_data_2"
        response2: Response = authenticated_client.post(
            f"/api/items/{test_item.id}/images",
            files={"file": ("front2.jpg", io.BytesIO(image_data2), "image/jpeg")},
            data={"file_type": ImageType.FRONT}
        )
        
        assert response2.status_code == status.HTTP_409_CONFLICT
        error_detail: dict[str, Any] = response2.json()
        assert "already exists" in error_detail["detail"]
        assert "delete the existing image first" in error_detail["detail"]

    @patch('api.routes.items.get_storage_service')
    def test_upload_duplicate_back_image_rejected(self, mock_get_storage, authenticated_client: TestClient, test_user: User, test_item: Item):
        """
        Flow: Upload back image, then try to upload another back image
        Expected: First succeeds, second returns 409 Conflict
        """
        # Mock the storage service
        mock_storage_service = AsyncMock(spec=StorageService)
        mock_storage_service.upload_file.return_value = ("test/path/back.jpg", 1024)
        mock_get_storage.return_value = mock_storage_service
        
        # Upload first back image
        image_data1 = b"fake_image_data_1"
        response1: Response = authenticated_client.post(
            f"/api/items/{test_item.id}/images",
            files={"file": ("back1.jpg", io.BytesIO(image_data1), "image/jpeg")},
            data={"file_type": ImageType.BACK}
        )
        
        assert response1.status_code == status.HTTP_201_CREATED
        
        # Try to upload second back image
        image_data2 = b"fake_image_data_2"
        response2: Response = authenticated_client.post(
            f"/api/items/{test_item.id}/images",
            files={"file": ("back2.jpg", io.BytesIO(image_data2), "image/jpeg")},
            data={"file_type": ImageType.BACK}
        )
        
        assert response2.status_code == status.HTTP_409_CONFLICT
        error_detail: dict[str, Any] = response2.json()
        assert "already exists" in error_detail["detail"]

    def test_upload_non_image_file_rejected(self, authenticated_client: TestClient, test_user: User, test_item: Item):
        """
        Flow: POST /api/items/{item_id}/images with non-image file
        Expected: 400 Bad Request with error about file type
        """
        # Create a text file instead of image
        text_data = b"This is not an image file"
        
        response: Response = authenticated_client.post(
            f"/api/items/{test_item.id}/images",
            files={"file": ("document.txt", io.BytesIO(text_data), "text/plain")},
            data={"file_type": ImageType.FRONT}
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        error_detail: dict[str, Any] = response.json()
        assert "File must be an image" in error_detail["detail"]

    @patch('api.routes.items.get_storage_service')
    def test_get_images_list_with_images(self, mock_get_storage, authenticated_client: TestClient, test_user: User, test_item: Item):
        """
        Flow: Upload images, then GET /api/items/{item_id}/images
        Expected: 200 OK with array of uploaded images
        """
        # Mock the storage service
        mock_storage_service = AsyncMock(spec=StorageService)
        mock_storage_service.upload_file.return_value = ("test/path/image.jpg", 1024)
        mock_get_storage.return_value = mock_storage_service
        
        # Upload front image
        image_data1 = b"fake_image_data_1"
        response1: Response = authenticated_client.post(
            f"/api/items/{test_item.id}/images",
            files={"file": ("front.jpg", io.BytesIO(image_data1), "image/jpeg")},
            data={"file_type": ImageType.FRONT}
        )
        assert response1.status_code == status.HTTP_201_CREATED
        
        # Get images list
        response: Response = authenticated_client.get(f"/api/items/{test_item.id}/images")
        
        assert response.status_code == status.HTTP_200_OK
        images: list[dict[str, Any]] = response.json()
        assert len(images) == 1
        assert images[0]["type"] == ImageType.FRONT

    @patch('api.routes.items.get_storage_service')
    def test_get_specific_image(self, mock_get_storage, authenticated_client: TestClient, test_user: User, test_item: Item):
        """
        Flow: Upload image, then GET /api/items/{item_id}/images/{image_id}
        Expected: 200 OK with specific image details
        """
        # Mock the storage service
        mock_storage_service = AsyncMock(spec=StorageService)
        mock_storage_service.upload_file.return_value = ("test/path/image.jpg", 1024)
        mock_get_storage.return_value = mock_storage_service
        
        # Upload image
        image_data = b"fake_image_data"
        upload_response: Response = authenticated_client.post(
            f"/api/items/{test_item.id}/images",
            files={"file": ("test.jpg", io.BytesIO(image_data), "image/jpeg")},
            data={"file_type": ImageType.FRONT}
        )
        assert upload_response.status_code == status.HTTP_201_CREATED
        uploaded_image: dict[str, Any] = upload_response.json()
        image_id: str = uploaded_image["id"]
        
        # Get specific image
        response: Response = authenticated_client.get(f"/api/items/{test_item.id}/images/{image_id}")
        
        assert response.status_code == status.HTTP_200_OK
        image_data_response: dict[str, Any] = response.json()
        assert image_data_response["id"] == image_id
        assert image_data_response["type"] == ImageType.FRONT
        assert image_data_response["item_id"] == str(test_item.id)

    def test_get_nonexistent_image(self, authenticated_client: TestClient, test_user: User, test_item: Item):
        """
        Flow: GET /api/items/{item_id}/images/{nonexistent_id}
        Expected: 404 Not Found with error message
        """
        fake_image_id = "00000000-0000-0000-0000-000000000000"
        response: Response = authenticated_client.get(f"/api/items/{test_item.id}/images/{fake_image_id}")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        error_detail: dict[str, Any] = response.json()
        assert "Image not found" in error_detail["detail"]

    @patch('api.routes.items.get_storage_service')
    def test_delete_image(self, mock_get_storage, authenticated_client: TestClient, test_user: User, test_item: Item):
        """
        Flow: Upload image, then DELETE /api/items/{item_id}/images/{image_id}
        Expected: 204 No Content, image removed from database and storage
        """
        # Mock the storage service
        mock_storage_service = AsyncMock(spec=StorageService)
        mock_storage_service.upload_file.return_value = ("test/path/image.jpg", 1024)
        mock_storage_service.delete_file.return_value = None
        mock_get_storage.return_value = mock_storage_service
        
        # Upload image
        image_data = b"fake_image_data"
        upload_response: Response = authenticated_client.post(
            f"/api/items/{test_item.id}/images",
            files={"file": ("test.jpg", io.BytesIO(image_data), "image/jpeg")},
            data={"file_type": ImageType.FRONT}
        )
        assert upload_response.status_code == status.HTTP_201_CREATED
        uploaded_image: dict[str, Any] = upload_response.json()
        image_id: str = uploaded_image["id"]
        
        # Delete image
        response: Response = authenticated_client.delete(f"/api/items/{test_item.id}/images/{image_id}")
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify image is no longer accessible
        get_response: Response = authenticated_client.get(f"/api/items/{test_item.id}/images/{image_id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    @patch('api.routes.items.get_storage_service')
    def test_delete_nonexistent_image(self, mock_get_storage, authenticated_client: TestClient, test_user: User, test_item: Item):
        """
        Flow: DELETE /api/items/{item_id}/images/{nonexistent_id}
        Expected: 404 Not Found with error message
        """
        # Mock the storage service
        mock_storage_service = AsyncMock(spec=StorageService)
        mock_get_storage.return_value = mock_storage_service
        
        fake_image_id = "00000000-0000-0000-0000-000000000000"
        response: Response = authenticated_client.delete(f"/api/items/{test_item.id}/images/{fake_image_id}")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        error_detail: dict[str, Any] = response.json()
        assert "Image not found" in error_detail["detail"]

    def test_image_ownership_verification(self, authenticated_client: TestClient, test_user: User, test_item: Item,
                                         another_user_client: TestClient):
        """
        Flow: Try to access images for another user's item
        Expected: 404 Not Found (item ownership verification)
        """
        # Try to get images for another user's item
        response: Response = another_user_client.get(f"/api/items/{test_item.id}/images")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        # Try to upload image to another user's item  
        image_data = b"fake_image_data"
        response: Response = another_user_client.post(
            f"/api/items/{test_item.id}/images",
            files={"file": ("test.jpg", io.BytesIO(image_data), "image/jpeg")},
            data={"file_type": ImageType.FRONT}
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
