"""Tests for transaction endpoints."""
import pytest
import pytest_asyncio
from fastapi import status
from sqlalchemy import select

from models import Collection, Counterparty, Item, ItemPriceHistory, Transaction, TransactionItem
from utils.enums import CounterpartyRole, PriceType, TransactionStatus, TransactionType


@pytest_asyncio.fixture
async def test_counterparty(test_session, test_user):
    """Create a test counterparty for transactions."""
    counterparty = Counterparty(
        name="Test Dealer",
        role=CounterpartyRole.BOTH,
        email="dealer@example.com",
        user_id=test_user.id,
    )
    test_session.add(counterparty)
    await test_session.commit()
    await test_session.refresh(counterparty)
    test_session.expunge(counterparty)
    return counterparty


@pytest_asyncio.fixture
async def test_transaction_item(test_session, test_user):
    """Create a test item for transactions."""
    item = Item(
        name="Transaction Test Coin",
        year=2024,
        description="Test coin for transactions",
        material="silver",
        weight=31.1,
        user_id=test_user.id,
    )
    test_session.add(item)
    await test_session.commit()
    await test_session.refresh(item)
    test_session.expunge(item)
    return item


class TestTransactionsEndpoints:
    """Test transaction endpoints."""

    def test_empty_transactions(self, authenticated_client, test_user):
        """Test GET /api/transactions/ with empty list."""
        response = authenticated_client.get("/api/transactions/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data == []

    def test_create_purchase_transaction(
        self, authenticated_client, test_user, test_counterparty, test_transaction_item
    ):
        """Test POST /api/transactions/purchase."""
        purchase_data = {
            "counterparty_id": test_counterparty.id,
            "currency": "usd",
            "notes": "Test purchase transaction",
            "items": [
                {
                    "item_id": str(test_transaction_item.id),
                    "price": 15000,  # $150.00 in cents
                    "currency": "usd",
                    "notes": "Test item purchase",
                }
            ],
        }

        response = authenticated_client.post("/api/transactions/purchase", json=purchase_data)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["transaction_type"] == "purchase"
        assert data["status"] == "completed"
        assert data["currency"] == "usd"
        assert data["total_amount"] == 15000

    def test_create_sale_transaction(
        self, authenticated_client, test_user, test_counterparty, test_transaction_item
    ):
        """Test POST /api/transactions/sale."""
        sale_data = {
            "counterparty_id": test_counterparty.id,
            "currency": "usd",
            "notes": "Test sale transaction",
            "items": [
                {
                    "item_id": str(test_transaction_item.id),
                    "price": 20000,  # $200.00 in cents
                    "currency": "usd",
                    "notes": "Test item sale",
                }
            ],
        }

        response = authenticated_client.post("/api/transactions/sale", json=sale_data)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["transaction_type"] == "sale"
        assert data["status"] == "completed"
        assert data["currency"] == "usd"
        assert data["total_amount"] == 20000

    def test_get_transaction_by_id(
        self, authenticated_client, test_user, test_counterparty, test_transaction_item
    ):
        """Test GET /api/transactions/{id}."""
        # Create transaction first
        purchase_data = {
            "counterparty_id": test_counterparty.id,
            "currency": "usd",
            "notes": "Test purchase for get test",
            "items": [
                {
                    "item_id": str(test_transaction_item.id),
                    "price": 15000,  # $150.00 in cents
                    "currency": "usd",
                    "notes": "Test item purchase",
                }
            ],
        }

        create_response = authenticated_client.post(
            "/api/transactions/purchase", json=purchase_data
        )
        assert create_response.status_code == status.HTTP_201_CREATED
        transaction_id = create_response.json()["id"]

        # Get transaction by ID
        response = authenticated_client.get(f"/api/transactions/{transaction_id}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == transaction_id
        assert data["transaction_type"] == "purchase"
        assert data["status"] == "completed"

    def test_cancel_transaction(
        self, authenticated_client, test_user, test_counterparty, test_transaction_item
    ):
        """Test POST /api/transactions/{id}/cancel."""
        # Create transaction first
        purchase_data = {
            "counterparty_id": test_counterparty.id,
            "currency": "usd",
            "notes": "Test purchase for cancel test",
            "items": [
                {
                    "item_id": str(test_transaction_item.id),
                    "price": 15000,  # $150.00 in cents
                    "currency": "usd",
                    "notes": "Test item purchase",
                }
            ],
        }

        create_response = authenticated_client.post(
            "/api/transactions/purchase", json=purchase_data
        )
        assert create_response.status_code == status.HTTP_201_CREATED
        transaction_id = create_response.json()["id"]

        # Cancel transaction
        response = authenticated_client.post(f"/api/transactions/{transaction_id}/cancel")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == transaction_id
        assert data["status"] == "cancelled"

    def test_get_nonexistent_transaction(self, authenticated_client, test_user):
        """Test GET /api/transactions/{id} for nonexistent transaction."""
        response = authenticated_client.get("/api/transactions/12345678-1234-1234-1234-123456789012")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_cancel_nonexistent_transaction(self, authenticated_client, test_user):
        """Test POST /api/transactions/{id}/cancel for nonexistent transaction."""
        response = authenticated_client.post("/api/transactions/12345678-1234-1234-1234-123456789012/cancel")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_purchase_with_invalid_counterparty(
        self, authenticated_client, test_user, test_transaction_item
    ):
        """Test POST /api/transactions/purchase with invalid counterparty."""
        purchase_data = {
            "counterparty_id": 999999,  # Non-existent counterparty
            "currency": "usd",
            "notes": "Test purchase with invalid counterparty",
            "items": [
                {
                    "item_id": str(test_transaction_item.id),
                    "price": 15000,
                    "currency": "usd",
                    "notes": "Test item purchase",
                }
            ],
        }

        response = authenticated_client.post("/api/transactions/purchase", json=purchase_data)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_purchase_with_invalid_item(
        self, authenticated_client, test_user, test_counterparty
    ):
        """Test POST /api/transactions/purchase with invalid item."""
        purchase_data = {
            "counterparty_id": test_counterparty.id,
            "currency": "usd",
            "notes": "Test purchase with invalid item",
            "items": [
                {
                    "item_id": "invalid-item-id",  # Non-existent item
                    "price": 15000,
                    "currency": "usd",
                    "notes": "Test invalid item purchase",
                }
            ],
        }

        response = authenticated_client.post("/api/transactions/purchase", json=purchase_data)
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest_asyncio.fixture
async def test_collection_with_item(test_session, test_user):
    """Create a test collection with one item."""
    # Create collection
    collection = Collection(
        name="Test Collection",
        description="Test collection for item removal tests",
        user_id=test_user.id,
    )
    test_session.add(collection)
    await test_session.flush()

    # Create item in collection
    item = Item(
        name="Collection Item",
        year=2024,
        description="Test item in collection",
        material="silver",
        weight=31.1,
        user_id=test_user.id,
        collection_id=collection.id,
    )
    test_session.add(item)

    await test_session.commit()
    
    # Refresh objects
    await test_session.refresh(collection)
    await test_session.refresh(item)
    
    # Expunge objects from session
    test_session.expunge(collection)
    test_session.expunge(item)
    
    return collection, item


class TestItemCollectionRemoval:
    """Test item removal from collections during individual sales."""

    async def test_individual_item_sale_removes_from_collection(
        self, authenticated_client, test_user, test_counterparty, test_collection_with_item, test_session
    ):
        """Test that selling individual item removes it from collection."""
        collection, item = test_collection_with_item
        
        # Verify item is initially in collection
        assert item.collection_id == collection.id

        # Sell individual item
        sale_data = {
            "counterparty_id": test_counterparty.id,
            "currency": "usd",
            "notes": "Test individual item sale",
            "items": [
                {
                    "item_id": str(item.id),
                    "price": 10000,  # $100.00 in cents
                    "currency": "usd",
                    "notes": "Test individual item sale",
                }
            ],
        }

        response = authenticated_client.post("/api/transactions/sale", json=sale_data)
        assert response.status_code == status.HTTP_201_CREATED

        # Verify item was removed from collection
        await test_session.commit()  # Refresh session
        item_result = await test_session.execute(
            select(Item).where(Item.id == item.id)
        )
        updated_item = item_result.scalar_one()
        assert updated_item.collection_id is None  # Item should be removed from collection

        # Verify SALE price history was created (not COLLECTION_SALE)
        price_history_result = await test_session.execute(
            select(ItemPriceHistory).where(
                ItemPriceHistory.item_id == item.id,
                ItemPriceHistory.type == PriceType.SALE
            )
        )
        sale_history = price_history_result.scalar_one()
        assert sale_history.price == 10000

    async def test_individual_sale_cancellation_keeps_item_out_of_collection(
        self, authenticated_client, test_user, test_counterparty, test_collection_with_item, test_session
    ):
        """Test that cancelling individual item sale doesn't put item back in collection."""
        collection, item = test_collection_with_item
        
        # Sell individual item (this removes it from collection)
        sale_data = {
            "counterparty_id": test_counterparty.id,
            "currency": "usd",
            "notes": "Test individual item sale for cancellation",
            "items": [
                {
                    "item_id": str(item.id),
                    "price": 10000,  # $100.00 in cents
                    "currency": "usd",
                    "notes": "Test individual item sale",
                }
            ],
        }

        create_response = authenticated_client.post("/api/transactions/sale", json=sale_data)
        assert create_response.status_code == status.HTTP_201_CREATED
        transaction_id = create_response.json()["id"]

        # Cancel transaction
        response = authenticated_client.post(f"/api/transactions/{transaction_id}/cancel")
        assert response.status_code == status.HTTP_200_OK

        # Verify item stays out of collection even after cancellation
        await test_session.commit()  # Refresh session
        item_result = await test_session.execute(
            select(Item).where(Item.id == item.id)
        )
        updated_item = item_result.scalar_one()
        assert updated_item.collection_id is None  # Item should still be out of collection

        # Verify SALE changed to CURRENT
        price_history_result = await test_session.execute(
            select(ItemPriceHistory).where(
                ItemPriceHistory.item_id == item.id,
                ItemPriceHistory.type == PriceType.CURRENT
            )
        )
        current_history = price_history_result.scalar_one()
        assert current_history.price == 10000
