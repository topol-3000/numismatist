"""Tests for collection transaction endpoints."""
import pytest
import pytest_asyncio
from fastapi import status
from sqlalchemy import select

from models import Collection, Counterparty, Item, ItemPriceHistory
from utils.enums import CounterpartyRole, PriceType


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
async def test_collection(test_session, test_user):
    """Create a test collection for transactions."""
    collection = Collection(
        name="Test Collection",
        description="Test collection for transactions",
        user_id=test_user.id,
    )
    test_session.add(collection)
    await test_session.commit()
    await test_session.refresh(collection)
    test_session.expunge(collection)
    return collection


@pytest_asyncio.fixture
async def test_collection_with_items(test_session, test_user):
    """Create a test collection with items."""
    # Create collection
    collection = Collection(
        name="Test Collection with Items",
        description="Test collection for transactions",
        user_id=test_user.id,
    )
    test_session.add(collection)
    await test_session.flush()  # Get ID without committing

    # Create some items for the collection
    items = []
    for i in range(3):
        item = Item(
            name=f"Collection Item {i+1}",
            year=2024,
            description=f"Test item {i+1} for collection transactions",
            material="silver",
            weight=31.1,
            user_id=test_user.id,
            collection_id=collection.id,
        )
        test_session.add(item)
        items.append(item)

    await test_session.commit()

    # Refresh all objects
    await test_session.refresh(collection)
    for item in items:
        await test_session.refresh(item)

    # Expunge objects so they can be used in test
    test_session.expunge(collection)
    for item in items:
        test_session.expunge(item)

    return collection, items


class TestCollectionTransactionsEndpoints:
    """Test collection transaction endpoints."""

    def test_purchase_collection(
        self, authenticated_client, test_user, test_counterparty, test_collection_with_items
    ):
        """Test POST /api/transactions/purchase-collection."""
        test_collection, items = test_collection_with_items

        purchase_data = {
            "counterparty_id": test_counterparty.id,
            "currency": "usd",
            "notes": "Test collection purchase",
            "collections": [
                {
                    "collection_id": str(test_collection.id),
                    "price": 30000,  # $300.00 in cents (will be distributed among 3 items)
                    "currency": "usd",
                    "notes": "Test collection purchase notes",
                }
            ],
        }

        response = authenticated_client.post("/api/transactions/purchase-collection", json=purchase_data)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["transaction_type"] == "purchase"
        assert data["status"] == "completed"
        assert data["currency"] == "usd"
        assert data["total_amount"] == 30000

    def test_sale_collection(
        self, authenticated_client, test_user, test_counterparty, test_collection_with_items
    ):
        """Test POST /api/transactions/sale-collection."""
        test_collection, items = test_collection_with_items

        sale_data = {
            "counterparty_id": test_counterparty.id,
            "currency": "usd",
            "notes": "Test collection sale",
            "collections": [
                {
                    "collection_id": str(test_collection.id),
                    "price": 45000,  # $450.00 in cents (will be distributed among 3 items)
                    "currency": "usd",
                    "notes": "Test collection sale notes",
                }
            ],
        }

        response = authenticated_client.post("/api/transactions/sale-collection", json=sale_data)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["transaction_type"] == "sale"
        assert data["status"] == "completed"
        assert data["currency"] == "usd"
        assert data["total_amount"] == 45000

    def test_purchase_collection_with_invalid_collection(
        self, authenticated_client, test_user, test_counterparty
    ):
        """Test POST /api/transactions/purchase-collection with invalid collection."""
        purchase_data = {
            "counterparty_id": test_counterparty.id,
            "currency": "usd",
            "notes": "Test purchase with invalid collection",
            "collections": [
                {
                    "collection_id": "invalid-collection-id",  # Non-existent collection
                    "price": 30000,
                    "currency": "usd",
                    "notes": "Test invalid collection purchase",
                }
            ],
        }

        response = authenticated_client.post("/api/transactions/purchase-collection", json=purchase_data)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_purchase_empty_collection(
        self, authenticated_client, test_user, test_counterparty, test_collection
    ):
        """Test POST /api/transactions/purchase-collection with empty collection."""
        purchase_data = {
            "counterparty_id": test_counterparty.id,
            "currency": "usd",
            "notes": "Test empty collection purchase",
            "collections": [
                {
                    "collection_id": str(test_collection.id),
                    "price": 30000,
                    "currency": "usd",
                    "notes": "Test empty collection purchase notes",
                }
            ],
        }

        response = authenticated_client.post("/api/transactions/purchase-collection", json=purchase_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_purchase_collection_with_invalid_counterparty(
        self, authenticated_client, test_user, test_collection_with_items
    ):
        """Test POST /api/transactions/purchase-collection with invalid counterparty."""
        test_collection, items = test_collection_with_items

        purchase_data = {
            "counterparty_id": 999999,  # Non-existent counterparty
            "currency": "usd",
            "notes": "Test purchase with invalid counterparty",
            "collections": [
                {
                    "collection_id": str(test_collection.id),
                    "price": 30000,
                    "currency": "usd",
                    "notes": "Test collection purchase notes",
                }
            ],
        }

        response = authenticated_client.post("/api/transactions/purchase-collection", json=purchase_data)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_sale_collection_with_invalid_counterparty(
        self, authenticated_client, test_user, test_collection_with_items
    ):
        """Test POST /api/transactions/sale-collection with invalid counterparty."""
        test_collection, items = test_collection_with_items

        sale_data = {
            "counterparty_id": 999999,  # Non-existent counterparty
            "currency": "usd",
            "notes": "Test sale with invalid counterparty",
            "collections": [
                {
                    "collection_id": str(test_collection.id),
                    "price": 45000,
                    "currency": "usd",
                    "notes": "Test collection sale notes",
                }
            ],
        }

        response = authenticated_client.post("/api/transactions/sale-collection", json=sale_data)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_collection_sale_cancellation(
        self, authenticated_client, test_user, test_counterparty, test_collection_with_items, test_session
    ):
        """Test that cancelling collection sale changes COLLECTION_SALE to CURRENT in price history."""
        collection, items = test_collection_with_items
        
        # Sell collection
        sale_data = {
            "counterparty_id": test_counterparty.id,
            "currency": "usd",
            "notes": "Test collection sale for cancellation",
            "collections": [
                {
                    "collection_id": str(collection.id),
                    "price": 30000,  # $300.00 in cents
                    "currency": "usd",
                    "notes": "Test collection sale",
                }
            ],
        }

        create_response = authenticated_client.post(
            "/api/transactions/sale-collection", json=sale_data
        )
        assert create_response.status_code == status.HTTP_201_CREATED
        transaction_id = create_response.json()["id"]

        # Cancel transaction
        response = authenticated_client.post(f"/api/transactions/{transaction_id}/cancel")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "cancelled"

        # Verify COLLECTION_SALE changed to CURRENT
        await test_session.commit()  # Refresh session
        price_history_result = await test_session.execute(
            select(ItemPriceHistory).where(
                ItemPriceHistory.item_id.in_([item.id for item in items]),
                ItemPriceHistory.type == PriceType.CURRENT
            )
        )
        current_histories = list(price_history_result.scalars().all())
        assert len(current_histories) == 3  # All COLLECTION_SALE should be changed to CURRENT
