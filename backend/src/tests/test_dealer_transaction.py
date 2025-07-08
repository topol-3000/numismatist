import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.dealer import Dealer
from models.transaction import Transaction
from models.item import Item
from models.transaction_item import TransactionItem
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
        transaction_items = []
        for i in range(2):
            item = Item(
                name=f"Gold Coin {i+1}", year="2020", material="gold",
                user_id=test_user.id
            )
            items.append(item)
        for i in range(8):
            item = Item(
                name=f"Silver Coin {i+1}", year="2021", material="silver",
                user_id=test_user.id
            )
            items.append(item)
        test_session.add_all(items)
        await test_session.flush()
        # Create a TransactionItem for each coin
        for item in items[:2]:
            transaction_items.append(TransactionItem(transaction_id=transaction_id, item_id=item.id, price=2000))
        for item in items[2:]:
            transaction_items.append(TransactionItem(transaction_id=transaction_id, item_id=item.id, price=500))
        test_session.add_all(transaction_items)
        await test_session.commit()
        return transaction_id

    async def check_items_and_total(self, test_session: AsyncSession, transaction_id):
        result = await test_session.execute(select(TransactionItem).where(TransactionItem.transaction_id == transaction_id))
        transaction_items = result.scalars().all()
        assert len(transaction_items) == 10
        gold = [ti for ti in transaction_items if ti.price == 2000]
        silver = [ti for ti in transaction_items if ti.price == 500]
        assert len(gold) == 2
        assert len(silver) == 8
        total = sum(ti.price for ti in transaction_items)
        # Update total_amount
        result = await test_session.execute(select(Transaction).where(Transaction.id == transaction_id))
        transaction = result.scalar_one()
        transaction.total_amount = total
        await test_session.flush()
        assert transaction.total_amount == 2*2000 + 8*500
        return [ti.item_id for ti in transaction_items], transaction_id

    async def check_coin_to_transaction_and_dealer(self, test_session: AsyncSession, coin_id):
        # Get TransactionItem by item_id
        result = await test_session.execute(select(TransactionItem).where(TransactionItem.item_id == coin_id))
        ti = result.scalar_one()
        tx_id = ti.transaction_id
        result = await test_session.execute(select(Transaction).where(Transaction.id == tx_id))
        tx = result.scalar_one()
        # Get all TransactionItems in this transaction
        result = await test_session.execute(select(TransactionItem).where(TransactionItem.transaction_id == tx_id))
        tx_items = result.scalars().all()
        assert len(tx_items) == 10
        # Get dealer by id
        dealer_id = tx.dealer_id
        result = await test_session.execute(select(Dealer).where(Dealer.id == dealer_id))
        dealer = result.scalar_one()
        assert dealer is not None
        return [ti.item_id for ti in tx_items], dealer_id

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
        await test_session.flush()
        dealer_id = dealer.id
        await test_session.commit()

        transaction = Transaction(dealer_id=dealer_id, user_id=test_user.id, date=date.today())
        test_session.add(transaction)
        await test_session.flush()
        transaction_id = transaction.id
        await test_session.commit()

        item = Item(name="Bronze Coin", year="2022", material="bronze", user_id=test_user.id)
        test_session.add(item)
        await test_session.flush()
        item_id = item.id

        ti = TransactionItem(transaction_id=transaction_id, item_id=item_id, price=100)
        test_session.add(ti)
        await test_session.commit()

        # Check via explicit select
        result = await test_session.execute(select(TransactionItem).where(TransactionItem.transaction_id == transaction_id))
        items = result.scalars().all()
        assert any(ti.item_id == item_id for ti in items)

    async def test_create_item_with_new_transaction_and_dealer(self, test_session: AsyncSession, test_user):
        dealer = Dealer(name="Stub Dealer", contact_info=None, user_id=test_user.id)
        test_session.add(dealer)
        await test_session.flush()
        dealer_id = dealer.id
        await test_session.commit()

        transaction = Transaction(dealer_id=dealer_id, user_id=test_user.id, date=date.today())
        test_session.add(transaction)
        await test_session.flush()
        transaction_id = transaction.id
        await test_session.commit()

        item = Item(name="Found Coin", year="2023", material="silver", user_id=test_user.id)
        test_session.add(item)
        await test_session.flush()
        item_id = item.id

        ti = TransactionItem(transaction_id=transaction_id, item_id=item_id, price=123)
        test_session.add(ti)
        await test_session.flush()
        ti_id = ti.id
        await test_session.commit()

        # Check via explicit select
        result = await test_session.execute(select(TransactionItem).where(TransactionItem.id == ti_id))
        ti_db = result.scalar_one()
        assert ti_db.transaction_id == transaction_id

        result = await test_session.execute(select(Transaction).where(Transaction.id == transaction_id))
        transaction_db = result.scalar_one()
        assert transaction_db.dealer_id == dealer_id

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
        dealer = Dealer(name="AutoStub", contact_info=None, user_id=test_user.id)
        test_session.add(dealer)
        await test_session.flush()
        dealer_id = dealer.id
        await test_session.commit()

        transaction = Transaction(dealer_id=dealer_id, user_id=test_user.id, date=date.today())
        test_session.add(transaction)
        await test_session.flush()
        transaction_id = transaction.id
        await test_session.commit()

        item = Item(name="Loose Coin", year="2024", material="copper", user_id=test_user.id)
        test_session.add(item)
        await test_session.flush()
        item_id = item.id

        ti = TransactionItem(transaction_id=transaction_id, item_id=item_id, price=0)
        test_session.add(ti)
        await test_session.flush()
        ti_id = ti.id
        await test_session.commit()

        # Check via explicit select
        result = await test_session.execute(select(TransactionItem).where(TransactionItem.id == ti_id))
        ti_db = result.scalar_one()
        assert ti_db.transaction_id == transaction_id

        result = await test_session.execute(select(Transaction).where(Transaction.id == transaction_id))
        transaction_db = result.scalar_one()
        assert transaction_db.dealer_id == dealer_id
