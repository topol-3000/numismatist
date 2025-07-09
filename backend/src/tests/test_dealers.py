import pytest
from fastapi import status
from models.dealer import Dealer


@pytest.mark.asyncio
class TestDealersEndpoints:
    async def test_create_dealer(self, authenticated_client, test_user, test_session):
        data = {
            "name": "DealerTest",
            "email": "dealer@test.com",
            "phone": "+1234567890",
            "address": "123 Main St",
            "website": "https://dealer.com",
            "note": "My favorite dealer"
        }
        response = authenticated_client.post("/api/dealers/", json=data)
        assert response.status_code == status.HTTP_201_CREATED
        dealer = response.json()
        assert dealer["name"] == data["name"]
        assert dealer["email"] == data["email"]
        assert dealer["phone"] == data["phone"]
        assert dealer["address"] == data["address"]
        assert dealer["website"] == data["website"]
        assert dealer["note"] == data["note"]
        # Check in DB
        result = await test_session.execute(
            Dealer.__table__.select().where(Dealer.name == data["name"]))
        db_dealer = result.first()
        assert db_dealer is not None

    async def test_get_dealers(self, authenticated_client, test_user, test_session):
        dealer = Dealer(
            name="DealerList",
            email="list@test.com",
            phone=None,
            address=None,
            website=None,
            note=None,
            user_id=test_user.id
        )
        test_session.add(dealer)
        await test_session.commit()
        response = authenticated_client.get("/api/dealers/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert any(d["name"] == "DealerList" for d in data)

    async def test_get_dealer_by_id(self, authenticated_client, test_user, test_session):
        dealer = Dealer(name="DealerById", email=None, phone=None, address=None, website=None, note=None, user_id=test_user.id)
        test_session.add(dealer)
        await test_session.commit()
        await test_session.refresh(dealer)
        response = authenticated_client.get(f"/api/dealers/{dealer.id}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "DealerById"
        assert data["note"] is None

    async def test_update_dealer(self, authenticated_client, test_user, test_session):
        dealer = Dealer(name="DealerUpd", email=None, phone=None, address=None, website=None, note=None, user_id=test_user.id)
        test_session.add(dealer)
        await test_session.commit()
        await test_session.refresh(dealer)
        update = {
            "name": "DealerUpdated",
            "email": "upd@test.com",
            "phone": "+9876543210",
            "address": "456 New St",
            "website": "https://upd.com",
            "note": "Updated note"
        }
        response = authenticated_client.put(f"/api/dealers/{dealer.id}", json=update)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == update["name"]
        assert data["email"] == update["email"]
        assert data["phone"] == update["phone"]
        assert data["address"] == update["address"]
        assert data["website"] == update["website"]
        assert data["note"] == update["note"]

    async def test_delete_dealer(self, authenticated_client, test_user, test_session):
        dealer = Dealer(name="DealerDel", email=None, phone=None, address=None, website=None, note=None, user_id=test_user.id)
        test_session.add(dealer)
        await test_session.commit()
        await test_session.refresh(dealer)
        response = authenticated_client.delete(f"/api/dealers/{dealer.id}")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        # Check not in DB
        result = await test_session.execute(
            Dealer.__table__.select().where(Dealer.id == dealer.id))
        assert result.first() is None
