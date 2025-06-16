"""Integration tests for complete application workflows."""
import pytest
from fastapi import status


class TestIntegrationWorkflows:
    """Test complete application workflows across multiple endpoints."""
    
    def test_complete_user_journey(self, authenticated_client, test_session):
        """Test complete user journey: register, login, create items."""
        
        # Step 1: User Registration
        registration_data = {
            "email": "journey@example.com",
            "password": "securepassword123"
        }
        
        register_response = authenticated_client.post("/api/auth/register", json=registration_data)
        assert register_response.status_code == status.HTTP_201_CREATED
        user_data = register_response.json()
        
        # Step 2: Create first item
        item1_data = {
            "name": "First Coin",
            "year": "2024",
            "description": "My first numismatic item",
            "material": "gold",
            "weight": 10.0
        }
        
        create_item1_response = authenticated_client.post("/api/items/", json=item1_data)
        assert create_item1_response.status_code == status.HTTP_201_CREATED
        item1 = create_item1_response.json()
        
        # Step 3: Create second item
        item2_data = {
            "name": "Silver Dollar",
            "year": "1921",
            "material": "silver",
            "weight": 26.73
        }
        
        create_item2_response = authenticated_client.post("/api/items/", json=item2_data)
        assert create_item2_response.status_code == status.HTTP_201_CREATED
        item2 = create_item2_response.json()
        
        # Step 4: View all items
        items_response = authenticated_client.get("/api/items/")
        assert items_response.status_code == status.HTTP_200_OK
        all_items = items_response.json()
        assert len(all_items) == 2
        
        # Items should be ordered by name
        item_names = [item["name"] for item in all_items]
        assert item_names == sorted(item_names)
        
        # Step 5: Update first item
        update_data = {
            "description": "Updated description for my first coin",
            "weight": 11.5
        }
        
        update_response = authenticated_client.put(f"/api/items/{item1['id']}", json=update_data)
        assert update_response.status_code == status.HTTP_200_OK
        updated_item = update_response.json()
        assert updated_item["description"] == update_data["description"]
        assert updated_item["weight"] == update_data["weight"]
        
        # Step 6: Delete one item
        delete_response = authenticated_client.delete(f"/api/items/{item2['id']}")
        assert delete_response.status_code == status.HTTP_204_NO_CONTENT
        
        # Step 7: Verify final state
        final_items_response = authenticated_client.get("/api/items/")
        assert final_items_response.status_code == status.HTTP_200_OK
        final_items = final_items_response.json()
        assert len(final_items) == 1
        assert final_items[0]["id"] == item1["id"]
        assert final_items[0]["description"] == update_data["description"]
    
    def test_concurrent_operations(self, authenticated_client, test_user):
        """Test concurrent-like operations to verify data consistency."""
        
        # Create multiple items in sequence
        items_data = [
            {"name": "Coin A", "year": "2024", "material": "gold"},
            {"name": "Coin B", "year": "2023", "material": "silver"},
            {"name": "Coin C", "year": "2022", "material": "platinum"}
        ]
        
        created_items = []
        for item_data in items_data:
            response = authenticated_client.post("/api/items/", json=item_data)
            assert response.status_code == status.HTTP_201_CREATED
            created_items.append(response.json())
        
        # Verify all items exist
        list_response = authenticated_client.get("/api/items/")
        assert list_response.status_code == status.HTTP_200_OK
        items_list = list_response.json()
        assert len(items_list) == 3
        
        # Perform updates on multiple items
        for i, item in enumerate(created_items):
            update_data = {"description": f"Updated description {i}"}
            update_response = authenticated_client.put(f"/api/items/{item['id']}", json=update_data)
            assert update_response.status_code == status.HTTP_200_OK
        
        # Verify all updates were applied
        final_list_response = authenticated_client.get("/api/items/")
        assert final_list_response.status_code == status.HTTP_200_OK
        final_items = final_list_response.json()
        assert len(final_items) == 3
        
        for i, item in enumerate(final_items):
            assert f"Updated description {i}" in [item["description"] for item in final_items]
    
    def test_error_handling_workflow(self, authenticated_client, test_user):
        """Test error handling across different scenarios."""
        
        # Test 1: Create item with invalid data
        invalid_item = {
            "name": "",  # Empty name should fail validation
            "year": "2024",
            "material": "gold"
        }
        
        response = authenticated_client.post("/api/items/", json=invalid_item)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Test 2: Access non-existent item
        response = authenticated_client.get("/api/items/non-existent-id")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        # Test 3: Update non-existent item
        response = authenticated_client.put("/api/items/non-existent-id", json={"name": "Updated"})
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        # Test 4: Delete non-existent item
        response = authenticated_client.delete("/api/items/non-existent-id")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        # Test 5: Create item with invalid material
        invalid_material_item = {
            "name": "Test Coin",
            "year": "2024",
            "material": "invalid_material"
        }
        
        response = authenticated_client.post("/api/items/", json=invalid_material_item)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Verify no side effects - user should still be able to create valid items
        valid_item = {
            "name": "Valid Coin",
            "year": "2024",
            "material": "silver"
        }
        
        response = authenticated_client.post("/api/items/", json=valid_item)
        assert response.status_code == status.HTTP_201_CREATED
    
    def test_data_consistency_workflow(self, authenticated_client, test_user):
        """Test data consistency across operations."""
        
        # Create an item
        item_data = {
            "name": "Consistency Test Coin",
            "year": "2024",
            "description": "Testing data consistency",
            "material": "gold",
            "weight": 15.0
        }
        
        create_response = authenticated_client.post("/api/items/", json=item_data)
        assert create_response.status_code == status.HTTP_201_CREATED
        created_item = create_response.json()
        item_id = created_item["id"]
        
        # Verify item appears in list
        list_response = authenticated_client.get("/api/items/")
        assert list_response.status_code == status.HTTP_200_OK
        items_list = list_response.json()
        assert len(items_list) == 1
        assert items_list[0]["id"] == item_id
        
        # Verify item can be retrieved individually
        get_response = authenticated_client.get(f"/api/items/{item_id}")
        assert get_response.status_code == status.HTTP_200_OK
        retrieved_item = get_response.json()
        assert retrieved_item["name"] == item_data["name"]
        assert retrieved_item["weight"] == item_data["weight"]
        
        # Update the item
        update_data = {
            "weight": 16.5,
            "description": "Updated description"
        }
        
        update_response = authenticated_client.put(f"/api/items/{item_id}", json=update_data)
        assert update_response.status_code == status.HTTP_200_OK
        
        # Verify updates are reflected in both individual get and list
        updated_get_response = authenticated_client.get(f"/api/items/{item_id}")
        assert updated_get_response.status_code == status.HTTP_200_OK
        updated_item = updated_get_response.json()
        assert updated_item["weight"] == update_data["weight"]
        assert updated_item["description"] == update_data["description"]
        assert updated_item["name"] == item_data["name"]  # Unchanged field
        
        updated_list_response = authenticated_client.get("/api/items/")
        assert updated_list_response.status_code == status.HTTP_200_OK
        updated_list = updated_list_response.json()
        assert len(updated_list) == 1
        assert updated_list[0]["weight"] == update_data["weight"]
        assert updated_list[0]["description"] == update_data["description"]
        
        # Delete the item
        delete_response = authenticated_client.delete(f"/api/items/{item_id}")
        assert delete_response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify item is gone from both individual get and list
        final_get_response = authenticated_client.get(f"/api/items/{item_id}")
        assert final_get_response.status_code == status.HTTP_404_NOT_FOUND
        
        final_list_response = authenticated_client.get("/api/items/")
        assert final_list_response.status_code == status.HTTP_200_OK
        final_list = final_list_response.json()
        assert len(final_list) == 0
