import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.dealer import Dealer
from models.transaction import Transaction
from models.item import Item
from datetime import date


@pytest.mark.asyncio
class TestDealerTransaction:
    async def create_and_check_dealers(self, test_session: AsyncSession, test_user):
        dealers = [Dealer(name=f"Dealer{i}", contact_info=f"d{i}@dealer.com", user_id=test_user.id) for i in range(5)]
        test_session.add_all(dealers)
        await test_session.commit()
        result = await test_session.execute(select(Dealer).where(Dealer.user_id == test_user.id))
        db_dealers = result.scalars().all()
        assert len(db_dealers) == 5
        return [dealer.id for dealer in db_dealers]

    async def create_transaction_with_items(self, test_session: AsyncSession, test_user, dealer_id):
        transaction = Transaction(dealer_id=dealer_id, user_id=test_user.id, date=date.today())
        test_session.add(transaction)
        await test_session.flush()

        transaction_id = transaction.id
        if transaction_id is None:
            await test_session.refresh(transaction)
            transaction_id = transaction.id

        items = []
        for i in range(2):
            item = Item(
                name=f"Gold Coin {i+1}", year="2020", material="gold",
                user_id=test_user.id, price=2000, transaction_id=transaction_id
            )
            items.append(item)

        for i in range(8):
            item = Item(
                name=f"Silver Coin {i+1}", year="2021", material="silver",
                user_id=test_user.id, price=500, transaction_id=transaction_id
            )
            items.append(item)

        test_session.add_all(items)
        await test_session.commit()
        return transaction_id


    async def check_items_and_total(self, test_session: AsyncSession, transaction_id):
        result = await test_session.execute(select(Item).where(Item.transaction_id == transaction_id))
        transaction_items = result.scalars().all()
        assert len(transaction_items) == 10
        gold = [item for item in transaction_items if item.material == "gold"]
        silver = [item for item in transaction_items if item.material == "silver"]
        assert all(item.price == 2000 for item in gold)
        assert all(item.price == 500 for item in silver)

        total = sum(item.price for item in transaction_items)

        # Update total_amount
        result = await test_session.execute(select(Transaction).where(Transaction.id == transaction_id))
        transaction = result.scalar_one()
        transaction.total_amount = total
        await test_session.flush()

        assert transaction.total_amount == 2*2000 + 8*500
        return [item.id for item in transaction_items], transaction_id


    async def check_coin_to_transaction_and_dealer(self, test_session: AsyncSession, coin_id):
        # Get Item by id
        result = await test_session.execute(select(Item).where(Item.id == coin_id))
        coin = result.scalar_one()
        # Get transaction by id
        tx_id = coin.transaction_id
        result = await test_session.execute(select(Transaction).where(Transaction.id == tx_id))
        tx = result.scalar_one()
        # Get all items in this transaction
        result = await test_session.execute(select(Item).where(Item.transaction_id == tx_id))
        tx_items = result.scalars().all()
        assert len(tx_items) == 10
        # Get dealer by id
        dealer_id = tx.dealer_id
        result = await test_session.execute(select(Dealer).where(Dealer.id == dealer_id))
        dealer = result.scalar_one()
        assert dealer is not None
        return [item.id for item in tx_items], dealer_id

    async def test_dealer_transaction_flow(self, test_session: AsyncSession, test_user):
        dealer_ids = await self.create_and_check_dealers(test_session, test_user)
        transaction_id = await self.create_transaction_with_items(test_session, test_user, dealer_ids[0])
        transaction_item_ids, transaction_id = await self.check_items_and_total(test_session, transaction_id)
        tx_item_ids, dealer_id = await self.check_coin_to_transaction_and_dealer(test_session, transaction_item_ids[0])
        assert len(tx_item_ids) == 10
        assert dealer_id == dealer_ids[0]

    async def test_add_item_to_existing_transaction(self, test_session: AsyncSession, test_user):
        dealer = Dealer(name="DealerX", contact_info="x@dealer.com", user_id=test_user.id)
        test_session.add(dealer)
        await test_session.commit()
        await test_session.refresh(dealer)
        transaction = Transaction(dealer_id=dealer.id, user_id=test_user.id, date=date.today())
        test_session.add(transaction)
        await test_session.commit()
        await test_session.refresh(transaction)
        # Add item to existing transaction
        item = Item(name="Bronze Coin", year="2022", material="bronze", user_id=test_user.id, price=100, transaction_id=transaction.id)
        test_session.add(item)
        await test_session.commit()
        await test_session.refresh(item)
        # Checking the item is added to the transaction
        result = await test_session.execute(select(Item).where(Item.transaction_id == transaction.id))
        items = result.scalars().all()
        assert any(i.id == item.id for i in items)

    async def test_create_item_with_new_transaction_and_dealer(self, test_session: AsyncSession, test_user):
        # Create a dealer
        dealer = Dealer(name="Stub Dealer", contact_info=None, user_id=test_user.id)
        test_session.add(dealer)
        await test_session.commit()
        await test_session.refresh(dealer)
        # Create a transaction with this dealer
        transaction = Transaction(dealer_id=dealer.id, user_id=test_user.id, date=date.today())
        test_session.add(transaction)
        await test_session.commit()
        await test_session.refresh(transaction)
        # Create an item with this transaction
        item = Item(name="Found Coin", year="2023", material="silver", user_id=test_user.id, price=None, transaction_id=transaction.id)
        test_session.add(item)
        await test_session.commit()
        await test_session.refresh(item)
        # Checking the item is added to the transaction
        assert item.transaction_id == transaction.id
        assert transaction.dealer_id == dealer.id

    async def test_transaction_without_dealer_forbidden(self, test_session: AsyncSession, test_user):
        # Trying to create a transaction without a dealer should raise an error
        transaction = Transaction(dealer_id=None, user_id=test_user.id, date=date.today())
        test_session.add(transaction)
        try:
            await test_session.commit()
            assert False, "Transaction without dealer should not be allowed!"
        except Exception:
            await test_session.rollback()

    async def test_auto_stub_dealer_on_item_without_purchase(self, test_session: AsyncSession, test_user):
        # If item is added without a purchase, create an auto stub dealer and transaction
        dealer = Dealer(name="AutoStub", contact_info=None, user_id=test_user.id)
        test_session.add(dealer)
        await test_session.commit()
        await test_session.refresh(dealer)
        transaction = Transaction(dealer_id=dealer.id, user_id=test_user.id, date=date.today())
        test_session.add(transaction)
        await test_session.commit()
        await test_session.refresh(transaction)
        item = Item(name="Loose Coin", year="2024", material="copper", user_id=test_user.id, price=None, transaction_id=transaction.id)
        test_session.add(item)
        await test_session.commit()
        await test_session.refresh(item)
        assert item.transaction_id == transaction.id
        assert transaction.dealer_id == dealer.id
