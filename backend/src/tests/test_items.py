"""Tests for items endpoints."""
import pytest
from fastapi import status


class TestItemsEndpoints:
    """Test numismatic items CRUD operations and data validation."""

    def test_empty_collection(self, authenticated_client, test_user):
        """
        Flow: GET /api/items/ with no items in collection
        Expected: 200 OK with empty array []
        """
        response = authenticated_client.get("/api/items/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data == []

    def test_list_items(self, authenticated_client, test_user, test_item):
        """
        Flow: GET /api/items/ when user has items
        Expected: 200 OK with array containing user's items (name and ID match test_item)
        """
        response = authenticated_client.get("/api/items/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == test_item.name
        assert data[0]["id"] == str(test_item.id)

    def test_get_item_by_id(self, authenticated_client, test_user, test_item):
        """
        Flow: GET /api/items/{id} for existing item
        Expected: 200 OK with complete item details (name, year, material, weight)
        """
        response = authenticated_client.get(f"/api/items/{test_item.id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == test_item.name
        assert data["year"] == test_item.year
        assert data["material"] == test_item.material
        assert data["weight"] == test_item.weight

    def test_get_nonexistent_item(self, authenticated_client, test_user):
        """
        Flow: GET /api/items/nonexistent-id
        Expected: 404 Not Found with "Item not found" in error detail
        """
        response = authenticated_client.get("/api/items/nonexistent-id")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Item not found" in response.json()["detail"]

    def test_create_item_complete_data(self, authenticated_client, test_user):
        """
        Flow: POST /api/items/ with complete item data (name, year, description, material, weight)
        Expected: 201 Created with all fields preserved, user_id set, auto-generated ID
        """        
        item_data = {
            "name": "Gold Eagle",
            "year": "2023",
            "description": "American Gold Eagle coin",
            "material": "gold",
            "weight": 33.93
        }

        response = authenticated_client.post("/api/items/", json=item_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == item_data["name"]
        assert data["year"] == item_data["year"]
        assert data["material"] == item_data["material"]
        assert data["weight"] == item_data["weight"]
        assert data["user_id"] == test_user.id
        assert "id" in data

    def test_create_item_minimal_data(self, authenticated_client, test_user):
        """
        Flow: POST /api/items/ with only required fields (name, year, material)
        Expected: 201 Created with optional fields (description, weight) as null
        """
        item_data = {
            "name": "Simple Coin",
            "year": "2024",
            "material": "silver"
        }

        response = authenticated_client.post("/api/items/", json=item_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == item_data["name"]
        assert data["description"] is None
        assert data["weight"] is None

    def test_create_item_invalid_material(self, authenticated_client, test_user):
        """
        Flow: POST /api/items/ with invalid material enum value ("unobtainium")
        Expected: 422 Unprocessable Entity due to material validation
        """
        item_data = {
            "name": "Invalid Coin",
            "year": "2024",
            "material": "unobtainium"  # Invalid material
        }

        response = authenticated_client.post("/api/items/", json=item_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_item_missing_fields(self, authenticated_client, test_user):
        """
        Flow: POST /api/items/ with missing required fields (only name provided)
        Expected: 422 Unprocessable Entity due to missing year and material
        """
        item_data = {
            "name": "Incomplete Coin"
            # Missing year and material
        }

        response = authenticated_client.post("/api/items/", json=item_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_partial_update_item(self, authenticated_client, test_user, test_item):
        """
        Flow: PUT /api/items/{id} with partial data (description, weight only)
        Expected: 200 OK with updated fields changed, other fields unchanged
        """
        update_data = {
            "description": "Updated description",
            "weight": 15.0
        }

        response = authenticated_client.put(f"/api/items/{test_item.id}", json=update_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["description"] == update_data["description"]
        assert data["weight"] == update_data["weight"]
        # Other fields should remain unchanged
        assert data["name"] == test_item.name
        assert data["year"] == test_item.year

    def test_complete_update_item(self, authenticated_client, test_user, test_item):
        """
        Flow: PUT /api/items/{id} with all fields updated
        Expected: 200 OK with all fields matching new values
        """
        update_data = {
            "name": "Updated Coin Name",
            "year": "2025",
            "description": "Completely updated description",
            "material": "platinum",
            "weight": 20.5
        }

        response = authenticated_client.put(f"/api/items/{test_item.id}", json=update_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["year"] == update_data["year"]
        assert data["description"] == update_data["description"]
        assert data["material"] == update_data["material"]
        assert data["weight"] == update_data["weight"]

    def test_update_nonexistent_item(self, authenticated_client, test_user):
        """
        Flow: PUT /api/items/nonexistent-id with update data
        Expected: 404 Not Found
        """
        update_data = {"name": "New Name"}

        response = authenticated_client.put("/api/items/nonexistent-id", json=update_data)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_item(self, authenticated_client, test_user, test_item):
        """
        Flow: DELETE /api/items/{id} -> verify with GET /api/items/{id}
        Expected: 204 No Content, then 404 Not Found on verification
        """
        response = authenticated_client.delete(f"/api/items/{test_item.id}")

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify item is deleted
        get_response = authenticated_client.get(f"/api/items/{test_item.id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_nonexistent_item(self, authenticated_client, test_user):
        """
        Flow: DELETE /api/items/nonexistent-id
        Expected: 404 Not Found
        """
        response = authenticated_client.delete("/api/items/nonexistent-id")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_unauthenticated_access(self, client):
        """
        Flow: Access all item endpoints without authentication
        Expected: All return 401 Unauthorized (GET, POST, PUT, DELETE)
        """
        # Test all endpoints without authentication

        response = client.get("/api/items/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        response = client.get("/api/items/some-id")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        response = client.post("/api/items/", json={"name": "Test", "year": "2024", "material": "gold"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        response = client.put("/api/items/some-id", json={"name": "Updated"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        response = client.delete("/api/items/some-id")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestItemsWorkflows:
    """Test comprehensive item management workflows and user journeys."""

    def test_item_lifecycle(self, authenticated_client, test_user):
        """
        Flow: Create item -> read item -> update item -> delete item -> verify deletion
        Expected: All CRUD operations succeed (201 -> 200 -> 200 -> 204 -> 404)
        """
        # Step 1: Create item
        create_data = {
            "name": "Lifecycle Coin",
            "year": "2024",
            "description": "Testing lifecycle",
            "material": "silver",
            "weight": 12.0
        }

        create_response = authenticated_client.post("/api/items/", json=create_data)
        assert create_response.status_code == status.HTTP_201_CREATED
        item = create_response.json()
        item_id = item["id"]

        # Step 2: Read item
        read_response = authenticated_client.get(f"/api/items/{item_id}")
        assert read_response.status_code == status.HTTP_200_OK
        read_item = read_response.json()
        assert read_item["name"] == create_data["name"]

        # Step 3: Update item
        update_data = {
            "description": "Updated lifecycle description",
            "weight": 15.5
        }

        update_response = authenticated_client.put(f"/api/items/{item_id}", json=update_data)
        assert update_response.status_code == status.HTTP_200_OK
        updated_item = update_response.json()
        assert updated_item["description"] == update_data["description"]
        assert updated_item["weight"] == update_data["weight"]

        # Step 4: Delete item
        delete_response = authenticated_client.delete(f"/api/items/{item_id}")
        assert delete_response.status_code == status.HTTP_204_NO_CONTENT

        # Step 5: Verify deletion
        final_read = authenticated_client.get(f"/api/items/{item_id}")
        assert final_read.status_code == status.HTTP_404_NOT_FOUND

    def test_user_isolation(self, authenticated_client, test_user, test_session):
        """
        Flow: Create item -> verify it appears in user's list and can be accessed individually
        Expected: User can only see their own items, proper ownership isolation
        """
        # Create item as authenticated user
        create_data = {
            "name": "User 1 Coin",
            "year": "2024",
            "material": "gold"
        }

        create_response = authenticated_client.post("/api/items/", json=create_data)
        assert create_response.status_code == status.HTTP_201_CREATED
        item = create_response.json()
        item_id = item["id"]

        # Verify user can see their own items
        list_response = authenticated_client.get("/api/items/")
        assert list_response.status_code == status.HTTP_200_OK
        items = list_response.json()
        assert len(items) >= 1
        assert any(i["id"] == item_id for i in items)

        # Verify user can access their own item by ID
        get_response = authenticated_client.get(f"/api/items/{item_id}")
        assert get_response.status_code == status.HTTP_200_OK

    def test_bulk_operations(self, authenticated_client, test_user):
        """
        Flow: Create 3 items -> verify list shows all 3 ordered by name -> delete all -> verify empty list
        Expected: Bulk operations work correctly, collection state properly managed
        """
        # Create multiple items
        items_data = [
            {"name": "Coin 1", "year": "2020", "material": "gold"},
            {"name": "Coin 2", "year": "2021", "material": "silver"},
            {"name": "Coin 3", "year": "2022", "material": "copper"},
        ]

        created_items = []
        for item_data in items_data:
            response = authenticated_client.post("/api/items/", json=item_data)
            assert response.status_code == status.HTTP_201_CREATED
            created_items.append(response.json())

        # Verify all items are in the list
        list_response = authenticated_client.get("/api/items/")
        assert list_response.status_code == status.HTTP_200_OK
        items_list = list_response.json()
        assert len(items_list) == 3

        # Items should be ordered by name
        names = [item["name"] for item in items_list]
        assert names == sorted(names)

        # Delete all items
        for item in created_items:
            delete_response = authenticated_client.delete(f"/api/items/{item['id']}")
            assert delete_response.status_code == status.HTTP_204_NO_CONTENT

        # Verify list is empty
        final_list = authenticated_client.get("/api/items/")
        assert final_list.status_code == status.HTTP_200_OK
        assert final_list.json() == []
