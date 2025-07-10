import pytest
from httpx import AsyncClient
from utils.enums import PriceType
import datetime
from datetime import datetime, timezone, timedelta
import uuid


@pytest.mark.asyncio
async def test_create_and_get_price_history(authenticated_client, test_item):
    payload = {
        "price": 100.5,
        "price_type": "in"
    }

    item_id = str(test_item.id) if not isinstance(test_item.id, str) else test_item.id
    response = authenticated_client.post(f"/api/price-history/?item_id={item_id}", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["price"] == 100.5
    assert data["price_type"] == "in"
    # Get price history for item
    response = authenticated_client.get(f"/api/price-history/item/{item_id}")
    assert response.status_code == 200
    items = response.json()
    assert any(ph["price_type"] == "in" and ph["price"] == 100.5 for ph in items)


@pytest.mark.asyncio
async def test_full_price_history_cycle(authenticated_client, test_item):
    item_id = str(test_item.id) if not isinstance(test_item.id, str) else test_item.id

    # Simulate purchase (in)
    purchase_payload = {
        "price": 150.0,
        "price_type": "in",
        "timestamp": (datetime.now(timezone.utc) - timedelta(days=120)).isoformat()
    }
    resp = authenticated_client.post(f"/api/price-history/?item_id={item_id}", json=purchase_payload)
    assert resp.status_code == 200
    purchase_id = resp.json()["id"]

    # Simulate sale (out)
    sale_payload = {
        "price": 500.0,
        "price_type": "out",
        "timestamp": (datetime.now(timezone.utc) - timedelta(days=10)).isoformat()
    }
    resp = authenticated_client.post(f"/api/price-history/?item_id={item_id}", json=sale_payload)
    assert resp.status_code == 200
    sale_id = resp.json()["id"]

    # After OUT price, any new price history should be forbidden
    current_3mo_payload = {
        "price": 200.0,
        "price_type": "current",
        "timestamp": (datetime.now(timezone.utc) - timedelta(days=90)).isoformat()
    }
    resp = authenticated_client.post(f"/api/price-history/?item_id={item_id}", json=current_3mo_payload)
    assert resp.status_code == 403

    # Optionally, check that other types are also forbidden
    current_2mo_payload = {
        "price": 250.0,
        "price_type": "current",
        "timestamp": (datetime.now(timezone.utc) - timedelta(days=60)).isoformat()
    }
    resp = authenticated_client.post(f"/api/price-history/?item_id={item_id}", json=current_2mo_payload)
    assert resp.status_code == 403

    # Optionally, check that auction/old price is forbidden
    auction_payload = {
        "price": 3000.0,
        "price_type": "current",
        "timestamp": datetime(1992, 5, 20, 12, 0, 0, tzinfo=timezone.utc).isoformat()
    }
    resp = authenticated_client.post(f"/api/price-history/?item_id={item_id}", json=auction_payload)
    assert resp.status_code == 403

    # Get all price history for item
    resp = authenticated_client.get(f"/api/price-history/item/{item_id}")
    assert resp.status_code == 200
    items = resp.json()
    # Check only IN and OUT prices exist
    assert any(ph["price_type"] == "in" and ph["price"] == 150.0 for ph in items)
    assert any(ph["price_type"] == "out" and ph["price"] == 500.0 for ph in items)


@pytest.mark.asyncio
async def test_update_price_history(authenticated_client, test_item):
    item_id = str(test_item.id) if not isinstance(test_item.id, str) else test_item.id
    # Create price history record
    payload = {
        "price": 123.45,
        "price_type": "current"
    }
    resp = authenticated_client.post(f"/api/price-history/?item_id={item_id}", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    price_history_id = data["id"]
    # Update price, price_type, and timestamp
    update_payload = {
        "price": 543.21,
        "price_type": "out",
        "timestamp": "2020-01-01T12:00:00"
    }
    resp = authenticated_client.patch(f"/api/price-history/{price_history_id}", json=update_payload)
    assert resp.status_code == 200
    updated = resp.json()
    assert updated["price"] == 543.21
    assert updated["price_type"] == "out"
    assert updated["timestamp"].startswith("2020-01-01T12:00:00")


def test_create_price_history_for_nonexistent_item(authenticated_client):
    non_existent_id = str(uuid.uuid4())
    payload = {"price": 99.99, "price_type": "in"}
    resp = authenticated_client.post(f"/api/price-history/?item_id={non_existent_id}", json=payload)
    assert resp.status_code in (404, 422)  # depends on backend logic


def test_get_price_history_for_nonexistent_item(authenticated_client):
    non_existent_id = str(uuid.uuid4())
    resp = authenticated_client.get(f"/api/price-history/item/{non_existent_id}")
    assert resp.status_code == 404


def test_price_history_serialization(authenticated_client, test_item):
    payload = {"price": 123.45, "price_type": "current"}
    resp = authenticated_client.post(f"/api/price-history/?item_id={test_item.id}", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "id" in data
    assert "item_id" in data
    assert "price" in data
    assert "price_type" in data
    assert "timestamp" in data
    # Check timezone-aware
    assert data["timestamp"].endswith("+00:00")


def test_create_price_history_with_invalid_price_type(authenticated_client, test_item):
    payload = {"price": 10.0, "price_type": "invalid_type"}
    resp = authenticated_client.post(f"/api/price-history/?item_id={test_item.id}", json=payload)
    assert resp.status_code == 422


def test_create_price_history_missing_required_fields(authenticated_client, test_item):
    payload = {"price_type": "in"}  # no price
    resp = authenticated_client.post(f"/api/price-history/?item_id={test_item.id}", json=payload)
    assert resp.status_code == 422
    payload = {"price": 10.0}  # no price_type
    resp = authenticated_client.post(f"/api/price-history/?item_id={test_item.id}", json=payload)
    assert resp.status_code == 422


def test_forbid_timestamp_update_for_in_or_out(authenticated_client, test_item):
    item_id = str(test_item.id) if not isinstance(test_item.id, str) else test_item.id
    # Create IN price
    payload = {"price": 111.0, "price_type": "in"}
    resp = authenticated_client.post(f"/api/price-history/?item_id={item_id}", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    price_history_id = data["id"]
    # Try to update timestamp for IN price (with a different valid price and price_type)
    update_payload = {"price": 112.0, "price_type": "in", "timestamp": "2022-01-01T12:00:00"}
    resp = authenticated_client.patch(f"/api/price-history/{price_history_id}", json=update_payload)
    assert resp.status_code == 403

    # Create OUT price
    payload = {"price": 222.0, "price_type": "out"}
    resp = authenticated_client.post(f"/api/price-history/?item_id={item_id}", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    price_history_id = data["id"]
    # Try to update timestamp for OUT price (with a different valid price and price_type)
    update_payload = {"price": 223.0, "price_type": "out", "timestamp": "2023-01-01T12:00:00"}
    resp = authenticated_client.patch(f"/api/price-history/{price_history_id}", json=update_payload)
    assert resp.status_code == 403


def test_price_history_deleted_with_item(authenticated_client, test_item):
    item_id = str(test_item.id) if not isinstance(test_item.id, str) else test_item.id
    # Add price history records
    payloads = [
        {"price": 10.0, "price_type": "in"},
        {"price": 20.0, "price_type": "current"}
    ]
    for payload in payloads:
        resp = authenticated_client.post(f"/api/price-history/?item_id={item_id}", json=payload)
        assert resp.status_code == 200

    # Check price history exists
    resp = authenticated_client.get(f"/api/price-history/item/{item_id}")
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) == 2
    # Delete item
    resp = authenticated_client.delete(f"/api/items/{item_id}")
    assert resp.status_code == 204
    # Check price history is deleted
    resp = authenticated_client.get(f"/api/price-history/item/{item_id}")
    assert resp.status_code == 404
