import pytest
from fastapi import status
from datetime import date


class TestDealersAPI:
    """API tests for /api/dealers/ endpoints (private per user), including integration with items and transactions."""

    def test_create_and_list_dealers(self, authenticated_client, test_user):
        # Create dealer
        dealer_data = {"name": "Test Dealer", "contact_info": "test@dealer.com"}
        response = authenticated_client.post("/api/dealers/", json=dealer_data)
        assert response.status_code == status.HTTP_201_CREATED
        dealer = response.json()
        assert dealer["name"] == dealer_data["name"]
        assert dealer["contact_info"] == dealer_data["contact_info"]
        assert dealer["user_id"] == test_user.id
        # List dealers
        response = authenticated_client.get("/api/dealers/")
        assert response.status_code == status.HTTP_200_OK
        dealers = response.json()
        assert any(d["name"] == dealer_data["name"] for d in dealers)

    def test_get_dealer_by_id(self, authenticated_client, test_user):
        # Create dealer
        dealer_data = {"name": "Dealer By ID", "contact_info": "id@dealer.com"}
        response = authenticated_client.post("/api/dealers/", json=dealer_data)
        dealer = response.json()
        dealer_id = dealer["id"]
        # Get by id
        response = authenticated_client.get(f"/api/dealers/{dealer_id}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == dealer_id
        assert data["name"] == dealer_data["name"]

    def test_update_dealer(self, authenticated_client, test_user):
        # Create dealer
        dealer_data = {"name": "Dealer To Update", "contact_info": "old@dealer.com"}
        response = authenticated_client.post("/api/dealers/", json=dealer_data)
        dealer = response.json()
        dealer_id = dealer["id"]
        # Update
        update_data = {"contact_info": "new@dealer.com"}
        response = authenticated_client.patch(f"/api/dealers/{dealer_id}", json=update_data)
        assert response.status_code == status.HTTP_200_OK
        updated = response.json()
        assert updated["contact_info"] == update_data["contact_info"]

    def test_delete_dealer(self, authenticated_client, test_user):
        # Create dealer
        dealer_data = {"name": "Dealer To Delete", "contact_info": "del@dealer.com"}
        response = authenticated_client.post("/api/dealers/", json=dealer_data)
        dealer = response.json()
        dealer_id = dealer["id"]
        # Delete
        response = authenticated_client.delete(f"/api/dealers/{dealer_id}")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        # Check not found
        response = authenticated_client.get(f"/api/dealers/{dealer_id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_dealer_transaction_and_items_flow(self, authenticated_client, test_user):
        # 1. Create a dealer
        dealer_data = {"name": "Flow Dealer", "contact_info": "flow@dealer.com"}
        dealer_resp = authenticated_client.post("/api/dealers/", json=dealer_data)
        assert dealer_resp.status_code == status.HTTP_201_CREATED
        dealer = dealer_resp.json()
        dealer_id = dealer["id"]

        # 2. Create items
        item1 = {"name": "Coin1", "year": "2024", "material": "gold"}
        item2 = {"name": "Coin2", "year": "2023", "material": "silver"}
        item1_resp = authenticated_client.post("/api/items/", json=item1)
        item2_resp = authenticated_client.post("/api/items/", json=item2)
        assert item1_resp.status_code == status.HTTP_201_CREATED
        assert item2_resp.status_code == status.HTTP_201_CREATED
        item1_id = item1_resp.json()["id"]
        item2_id = item2_resp.json()["id"]

        # 3. Create a transaction with these items
        transaction_data = {
            "dealer_id": dealer_id,
            "date": "2025-07-05",
            "items": [
                {"item_id": item1_id, "price": 1000},
                {"item_id": item2_id, "price": 500}
            ]
        }
        tx_resp = authenticated_client.post("/api/transactions/", json=transaction_data)
        assert tx_resp.status_code == status.HTTP_201_CREATED
        tx = tx_resp.json()
        assert tx["dealer_id"] == dealer_id
        assert len(tx["transaction_items"]) == 2
        for ti in tx["transaction_items"]:
            assert "item_id" in ti and "price" in ti

        # 4. Get the list of transactions and check that our transaction is present
        tx_list_resp = authenticated_client.get("/api/transactions/")
        assert tx_list_resp.status_code == status.HTTP_200_OK
        tx_list = tx_list_resp.json()
        assert any(t["id"] == tx["id"] for t in tx_list)

        # 5. Get transaction details and check sales/purchases data
        tx_detail_resp = authenticated_client.get(f"/api/transactions/?transaction_id={tx['id']}")
        assert tx_detail_resp.status_code == status.HTTP_200_OK
        tx_detail = tx_detail_resp.json()
        if isinstance(tx_detail, list):
            assert len(tx_detail) == 1
            tx_detail = tx_detail[0]

        assert tx_detail["dealer_id"] == dealer_id
        assert len(tx_detail["transaction_items"]) == 2
        item_ids = {ti["item_id"] for ti in tx_detail["transaction_items"]}
        assert item1_id in item_ids and item2_id in item_ids
        prices = {ti["price"] for ti in tx_detail["transaction_items"]}
        assert 1000 in prices and 500 in prices
        item1_price = next(ti["price"] for ti in tx_detail["transaction_items"] if ti["item_id"] == item1_id)
        assert item1_price == 1000

    def test_item_price_after_purchase(self, authenticated_client, test_user):
        # Create dealer
        dealer_data = {"name": "Dealer Price Test", "contact_info": "price@dealer.com"}
        dealer_resp = authenticated_client.post("/api/dealers/", json=dealer_data)
        dealer = dealer_resp.json()
        dealer_id = dealer["id"]
        # Create item
        item_data = {"name": "CoinPrice", "year": "2025", "material": "gold"}
        item_resp = authenticated_client.post("/api/items/", json=item_data)
        assert item_resp.status_code == status.HTTP_201_CREATED
        item_id = item_resp.json()["id"]
        # Create transaction with this item
        transaction_data = {
            "dealer_id": dealer_id,
            "date": "2025-07-05",
            "items": [
                {"item_id": item_id, "price": 777}
            ]
        }
        tx_resp = authenticated_client.post("/api/transactions/", json=transaction_data)
        assert tx_resp.status_code == status.HTTP_201_CREATED
        tx = tx_resp.json()
        tx_id = tx["id"]
        # Get transaction details and check item price
        tx_detail_resp = authenticated_client.get(f"/api/transactions/?transaction_id={tx_id}")
        assert tx_detail_resp.status_code == status.HTTP_200_OK
        tx_detail = tx_detail_resp.json()
        if isinstance(tx_detail, list):
            assert len(tx_detail) == 1
            tx_detail = tx_detail[0]
        item_price = next(ti["price"] for ti in tx_detail["transaction_items"] if ti["item_id"] == item_id)
        assert item_price == 777

def test_create_transaction_with_new_dealer(authenticated_client, test_user):
    tx_data = {
        "dealer_data": {"name": "Auto Dealer", "contact_info": "auto@dealer.com"},
        "date": str(date.today()),
        "total_amount": 555,
        "items": [
            {
                "name": "Auto Coin",
                "year": "2025",
                "material": "gold",
                "price": 555
            }
        ]
    }
    tx_resp = authenticated_client.post("/api/transactions/", json=tx_data)
    assert tx_resp.status_code == status.HTTP_201_CREATED
    tx = tx_resp.json()
    assert tx["dealer_id"] is not None
    assert tx["total_amount"] == 555 or tx["total_amount"] is None
    assert len(tx["transaction_items"]) == 1
    assert tx["transaction_items"][0]["price"] == 555

def test_create_transaction_with_existing_dealer(authenticated_client, test_user):
    dealer_data = {"name": "Existing Dealer", "contact_info": "exist@dealer.com"}
    dealer_resp = authenticated_client.post("/api/dealers/", json=dealer_data)
    dealer_id = dealer_resp.json()["id"]
    tx_data = {
        "dealer_id": dealer_id,
        "date": str(date.today()),
        "total_amount": 777,
        "items": [
            {
                "name": "Coin with Existing Dealer",
                "year": "2025",
                "material": "silver",
                "price": 777
            }
        ]
    }
    tx_resp = authenticated_client.post("/api/transactions/", json=tx_data)
    assert tx_resp.status_code == status.HTTP_201_CREATED
    tx = tx_resp.json()
    assert tx["dealer_id"] == dealer_id
    assert len(tx["transaction_items"]) == 1
    assert tx["transaction_items"][0]["price"] == 777
