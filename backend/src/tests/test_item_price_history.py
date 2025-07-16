"""Tests for item price history functionality."""
from typing import Any
import pytest
from fastapi import status
from fastapi.testclient import TestClient
from httpx import Response

from models.user import User
from models.item import Item


class TestItemPriceHistory:
    """Test item price history functionality."""

    def test_empty_price_history(self, authenticated_client: TestClient, test_user: User, test_item: Item):
        """
        Flow: GET /api/items/{item_id}/price-history for new item
        Expected: 200 OK with array containing only the purchase price entry
        """
        response: Response = authenticated_client.get(f"/api/items/{test_item.id}/price-history")
        
        assert response.status_code == status.HTTP_200_OK
        price_history: list[dict[str, Any]] = response.json()
        assert len(price_history) == 1  # Only purchase price entry
        assert price_history[0]["type"] == "p"  # Purchase type
        assert price_history[0]["item_id"] == str(test_item.id)

    def test_add_current_price_entry(self, authenticated_client: TestClient, test_user: User, test_item: Item):
        """
        Flow: POST /api/items/{item_id}/price-history with current market price
        Expected: 201 Created with new price entry, type 'c' (current)
        """
        price_data: dict[str, Any] = {
            "price": 12000,  # $120 in pennies
            "datetime": "2024-01-15T10:30:00"
        }
        
        response: Response = authenticated_client.post(f"/api/items/{test_item.id}/price-history", json=price_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        price_entry: dict[str, Any] = response.json()
        assert price_entry["price"] == price_data["price"]
        assert price_entry["type"] == "c"  # Current market price
        assert price_entry["item_id"] == str(test_item.id)

    def test_add_price_without_datetime(self, authenticated_client: TestClient, test_user: User, test_item: Item):
        """
        Flow: POST /api/items/{item_id}/price-history without datetime
        Expected: 201 Created with current datetime auto-generated
        """
        price_data: dict[str, Any] = {
            "price": 15000  # $150 in pennies
        }
        
        response: Response = authenticated_client.post(f"/api/items/{test_item.id}/price-history", json=price_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        price_entry: dict[str, Any] = response.json()
        assert price_entry["price"] == price_data["price"]
        assert price_entry["type"] == "c"
        assert "datetime" in price_entry  # Should have auto-generated datetime

    def test_get_price_history_multiple_entries(self, authenticated_client: TestClient, test_user: User, test_item: Item):
        """
        Flow: Add multiple price entries -> GET price history
        Expected: 200 OK with all entries ordered by datetime descending
        """
        # Add multiple price entries
        price_entries: list[dict[str, Any]] = [
            {"price": 10000, "datetime": "2024-01-10T10:00:00"},
            {"price": 12000, "datetime": "2024-01-15T10:00:00"},
            {"price": 11000, "datetime": "2024-01-12T10:00:00"},
        ]
        
        for price_data in price_entries:
            response: Response = authenticated_client.post(f"/api/items/{test_item.id}/price-history", json=price_data)
            assert response.status_code == status.HTTP_201_CREATED
        
        # Get price history
        response: Response = authenticated_client.get(f"/api/items/{test_item.id}/price-history")
        assert response.status_code == status.HTTP_200_OK
        
        history: list[dict[str, Any]] = response.json()
        assert len(history) == 4  # 3 new entries + 1 original purchase entry
        
        # Check entries are ordered by datetime descending (newest first)
        # Skip the first entry as it's the purchase entry with current timestamp
        market_entries: list[dict[str, Any]] = [entry for entry in history if entry["type"] == "c"]
        market_datetimes: list[str] = [entry["datetime"] for entry in market_entries]
        expected_order: list[str] = ["2024-01-15T10:00:00", "2024-01-12T10:00:00", "2024-01-10T10:00:00"]
        assert market_datetimes == expected_order

    def test_update_price_history_entry(self, authenticated_client: TestClient, test_user: User, test_item: Item):
        """
        Flow: Add price entry -> PATCH to update it
        Expected: 200 OK with updated price and datetime
        """
        # Add a price entry
        price_data: dict[str, Any] = {"price": 10000, "datetime": "2024-01-10T10:00:00"}
        create_response: Response = authenticated_client.post(f"/api/items/{test_item.id}/price-history", json=price_data)
        assert create_response.status_code == status.HTTP_201_CREATED
        
        entry_id: str = create_response.json()["id"]
        
        # Update the entry
        update_data: dict[str, Any] = {
            "price": 15000,
            "datetime": "2024-01-10T15:00:00"
        }
        
        response: Response = authenticated_client.patch(f"/api/items/{test_item.id}/price-history/{entry_id}", json=update_data)
        assert response.status_code == status.HTTP_200_OK
        
        updated_entry: dict[str, Any] = response.json()
        assert updated_entry["price"] == update_data["price"]
        assert updated_entry["datetime"] == update_data["datetime"]

    def test_delete_current_price_entry(self, authenticated_client: TestClient, test_user: User, test_item: Item):
        """
        Flow: Add current price entry -> DELETE it
        Expected: 204 No Content, entry removed from history
        """
        # Add a current price entry
        price_data: dict[str, Any] = {"price": 10000}
        create_response: Response = authenticated_client.post(f"/api/items/{test_item.id}/price-history", json=price_data)
        assert create_response.status_code == status.HTTP_201_CREATED
        
        entry_id: str = create_response.json()["id"]
        
        # Delete the entry
        response: Response = authenticated_client.delete(f"/api/items/{test_item.id}/price-history/{entry_id}")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify entry is removed
        history_response: Response = authenticated_client.get(f"/api/items/{test_item.id}/price-history")
        history: list[dict[str, Any]] = history_response.json()
        assert not any(entry["id"] == entry_id for entry in history)

    def test_cannot_delete_purchase_price_entry(self, authenticated_client: TestClient, test_user: User, test_item: Item):
        """
        Flow: Try to DELETE purchase price entry (type 'p')
        Expected: 400 Bad Request with error about permanent records
        """
        # Get price history to find purchase entry
        response: Response = authenticated_client.get(f"/api/items/{test_item.id}/price-history")
        history: list[dict[str, Any]] = response.json()
        
        # Find the purchase entry (there's always exactly one purchase entry)
        purchase_entries: list[dict[str, Any]] = [entry for entry in history if entry["type"] == "p"]
        purchase_entry: dict[str, Any] = purchase_entries[0]
        
        # Try to delete it
        response: Response = authenticated_client.delete(f"/api/items/{test_item.id}/price-history/{purchase_entry['id']}")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "permanent records" in response.json()["detail"]

    def test_price_history_item_ownership(self, authenticated_client: TestClient, test_user: User, test_item: Item, another_user_client: TestClient):
        """
        Flow: Try to access another user's item price history
        Expected: 404 Not Found (item ownership verification)
        """
        # Try to access price history of another user's item
        response: Response = another_user_client.get(f"/api/items/{test_item.id}/price-history")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        # Try to add price history to another user's item
        price_data: dict[str, Any] = {"price": 10000}
        response: Response = another_user_client.post(f"/api/items/{test_item.id}/price-history", json=price_data)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_price_history_with_nonexistent_item(self, authenticated_client: TestClient, test_user: User):
        """
        Flow: Try to access price history of non-existent item
        Expected: 404 Not Found
        """
        nonexistent_uuid: str = "12345678-1234-1234-1234-123456789012"
        
        response: Response = authenticated_client.get(f"/api/items/{nonexistent_uuid}/price-history")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_price_history_validation(self, authenticated_client: TestClient, test_user: User, test_item: Item):
        """
        Flow: POST invalid price data (negative price)
        Expected: 422 Unprocessable Entity
        """
        invalid_price_data: dict[str, Any] = {
            "price": -1000  # Negative price should be invalid
        }
        
        response: Response = authenticated_client.post(f"/api/items/{test_item.id}/price-history", json=invalid_price_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_update_nonexistent_price_entry(self, authenticated_client: TestClient, test_user: User, test_item: Item):
        """
        Flow: PATCH non-existent price history entry
        Expected: 404 Not Found
        """
        nonexistent_entry_id: int = 99999
        update_data: dict[str, Any] = {"price": 10000}
        
        response: Response = authenticated_client.patch(f"/api/items/{test_item.id}/price-history/{nonexistent_entry_id}", json=update_data)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_item_with_price_history_in_detail_view(self, authenticated_client: TestClient, test_user: User, test_item: Item):
        """
        Flow: Add price entries -> GET /api/items/{item_id} (detail view)
        Expected: 200 OK with price_history array included
        """
        # Add a price entry
        price_data: dict[str, Any] = {"price": 12000, "datetime": "2024-01-15T10:00:00"}
        create_response: Response = authenticated_client.post(f"/api/items/{test_item.id}/price-history", json=price_data)
        assert create_response.status_code == status.HTTP_201_CREATED
        
        # Get item detail view
        response: Response = authenticated_client.get(f"/api/items/{test_item.id}")
        assert response.status_code == status.HTTP_200_OK
        
        item_data: dict[str, Any] = response.json()
        assert "price_history" in item_data
        assert len(item_data["price_history"]) == 2  # Purchase + current price
        
        # Verify price history is ordered by datetime descending
        price_history: list[dict[str, Any]] = item_data["price_history"]
        datetimes: list[str] = [entry["datetime"] for entry in price_history]
        assert datetimes == sorted(datetimes, reverse=True)

    def test_price_history_workflow(self, authenticated_client: TestClient, test_user: User):
        """
        Flow: Complete price history workflow
        Expected: Create item -> add multiple prices -> update -> delete -> verify
        """
        # Step 1: Create item (creates purchase price entry)
        item_data: dict[str, Any] = {
            "name": "Price History Coin",
            "year": "2024",
            "material": "gold",
            "purchase_price": 50000,  # $500 purchase price
            "purchase_date": "2024-01-01T10:00:00"
        }
        
        create_response: Response = authenticated_client.post("/api/items/", json=item_data)
        assert create_response.status_code == status.HTTP_201_CREATED
        item_id: str = create_response.json()["id"]
        
        # Step 2: Add current market prices over time
        market_prices: list[dict[str, Any]] = [
            {"price": 52000, "datetime": "2024-01-15T10:00:00"},  # Price went up
            {"price": 48000, "datetime": "2024-01-20T10:00:00"},  # Price went down
            {"price": 55000, "datetime": "2024-01-25T10:00:00"},  # Price went up again
        ]
        
        created_entries: list[dict[str, Any]] = []
        for price_data in market_prices:
            response: Response = authenticated_client.post(f"/api/items/{item_id}/price-history", json=price_data)
            assert response.status_code == status.HTTP_201_CREATED
            created_entries.append(response.json())
        
        # Step 3: Verify complete history
        history_response: Response = authenticated_client.get(f"/api/items/{item_id}/price-history")
        assert history_response.status_code == status.HTTP_200_OK
        
        history: list[dict[str, Any]] = history_response.json()
        assert len(history) == 4  # 1 purchase + 3 market prices
        
        # Step 4: Update a price entry
        entry_to_update: dict[str, Any] = created_entries[0]
        update_data: dict[str, Any] = {"price": 53000}
        
        update_response: Response = authenticated_client.patch(f"/api/items/{item_id}/price-history/{entry_to_update['id']}", json=update_data)
        assert update_response.status_code == status.HTTP_200_OK
        
        # Step 5: Delete a current price entry (not purchase)
        entry_to_delete: dict[str, Any] = created_entries[1]
        delete_response: Response = authenticated_client.delete(f"/api/items/{item_id}/price-history/{entry_to_delete['id']}")
        assert delete_response.status_code == status.HTTP_204_NO_CONTENT
        
        # Step 6: Verify final state
        final_history_response: Response = authenticated_client.get(f"/api/items/{item_id}/price-history")
        final_history: list[dict[str, Any]] = final_history_response.json()
        assert len(final_history) == 3  # 1 purchase + 2 remaining market prices
        
        # Verify the updated price is reflected
        updated_entries: list[dict[str, Any]] = [entry for entry in final_history if entry["id"] == entry_to_update["id"]]
        updated_entry: dict[str, Any] = updated_entries[0]
        assert updated_entry["price"] == update_data["price"]
        
        # Verify the deleted entry is gone
        assert not any(entry["id"] == entry_to_delete["id"] for entry in final_history)
