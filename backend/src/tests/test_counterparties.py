import pytest
from sqlalchemy import select

from models.counterparty import Counterparty


class TestCounterpartiesEndpoints:
    async def test_create_counterparty(self, authenticated_client, test_user, test_session):
        data = {
            "name": "CounterpartyTest",
            "role": "seller",
            "email": "counterparty@test.com",
            "phone": "555-1234",
            "address": "123 Test St",
            "website": "https://counterparty.com",
            "note": "My favorite counterparty"
        }
        response = authenticated_client.post("/api/counterparties/", json=data)
        assert response.status_code == 201
        counterparty = response.json()
        assert counterparty["name"] == data["name"]
        assert counterparty["role"] == data["role"]
        assert counterparty["email"] == data["email"]
        assert counterparty["phone"] == data["phone"]
        assert counterparty["address"] == data["address"]
        assert counterparty["website"] == data["website"]
        assert counterparty["note"] == data["note"]

        # Verify in database
        result = await test_session.execute(
            Counterparty.__table__.select().where(Counterparty.name == data["name"]))
        db_counterparty = result.first()
        assert db_counterparty is not None

    async def test_get_counterparties(self, authenticated_client, test_user, test_session):
        # First create a counterparty
        counterparty = Counterparty(name="Test Counterparty", user_id=test_user.id)
        test_session.add(counterparty)
        await test_session.commit()

        response = authenticated_client.get("/api/counterparties/")
        assert response.status_code == 200
        counterparties = response.json()
        assert len(counterparties) >= 1
        assert any(c["name"] == "Test Counterparty" for c in counterparties)

    async def test_get_counterparty(self, authenticated_client, test_user, test_session):
        # Create a counterparty
        counterparty = Counterparty(name="Test Counterparty", user_id=test_user.id)
        test_session.add(counterparty)
        await test_session.commit()
        await test_session.refresh(counterparty)

        response = authenticated_client.get(f"/api/counterparties/{counterparty.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == counterparty.id
        assert data["name"] == "Test Counterparty"

    async def test_update_counterparty(self, authenticated_client, test_user, test_session):
        # Create a counterparty
        counterparty = Counterparty(name="Test Counterparty", user_id=test_user.id)
        test_session.add(counterparty)
        await test_session.commit()
        await test_session.refresh(counterparty)

        update_data = {"name": "Updated Counterparty"}
        response = authenticated_client.put(f"/api/counterparties/{counterparty.id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Counterparty"

    async def test_delete_counterparty(self, authenticated_client, test_user, test_session):
        # Create a counterparty
        counterparty = Counterparty(name="Test Counterparty", user_id=test_user.id)
        test_session.add(counterparty)
        await test_session.commit()
        await test_session.refresh(counterparty)

        response = authenticated_client.delete(f"/api/counterparties/{counterparty.id}")
        assert response.status_code == 204

        # Verify it's deleted
        result = await test_session.execute(
            select(Counterparty).where(Counterparty.id == counterparty.id))
        assert result.scalar_one_or_none() is None
