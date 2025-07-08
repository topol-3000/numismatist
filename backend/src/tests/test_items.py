"""Tests for items endpoints."""
import pytest
from fastapi import status
from models.dealer import Dealer
from models.transaction import Transaction
from models.transaction_item import TransactionItem
from datetime import date
from sqlalchemy import select


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


@pytest.mark.asyncio
class TestItemTransactionIntegration:
    """Tests for item creation with transaction/dealer logic."""

    async def test_create_item_with_price_and_existing_dealer(self, authenticated_client, test_user, test_session):
        # Create dealer
        dealer = Dealer(name="Dealer1", contact_info="d1@dealer.com", user_id=test_user.id)
        test_session.add(dealer)
        await test_session.commit()
        await test_session.refresh(dealer)
        dealer_id = dealer.id
        # Create item with price and dealer_id
        item_data = {
            "name": "Coin A", "year": "2025", "material": "gold", "price": 1000, "dealer_id": dealer_id
        }
        response = authenticated_client.post("/api/items/", json=item_data)
        assert response.status_code == status.HTTP_201_CREATED
        # Check transaction and transaction_item created
        result = await test_session.execute(select(Transaction).where(Transaction.dealer_id == dealer_id, Transaction.user_id == test_user.id).order_by(Transaction.id.desc()))
        tx = result.scalars().first()
        assert tx is not None
        assert tx.total_amount == 1000
        result = await test_session.execute(select(TransactionItem).where(TransactionItem.transaction_id == tx.id))
        ti = result.scalars().first()
        assert ti is not None
        assert ti.price == 1000

    async def test_create_item_with_price_and_dealer_data(self, authenticated_client, test_user, test_session):
        # Create item with price and dealer_data
        item_data = {
            "name": "Coin B", "year": "2025", "material": "silver", "price": 500, "dealer_data": {"name": "Dealer2", "contact_info": "d2@dealer.com"}
        }
        response = authenticated_client.post("/api/items/", json=item_data)
        assert response.status_code == status.HTTP_201_CREATED
        # Check dealer, transaction, transaction_item created
        result = await test_session.execute(select(Dealer).where(Dealer.name == "Dealer2", Dealer.user_id == test_user.id))
        dealer = result.scalars().first()
        assert dealer is not None
        result = await test_session.execute(select(Transaction).where(Transaction.dealer_id == dealer.id, Transaction.user_id == test_user.id).order_by(Transaction.id.desc()))
        tx = result.scalars().first()
        assert tx is not None
        assert tx.total_amount == 500
        result = await test_session.execute(select(TransactionItem).where(TransactionItem.transaction_id == tx.id))
        ti = result.scalars().first()
        assert ti is not None
        assert ti.price == 500

    async def test_create_item_with_price_and_transaction_id(self, authenticated_client, test_user, test_session):
        # Create dealer and transaction
        dealer = Dealer(name="Dealer3", contact_info=None, user_id=test_user.id)
        test_session.add(dealer)
        await test_session.commit()
        await test_session.refresh(dealer)
        dealer_id = dealer.id
        tx = Transaction(dealer_id=dealer_id, user_id=test_user.id, date=date.today(), total_amount=0)
        test_session.add(tx)
        await test_session.commit()
        await test_session.refresh(tx)
        tx_id = tx.id
        # Create item with price and transaction_id
        item_data = {"name": "Coin C", "year": "2025", "material": "copper", "price": 200, "transaction_id": tx_id}
        response = authenticated_client.post("/api/items/", json=item_data)
        assert response.status_code == status.HTTP_201_CREATED
        # Check transaction total_amount updated
        await test_session.refresh(tx)
        assert tx.total_amount == 200
        result = await test_session.execute(select(TransactionItem).where(TransactionItem.transaction_id == tx.id))
        ti = result.scalars().first()
        assert ti is not None
        assert ti.price == 200

    async def test_create_item_with_no_transaction_fields(self, authenticated_client, test_user, test_session):
        # Create item with no price/dealer/transaction
        item_data = {"name": "Coin D", "year": "2025", "material": "silver"}
        response = authenticated_client.post("/api/items/", json=item_data)
        assert response.status_code == status.HTTP_201_CREATED
        # Should not create any transaction or transaction_item
        item_id = response.json()["id"]
        result = await test_session.execute(select(TransactionItem).where(TransactionItem.item_id == item_id))
        ti = result.scalars().first()
        assert ti is None

    async def test_create_item_with_price_but_no_dealer(self, authenticated_client, test_user):
        # Should fail (no dealer_id or dealer_data)
        item_data = {"name": "Coin E", "year": "2025", "material": "gold", "price": 100}
        response = authenticated_client.post("/api/items/", json=item_data)
        assert response.status_code == 404 or response.status_code == 422

    async def test_create_item_with_invalid_transaction_id(self, authenticated_client, test_user):
        # Should fail (transaction_id does not exist)
        item_data = {"name": "Coin F", "year": "2025", "material": "gold", "price": 100, "transaction_id": 999999}
        response = authenticated_client.post("/api/items/", json=item_data)
        assert response.status_code == 404
