"""Integration tests for complete application workflows."""
import pytest
from fastapi import status


class TestGeneralWorkflow:
    """Integration tests for numismatic application workflows including user journeys, collection management, and system reliability."""
    
    def test_user_collection_lifecycle(self, authenticated_client, test_session):
        """
        Flow: Register user -> create items -> update item -> delete item -> verify final state
        Expected: All operations succeed with proper status codes and data consistency maintained
        """
        # Register user
        response = authenticated_client.post("/api/auth/register", json={
            "email": "journey@example.com", "password": "securepassword123"
        })
        assert response.status_code == status.HTTP_201_CREATED
         # Create two items
        item1_response = authenticated_client.post("/api/items/", json={
            "name": "First Coin", "year": "2024", "description": "My first coin",
            "material": "gold", "weight": 10.0, "purchase_price": 15000
        })
        item2_response = authenticated_client.post("/api/items/", json={
            "name": "Silver Dollar", "year": "1921", "material": "silver", 
            "weight": 26.73, "purchase_price": 5000
        })
        assert item1_response.status_code == status.HTTP_201_CREATED
        assert item2_response.status_code == status.HTTP_201_CREATED
        
        item1, item2 = item1_response.json(), item2_response.json()
        
        # Verify collection has 2 items
        items = authenticated_client.get("/api/items/").json()
        assert len(items) == 2
        
        # Update first item
        update_response = authenticated_client.patch(f"/api/items/{item1['id']}", json={
            "description": "Updated description", "weight": 11.5
        })
        assert update_response.status_code == status.HTTP_200_OK
        updated_item = update_response.json()
        assert updated_item["description"] == "Updated description"
        assert updated_item["weight"] == 11.5
        
        # Delete second item
        delete_response = authenticated_client.delete(f"/api/items/{item2['id']}")
        assert delete_response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify final state: 1 updated item
        final_items = authenticated_client.get("/api/items/").json()
        assert len(final_items) == 1
        assert final_items[0]["id"] == item1["id"]
        assert final_items[0]["description"] == "Updated description"
    
    def test_bulk_operations(self, authenticated_client, test_user):
        """
        Flow: Create multiple items -> verify collection -> update all items -> verify all updates applied
        Expected: 201 for each creation, 200 for updates, consistent data across all operations
        """
        # Create 3 items
        items_data = [
            {"name": "Coin A", "year": "2024", "material": "gold", "purchase_price": 12000},
            {"name": "Coin B", "year": "2023", "material": "silver", "purchase_price": 4000},
            {"name": "Coin C", "year": "2022", "material": "platinum", "purchase_price": 25000}
        ]
        
        created_items = []
        for item_data in items_data:
            response = authenticated_client.post("/api/items/", json=item_data)
            assert response.status_code == status.HTTP_201_CREATED
            created_items.append(response.json())
        
        # Verify all items exist
        items_list = authenticated_client.get("/api/items/").json()
        assert len(items_list) == 3
        
        # Update all items
        for i, item in enumerate(created_items):
            update_response = authenticated_client.patch(f"/api/items/{item['id']}", 
                                                     json={"description": f"Updated description {i}"})
            assert update_response.status_code == status.HTTP_200_OK
        
        # Verify all updates applied
        final_items = authenticated_client.get("/api/items/").json()
        assert len(final_items) == 3
        
        descriptions = [item["description"] for item in final_items]
        for i in range(3):
            assert f"Updated description {i}" in descriptions
    
    def test_error_handling(self, authenticated_client, test_user):
        """
        Flow: Attempt invalid operations -> verify proper error codes -> confirm system recovery with valid operation
        Expected: Appropriate 4xx status codes for errors, 201 for recovery operation
        """
        # Invalid item data
        invalid_responses = [
            authenticated_client.post("/api/items/", json={"name": "", "year": "2024", "material": "gold", "purchase_price": 5000}),
            authenticated_client.get("/api/items/12345678-1234-1234-1234-123456789012"),  # Valid UUID format
            authenticated_client.patch("/api/items/12345678-1234-1234-1234-123456789012", json={"name": "Updated"}),
            authenticated_client.delete("/api/items/12345678-1234-1234-1234-123456789012"),
            authenticated_client.post("/api/items/", json={"name": "Test", "year": "2024", "material": "invalid", "purchase_price": 5000})
        ]
        
        expected_codes = [
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_404_NOT_FOUND,
            status.HTTP_404_NOT_FOUND,
            status.HTTP_404_NOT_FOUND,
            status.HTTP_422_UNPROCESSABLE_ENTITY
        ]
        
        for response, expected_code in zip(invalid_responses, expected_codes):
            assert response.status_code == expected_code
        
        # Verify system recovery with valid operation
        valid_response = authenticated_client.post("/api/items/", json={
            "name": "Valid Coin", "year": "2024", "material": "silver", "purchase_price": 6000
        })
        assert valid_response.status_code == status.HTTP_201_CREATED
    
    def test_data_consistency(self, authenticated_client, test_user):
        """
        Flow: Create item -> verify in list and individual views -> update -> verify changes -> delete -> verify removal
        Expected: Data consistency maintained across all views and operations, proper 404 after deletion
        """        # Create item
        item_data = {
            "name": "Consistency Test Coin", "year": "2024",
            "description": "Testing data consistency", "material": "gold", 
            "weight": 15.0, "purchase_price": 18000
        }

        created_response = authenticated_client.post("/api/items/", json=item_data)
        assert created_response.status_code == status.HTTP_201_CREATED
        created_item = created_response.json()
        item_id = created_item["id"]
        
        # Verify item in both list and individual get
        items_list = authenticated_client.get("/api/items/").json()
        individual_item = authenticated_client.get(f"/api/items/{item_id}").json()
        
        assert len(items_list) == 1
        assert items_list[0]["id"] == item_id
        assert individual_item["name"] == item_data["name"]
        assert individual_item["weight"] == item_data["weight"]
        
        # Update item
        update_data = {"weight": 16.5, "description": "Updated description"}
        authenticated_client.patch(f"/api/items/{item_id}", json=update_data)
        
        # Verify updates in both views
        updated_individual = authenticated_client.get(f"/api/items/{item_id}").json()
        updated_list = authenticated_client.get("/api/items/").json()
        
        assert updated_individual["weight"] == 16.5
        assert updated_individual["description"] == "Updated description"
        assert updated_individual["name"] == item_data["name"]  # Unchanged
        assert updated_list[0]["weight"] == 16.5
        assert updated_list[0]["description"] == "Updated description"
        
        # Delete item and verify removal
        delete_response = authenticated_client.delete(f"/api/items/{item_id}")
        assert delete_response.status_code == status.HTTP_204_NO_CONTENT
        
        get_response = authenticated_client.get(f"/api/items/{item_id}")
        final_list = authenticated_client.get("/api/items/").json()
        
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
        assert len(final_list) == 0
