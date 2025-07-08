import pytest
from fastapi import status
from datetime import date


class TestTransactionsAPI:
    """API tests for /api/transactions/ endpoints (full CRUD)."""

    def test_create_and_get_transaction(self, authenticated_client, test_user):
        dealer_data = {"name": "Dealer CRUD", "contact_info": "crud@dealer.com"}
        dealer_resp = authenticated_client.post("/api/dealers/", json=dealer_data)
        dealer_id = dealer_resp.json()["id"]
        item_data = {"name": "CRUD Coin", "year": "2025", "material": "gold"}
        item_resp = authenticated_client.post("/api/items/", json=item_data)
        item_id = item_resp.json()["id"]
        tx_data = {
            "dealer_id": dealer_id,
            "date": str(date.today()),
            "total_amount": 100,
            "items": [
                {"item_id": item_id, "price": 100}
            ]
        }
        tx_resp = authenticated_client.post("/api/transactions/", json=tx_data)
        assert tx_resp.status_code == status.HTTP_201_CREATED
        tx = tx_resp.json()
        tx_id = tx["id"]
        get_resp = authenticated_client.get(f"/api/transactions/?transaction_id={tx_id}")
        assert get_resp.status_code == status.HTTP_200_OK
        data = get_resp.json()
        if isinstance(data, list):
            assert len(data) == 1
            data = data[0]
        assert data["id"] == tx_id
        assert data["dealer_id"] == dealer_id
        assert len(data["transaction_items"]) == 1

    def test_patch_transaction(self, authenticated_client, test_user):
        dealer_data = {"name": "PatchDealer", "contact_info": "patch@dealer.com"}
        dealer_resp = authenticated_client.post("/api/dealers/", json=dealer_data)
        dealer_id = dealer_resp.json()["id"]
        item1_data = {"name": "PatchCoin1", "year": "2020", "material": "gold"}
        item2_data = {"name": "PatchCoin2", "year": "2021", "material": "silver"}
        item1_resp = authenticated_client.post("/api/items/", json=item1_data)
        item2_resp = authenticated_client.post("/api/items/", json=item2_data)
        item1_id = item1_resp.json()["id"]
        item2_id = item2_resp.json()["id"]
        tx_data = {
            "dealer_id": dealer_id,
            "date": str(date.today()),
            "total_amount": 100,
            "items": [
                {"item_id": item1_id, "price": 100}
            ]
        }
        tx_resp = authenticated_client.post("/api/transactions/", json=tx_data)
        tx_id = tx_resp.json()["id"]
        patch_data = {
            "dealer_id": dealer_id,
            "date": str(date.today()),
            "total_amount": 200,
            "items": [
                {"item_id": item2_id, "price": 200}
            ]
        }
        patch_resp = authenticated_client.patch(f"/api/transactions/{tx_id}", json=patch_data)
        assert patch_resp.status_code == status.HTTP_200_OK
        patched = patch_resp.json()
        assert patched["total_amount"] == 200
        assert len(patched["transaction_items"]) == 1
        assert patched["transaction_items"][0]["item_id"] == item2_id
        assert patched["transaction_items"][0]["price"] == 200

    def test_delete_transaction(self, authenticated_client, test_user):
        dealer_data = {"name": "DeleteDealer", "contact_info": "delete@dealer.com"}
        dealer_resp = authenticated_client.post("/api/dealers/", json=dealer_data)
        dealer_id = dealer_resp.json()["id"]
        item_data = {"name": "DeleteCoin", "year": "2022", "material": "bronze"}
        item_resp = authenticated_client.post("/api/items/", json=item_data)
        item_id = item_resp.json()["id"]
        tx_data = {
            "dealer_id": dealer_id,
            "date": str(date.today()),
            "total_amount": 100,
            "items": [
                {"item_id": item_id, "price": 100}
            ]
        }
        tx_resp = authenticated_client.post("/api/transactions/", json=tx_data)
        tx_id = tx_resp.json()["id"]
        del_resp = authenticated_client.delete(f"/api/transactions/{tx_id}")
        assert del_resp.status_code == status.HTTP_204_NO_CONTENT
        get_resp = authenticated_client.get(f"/api/transactions/?transaction_id={tx_id}")
        if get_resp.status_code == status.HTTP_404_NOT_FOUND:
            assert True
        else:
            data = get_resp.json()
            assert isinstance(data, list)
            assert len(data) == 0

    def test_create_transaction_auto_total_amount(self, authenticated_client, test_user):
        dealer_data = {"name": "AutoTotal Dealer", "contact_info": "auto@dealer.com"}
        dealer_resp = authenticated_client.post("/api/dealers/", json=dealer_data)
        dealer_id = dealer_resp.json()["id"]
        item1_data = {"name": "AutoTotal Coin1", "year": "2022", "material": "gold"}
        item2_data = {"name": "AutoTotal Coin2", "year": "2023", "material": "silver"}
        item1_resp = authenticated_client.post("/api/items/", json=item1_data)
        item2_resp = authenticated_client.post("/api/items/", json=item2_data)
        item1_id = item1_resp.json()["id"]
        item2_id = item2_resp.json()["id"]
        tx_data = {
            "dealer_id": dealer_id,
            "date": str(date.today()),
            "items": [
                {"item_id": item1_id, "price": 150.5},
                {"item_id": item2_id, "price": 249.5}
            ]
        }
        tx_resp = authenticated_client.post("/api/transactions/", json=tx_data)
        assert tx_resp.status_code == status.HTTP_201_CREATED
        tx = tx_resp.json()
        assert abs(tx["total_amount"] - 400.0) < 0.01
        assert len(tx["transaction_items"]) == 2
        prices = sorted([ti["price"] for ti in tx["transaction_items"]])
        assert prices == [150.5, 249.5]

    def test_create_transaction_with_new_item(self, authenticated_client, test_user):
        dealer_data = {"name": "Dealer New Coin", "contact_info": "newcoin@dealer.com"}
        dealer_resp = authenticated_client.post("/api/dealers/", json=dealer_data)
        dealer_id = dealer_resp.json()["id"]
        tx_data = {
            "dealer_id": dealer_id,
            "date": str(date.today()),
            "total_amount": 1234,
            "items": [
                {
                    "name": "Brand New Coin",
                    "year": "2025",
                    "material": "gold",
                    "price": 1234
                }
            ]
        }
        tx_resp = authenticated_client.post("/api/transactions/", json=tx_data)
        assert tx_resp.status_code == status.HTTP_201_CREATED
        tx = tx_resp.json()
        assert tx["dealer_id"] == dealer_id
        assert len(tx["transaction_items"]) == 1
        item_id = tx["transaction_items"][0]["item_id"]
        assert isinstance(item_id, str)
        assert tx["transaction_items"][0]["price"] == 1234

    def test_create_transaction_with_existing_and_new_items(self, authenticated_client, test_user):
        dealer_data = {"name": "Dealer Mixed", "contact_info": "mixed@dealer.com"}
        dealer_resp = authenticated_client.post("/api/dealers/", json=dealer_data)
        dealer_id = dealer_resp.json()["id"]
        item_data = {"name": "Existing Coin", "year": "2024", "material": "silver"}
        item_resp = authenticated_client.post("/api/items/", json=item_data)
        item_id = item_resp.json()["id"]
        tx_data = {
            "dealer_id": dealer_id,
            "date": str(date.today()),
            "total_amount": 2000,
            "items": [
                {
                    "item_id": item_id,
                    "price": 1000
                },
                {
                    "name": "Brand New Coin 2",
                    "year": "2025",
                    "material": "gold",
                    "price": 1000
                }
            ]
        }
        tx_resp = authenticated_client.post("/api/transactions/", json=tx_data)
        assert tx_resp.status_code == status.HTTP_201_CREATED
        tx = tx_resp.json()
        assert tx["dealer_id"] == dealer_id
        assert len(tx["transaction_items"]) == 2
        item_ids = [ti["item_id"] for ti in tx["transaction_items"]]
        assert item_id in item_ids
        assert any(isinstance(iid, str) and iid != item_id for iid in item_ids)

    def test_create_transaction_with_type(self, authenticated_client, test_user):
        dealer_data = {"name": "Type Dealer", "contact_info": "type@dealer.com"}
        dealer_resp = authenticated_client.post("/api/dealers/", json=dealer_data)
        dealer_id = dealer_resp.json()["id"]
        item_data = {"name": "Type Coin", "year": "2025", "material": "gold"}
        item_resp = authenticated_client.post("/api/items/", json=item_data)
        item_id = item_resp.json()["id"]
        tx_data = {
            "dealer_id": dealer_id,
            "date": str(date.today()),
            "total_amount": 123,
            "type": "gift",
            "items": [
                {"item_id": item_id, "price": 123}
            ]
        }
        tx_resp = authenticated_client.post("/api/transactions/", json=tx_data)
        assert tx_resp.status_code == status.HTTP_201_CREATED
        tx = tx_resp.json()
        assert tx["type"] == "gift"
        tx_data2 = {
            "dealer_id": dealer_id,
            "date": str(date.today()),
            "total_amount": 111,
            "items": [
                {"item_id": item_id, "price": 111}
            ]
        }
        tx_resp2 = authenticated_client.post("/api/transactions/", json=tx_data2)
        assert tx_resp2.status_code == status.HTTP_201_CREATED
        tx2 = tx_resp2.json()
        assert tx2["type"] == "purchase"
