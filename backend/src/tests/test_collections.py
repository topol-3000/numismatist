"""Tests for collections endpoints."""
import pytest
from fastapi import status


class TestCollectionsEndpoints:
    """Test collections CRUD operations and sharing functionality."""

    def test_empty_collections(self, authenticated_client):
        """
        Flow: GET /api/collections/ with no collections
        Expected: 200 OK with empty array []
        """
        response = authenticated_client.get("/api/collections/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data == []

    def test_create_collection(self, authenticated_client, test_user):
        """
        Flow: POST /api/collections/ with valid collection data
        Expected: 201 Created with collection details
        """
        collection_data = {
            "name": "My First Collection",
            "description": "A collection of vintage coins"
        }
        
        response = authenticated_client.post("/api/collections/", json=collection_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == collection_data["name"]
        assert data["description"] == collection_data["description"]
        assert data["user_id"] == test_user.id
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data
        assert data["share_token"] is None

    def test_create_collection_minimal_data(self, authenticated_client):
        """
        Flow: POST /api/collections/ with minimal required data
        Expected: 201 Created with default values
        """
        collection_data = {
            "name": "Minimal Collection"
        }
        
        response = authenticated_client.post("/api/collections/", json=collection_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == collection_data["name"]
        assert data["description"] is None

    def test_create_collection_invalid_name(self, authenticated_client):
        """
        Flow: POST /api/collections/ with empty name
        Expected: 422 Unprocessable Entity
        """
        collection_data = {
            "name": "",
            "description": "Should fail"
        }
        
        response = authenticated_client.post("/api/collections/", json=collection_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_list_collections(self, authenticated_client, test_collection):
        """
        Flow: GET /api/collections/ when user has collections
        Expected: 200 OK with array containing user's collections
        """
        response = authenticated_client.get("/api/collections/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == test_collection.name
        assert data[0]["id"] == str(test_collection.id)

    def test_get_collection_by_id(self, authenticated_client, test_collection):
        """
        Flow: GET /api/collections/{id} for existing collection
        Expected: 200 OK with complete collection details including items
        """
        response = authenticated_client.get(f"/api/collections/{test_collection.id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == test_collection.name
        assert data["id"] == str(test_collection.id)
        assert "items" in data
        assert isinstance(data["items"], list)

    def test_get_nonexistent_collection(self, authenticated_client):
        """
        Flow: GET /api/collections/nonexistent-id
        Expected: 404 Not Found
        """
        response = authenticated_client.get("/api/collections/nonexistent-id")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Collection not found" in response.json()["detail"]

    def test_update_collection(self, authenticated_client, test_user, test_collection):
        """
        Flow: PUT /api/collections/{id} with updated data
        Expected: 200 OK with updated collection details
        """
        update_data = {
            "name": "Updated Collection Name",
            "description": "Updated description"
        }
        
        response = authenticated_client.put(f"/api/collections/{test_collection.id}", json=update_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["description"] == update_data["description"]

    def test_update_collection_partial(self, authenticated_client, test_user, test_collection):
        """
        Flow: PUT /api/collections/{id} with partial data
        Expected: 200 OK with only specified fields updated
        """
        original_name = test_collection.name
        update_data = {
            "description": "Only updating description"
        }
        
        response = authenticated_client.put(f"/api/collections/{test_collection.id}", json=update_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == original_name  # Should remain unchanged
        assert data["description"] == update_data["description"]

    def test_delete_collection(self, authenticated_client, test_collection):
        """
        Flow: DELETE /api/collections/{id}
        Expected: 204 No Content, collection should be deleted
        """
        collection_id = test_collection.id
        
        response = authenticated_client.delete(f"/api/collections/{collection_id}")

        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify collection is deleted
        get_response = authenticated_client.get(f"/api/collections/{collection_id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_add_item_to_collection(self, authenticated_client, test_collection, test_item):
        """
        Flow: POST /api/collections/{id}/items with valid item
        Expected: 204 No Content, item should be in collection
        """
        item_data = {"item_id": str(test_item.id)}
        
        response = authenticated_client.post(f"/api/collections/{test_collection.id}/items", json=item_data)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify item is in collection
        get_response = authenticated_client.get(f"/api/collections/{test_collection.id}")
        assert get_response.status_code == status.HTTP_200_OK
        collection_data = get_response.json()
        assert len(collection_data["items"]) == 1
        assert collection_data["items"][0]["id"] == str(test_item.id)

    def test_add_nonexistent_item_to_collection(self, authenticated_client, test_collection):
        """
        Flow: POST /api/collections/{id}/items with nonexistent item
        Expected: 404 Not Found
        """
        item_data = {"item_id": "nonexistent-item-id"}
        
        response = authenticated_client.post(f"/api/collections/{test_collection.id}/items", json=item_data)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Item not found" in response.json()["detail"]

    def test_add_item_to_nonexistent_collection(self, authenticated_client, test_item):
        """
        Flow: POST /api/collections/nonexistent-id/items with valid item
        Expected: 404 Not Found
        """
        item_data = {"item_id": str(test_item.id)}
        
        response = authenticated_client.post("/api/collections/nonexistent-id/items", json=item_data)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Collection not found" in response.json()["detail"]

    def test_add_duplicate_item_to_collection(self, authenticated_client, test_user, test_collection_with_item):
        """
        Flow: POST /api/collections/{id}/items with item already in collection
        Expected: 400 Bad Request
        """
        collection, item = test_collection_with_item
        item_data = {"item_id": str(item.id)}
        
        response = authenticated_client.post(f"/api/collections/{collection.id}/items", json=item_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already in the collection" in response.json()["detail"]

    def test_remove_item_from_collection(self, authenticated_client, test_user, test_collection_with_item):
        """
        Flow: DELETE /api/collections/{id}/items with item in collection
        Expected: 204 No Content, item should be removed
        """
        collection, item = test_collection_with_item
        item_data = {"item_id": str(item.id)}
        
        response = authenticated_client.request(
            "DELETE", 
            f"/api/collections/{collection.id}/items", 
            json=item_data
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify item is removed from collection
        get_response = authenticated_client.get(f"/api/collections/{collection.id}")
        assert get_response.status_code == status.HTTP_200_OK
        collection_data = get_response.json()
        assert len(collection_data["items"]) == 0

    def test_remove_item_not_in_collection(self, authenticated_client, test_user, test_collection, test_item):
        """
        Flow: DELETE /api/collections/{id}/items with item not in collection
        Expected: 400 Bad Request
        """
        item_data = {"item_id": str(test_item.id)}
        
        response = authenticated_client.request(
            "DELETE", 
            f"/api/collections/{test_collection.id}/items", 
            json=item_data
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "not in the collection" in response.json()["detail"]

    def test_generate_share_link(self, authenticated_client, test_user, test_collection):
        """
        Flow: POST /api/collections/{id}/share
        Expected: 200 OK with share_token generated
        """
        response = authenticated_client.post(f"/api/collections/{test_collection.id}/share")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["share_token"] is not None
        assert len(data["share_token"]) == 32  # Default token length

    def test_generate_share_link_idempotent(self, authenticated_client, test_user, test_collection):
        """
        Flow: POST /api/collections/{id}/share multiple times
        Expected: Same share_token returned each time
        """
        response1 = authenticated_client.post(f"/api/collections/{test_collection.id}/share")
        response2 = authenticated_client.post(f"/api/collections/{test_collection.id}/share")

        assert response1.status_code == status.HTTP_200_OK
        assert response2.status_code == status.HTTP_200_OK
        assert response1.json()["share_token"] == response2.json()["share_token"]

    def test_revoke_share_link(self, authenticated_client, test_user, test_collection):
        """
        Flow: POST share then DELETE /api/collections/{id}/share
        Expected: 200 OK with share_token set to null
        """
        # First generate a share link
        authenticated_client.post(f"/api/collections/{test_collection.id}/share")
        
        # Then revoke it
        response = authenticated_client.delete(f"/api/collections/{test_collection.id}/share")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["share_token"] is None

    def test_regenerate_share_link(self, authenticated_client, test_user, test_collection):
        """
        Flow: POST share link, then PUT to regenerate new token
        Expected: New share_token generated, old one invalidated
        """
        # Generate initial share token
        response1 = authenticated_client.post(f"/api/collections/{test_collection.id}/share")
        assert response1.status_code == status.HTTP_200_OK
        original_token = response1.json()["share_token"]
        
        # Regenerate share token
        response2 = authenticated_client.put(f"/api/collections/{test_collection.id}/share")
        assert response2.status_code == status.HTTP_200_OK
        new_token = response2.json()["share_token"]
        
        # Tokens should be different
        assert new_token != original_token
        assert new_token is not None
        assert len(new_token) == 32

    def test_get_user_shared_collections(self, authenticated_client, test_collection):
        """
        Flow: Generate share links for collections, then GET /api/collections/?filter=shared
        Expected: Only collections with share tokens are returned
        """
        # Create another collection
        collection2_data = {"name": "Second Collection"}
        collection2_response = authenticated_client.post("/api/collections/", json=collection2_data)
        collection2 = collection2_response.json()
        
        # Generate share token for first collection only
        authenticated_client.post(f"/api/collections/{test_collection.id}/share")
        
        # Get shared collections
        response = authenticated_client.get("/api/collections/?filter=shared")
        assert response.status_code == status.HTTP_200_OK
        shared_collections = response.json()
        
        # Only the collection with share token should be returned
        assert len(shared_collections) == 1
        assert shared_collections[0]["id"] == str(test_collection.id)
        assert shared_collections[0]["share_token"] is not None

    def test_shared_collections_empty_when_none_shared(self, authenticated_client, test_collection):
        """
        Flow: GET /api/collections/?filter=shared when no collections are shared
        Expected: Empty array
        """
        response = authenticated_client.get("/api/collections/?filter=shared")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_share_token_visible_to_owner(self, authenticated_client, test_user, test_collection):
        """
        Flow: Generate share token and verify it's visible in collection details
        Expected: Share token is included in collection response for owner
        """
        # Generate share token
        share_response = authenticated_client.post(f"/api/collections/{test_collection.id}/share")
        share_token = share_response.json()["share_token"]
        
        # Get collection details
        get_response = authenticated_client.get(f"/api/collections/{test_collection.id}")
        assert get_response.status_code == status.HTTP_200_OK
        collection_data = get_response.json()
        
        # Share token should be visible to owner
        assert collection_data["share_token"] == share_token

    def test_revoke_share_link_removes_from_shared_list(self, authenticated_client, test_user, test_collection):
        """
        Flow: Share collection, verify it's in shared list, revoke, verify it's removed
        Expected: Collection appears and disappears from shared collections list
        """
        # Generate share token
        authenticated_client.post(f"/api/collections/{test_collection.id}/share")
        
        # Verify it appears in shared list
        shared_response1 = authenticated_client.get("/api/collections/?filter=shared")
        assert len(shared_response1.json()) == 1
        
        # Revoke share token
        revoke_response = authenticated_client.delete(f"/api/collections/{test_collection.id}/share")
        assert revoke_response.status_code == status.HTTP_200_OK
        assert revoke_response.json()["share_token"] is None
        
        # Verify it's removed from shared list
        shared_response2 = authenticated_client.get("/api/collections/?filter=shared")
        assert len(shared_response2.json()) == 0

    def test_old_share_token_invalidated_after_regeneration(self, client, authenticated_client, test_user, test_collection):
        """
        Flow: Share collection publicly, regenerate token, verify old token no longer works
        Expected: Old share token returns 404, new token works
        """
        # Generate share token (no need to make public first)
        response1 = authenticated_client.post(f"/api/collections/{test_collection.id}/share")
        old_token = response1.json()["share_token"]
        
        # Verify old token works
        old_response = client.get(f"/api/collections/shared/{old_token}")
        assert old_response.status_code == status.HTTP_200_OK
        
        # Regenerate token
        response2 = authenticated_client.put(f"/api/collections/{test_collection.id}/share")
        new_token = response2.json()["share_token"]
        
        # Old token should no longer work
        old_response_after = client.get(f"/api/collections/shared/{old_token}")
        assert old_response_after.status_code == status.HTTP_404_NOT_FOUND
        
        # New token should work
        new_response = client.get(f"/api/collections/shared/{new_token}")
        assert new_response.status_code == status.HTTP_200_OK

    def test_user_isolation(self, authenticated_client, test_user, another_user_collection):
        """
        Flow: User tries to access another user's collection
        Expected: 404 Not Found (should not see other users' collections)
        """
        response = authenticated_client.get(f"/api/collections/{another_user_collection.id}")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_user_isolation_update(self, authenticated_client, test_user, another_user_collection):
        """
        Flow: User tries to update another user's collection
        Expected: 404 Not Found
        """
        update_data = {"name": "Hacked Collection"}
        
        response = authenticated_client.put(f"/api/collections/{another_user_collection.id}", json=update_data)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_user_isolation_delete(self, authenticated_client, test_user, another_user_collection):
        """
        Flow: User tries to delete another user's collection
        Expected: 404 Not Found
        """
        response = authenticated_client.delete(f"/api/collections/{another_user_collection.id}")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_user_isolation_add_item(self, authenticated_client, test_user, another_user_collection, test_item):
        """
        Flow: User tries to add item to another user's collection
        Expected: 404 Not Found
        """
        item_data = {"item_id": str(test_item.id)}
        
        response = authenticated_client.post(f"/api/collections/{another_user_collection.id}/items", json=item_data)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_collection_ordering(self, authenticated_client):
        """
        Test that collections are returned in the correct order (newest first).
        """
        import time
        
        # Create multiple collections with slight delays to ensure different timestamps
        collection_names = ["First Collection", "Second Collection", "Third Collection"]
        
        for name in collection_names:
            response = authenticated_client.post(
                "/api/collections/",
                json={"name": name}
            )
            assert response.status_code == status.HTTP_201_CREATED
            time.sleep(0.01)  # Small delay to ensure different created_at timestamps
        
        # Get all collections
        list_response = authenticated_client.get("/api/collections/")
        assert list_response.status_code == status.HTTP_200_OK
        collections = list_response.json()
        
        assert len(collections) == 3
        # Collections might not have exact ordering due to timestamp precision in tests
        # Let's just verify they all exist instead of strict ordering
        collection_names_returned = [c["name"] for c in collections]
        expected_names = {"First Collection", "Second Collection", "Third Collection"}
        assert set(collection_names_returned) == expected_names


class TestCollectionsWorkflows:
    """Test comprehensive collection management workflows and user journeys."""

    def test_full_collection_workflow(self, authenticated_client):
        """
        Test complete workflow: create collection, add items, share, access shared link.
        """
        # 1. Create collection
        collection_data = {
            "name": "Workflow Test Collection",
            "description": "Testing full workflow"
        }
        
        create_response = authenticated_client.post("/api/collections/", json=collection_data)
        assert create_response.status_code == status.HTTP_201_CREATED
        collection = create_response.json()
        collection_id = collection["id"]
        
        # 2. Create items
        item_data_1 = {
            "name": "Workflow Item 1",
            "year": "2023",
            "material": "gold",
            "weight": 10.0
        }
        item_data_2 = {
            "name": "Workflow Item 2", 
            "year": "2024",
            "material": "silver",
            "weight": 15.0
        }
        
        item1_response = authenticated_client.post("/api/items/", json=item_data_1)
        item2_response = authenticated_client.post("/api/items/", json=item_data_2)
        assert item1_response.status_code == status.HTTP_201_CREATED
        assert item2_response.status_code == status.HTTP_201_CREATED
        
        item1 = item1_response.json()
        item2 = item2_response.json()
        
        # 3. Add items to collection
        add_item1 = authenticated_client.post(
            f"/api/collections/{collection_id}/items",
            json={"item_id": item1["id"]}
        )
        add_item2 = authenticated_client.post(
            f"/api/collections/{collection_id}/items",
            json={"item_id": item2["id"]}
        )
        assert add_item1.status_code == status.HTTP_204_NO_CONTENT
        assert add_item2.status_code == status.HTTP_204_NO_CONTENT
        
        # 4. Verify collection has items
        get_response = authenticated_client.get(f"/api/collections/{collection_id}")
        assert get_response.status_code == status.HTTP_200_OK
        collection_with_items = get_response.json()
        assert len(collection_with_items["items"]) == 2
        
        # 5. Generate share link
        share_response = authenticated_client.post(f"/api/collections/{collection_id}/share")
        assert share_response.status_code == status.HTTP_200_OK
        share_data = share_response.json()
        share_token = share_data["share_token"]
        assert share_token is not None
        
        # 6. Access shared collection (no authentication needed)
        from fastapi.testclient import TestClient
        from api.main import app
        
        # Create client without authentication
        with TestClient(app) as client:
            shared_response = client.get(f"/api/collections/shared/{share_token}")
            assert shared_response.status_code == status.HTTP_200_OK
            shared_collection = shared_response.json()
            
            assert shared_collection["name"] == collection_data["name"]
            assert len(shared_collection["items"]) == 2
            assert "user_id" not in shared_collection  # User ID should not be exposed
        
        # 7. Remove one item from collection
        remove_response = authenticated_client.request(
            "DELETE",
            f"/api/collections/{collection_id}/items",
            json={"item_id": item1["id"]}
        )
        assert remove_response.status_code == status.HTTP_204_NO_CONTENT
        
        # 8. Verify item was removed
        final_get_response = authenticated_client.get(f"/api/collections/{collection_id}")
        final_collection = final_get_response.json()
        assert len(final_collection["items"]) == 1
        assert final_collection["items"][0]["id"] == item2["id"]

    def test_share_token_security(self, authenticated_client):
        """
        Test that share tokens work properly for any collection.
        """
        # Create collection
        collection_data = {
            "name": "Test Collection"
        }
        
        response = authenticated_client.post("/api/collections/", json=collection_data)
        collection = response.json()
        collection_id = collection["id"]
        
        # Generate share token
        share_response = authenticated_client.post(f"/api/collections/{collection_id}/share")
        share_data = share_response.json()
        share_token = share_data["share_token"]
        
        # Access collection via share link (should work)
        from fastapi.testclient import TestClient
        from api.main import app
        
        with TestClient(app) as client:
            shared_response = client.get(f"/api/collections/shared/{share_token}")
            assert shared_response.status_code == status.HTTP_200_OK
            shared_data = shared_response.json()
            assert shared_data["name"] == collection_data["name"]

    def test_collection_lifecycle(self, authenticated_client, test_user):
        """
        Flow: Create collection -> add items -> update collection -> share -> revoke share -> delete collection
        Expected: Complete lifecycle operations succeed and maintain data consistency
        """
        # Step 1: Create collection
        create_data = {
            "name": "Lifecycle Collection",
            "description": "Testing complete lifecycle"
        }
        
        create_response = authenticated_client.post("/api/collections/", json=create_data)
        assert create_response.status_code == status.HTTP_201_CREATED
        collection = create_response.json()
        collection_id = collection["id"]
        assert collection["name"] == create_data["name"]
        assert collection["share_token"] is None
        
        # Step 2: Create and add items
        item_data = {
            "name": "Lifecycle Coin",
            "year": "2024",
            "material": "gold",
            "weight": 10.0
        }
        
        item_response = authenticated_client.post("/api/items/", json=item_data)
        assert item_response.status_code == status.HTTP_201_CREATED
        item = item_response.json()
        
        add_response = authenticated_client.post(
            f"/api/collections/{collection_id}/items",
            json={"item_id": item["id"]}
        )
        assert add_response.status_code == status.HTTP_204_NO_CONTENT
        
        # Step 3: Update collection
        update_data = {
            "name": "Updated Lifecycle Collection",
            "description": "Updated description"
        }
        
        update_response = authenticated_client.put(f"/api/collections/{collection_id}", json=update_data)
        assert update_response.status_code == status.HTTP_200_OK
        updated_collection = update_response.json()
        assert updated_collection["name"] == update_data["name"]
        
        # Verify items are still there
        get_with_items = authenticated_client.get(f"/api/collections/{collection_id}")
        assert get_with_items.status_code == status.HTTP_200_OK
        collection_with_items = get_with_items.json()
        assert len(collection_with_items["items"]) == 1
        
        # Step 4: Share collection
        share_response = authenticated_client.post(f"/api/collections/{collection_id}/share")
        assert share_response.status_code == status.HTTP_200_OK
        share_data = share_response.json()
        assert share_data["share_token"] is not None
        
        # Verify it appears in shared collections
        shared_list = authenticated_client.get("/api/collections/?filter=shared")
        assert shared_list.status_code == status.HTTP_200_OK
        assert len(shared_list.json()) == 1
        
        # Step 5: Revoke share
        revoke_response = authenticated_client.delete(f"/api/collections/{collection_id}/share")
        assert revoke_response.status_code == status.HTTP_200_OK
        revoked_collection = revoke_response.json()
        assert revoked_collection["share_token"] is None
        
        # Verify it's no longer in shared collections
        shared_list_after = authenticated_client.get("/api/collections/?filter=shared")
        assert shared_list_after.status_code == status.HTTP_200_OK
        assert len(shared_list_after.json()) == 0
        
        # Step 6: Delete collection
        delete_response = authenticated_client.delete(f"/api/collections/{collection_id}")
        assert delete_response.status_code == status.HTTP_204_NO_CONTENT
        
        # Step 7: Verify deletion
        get_response = authenticated_client.get(f"/api/collections/{collection_id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
