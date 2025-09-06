from datetime import datetime
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from api.dependency.database import SessionDependency
from api.routes.fastapi_users import current_active_user
from models import (
    Collection,
    Counterparty,
    Item,
    ItemPriceHistory,
    Transaction,
    TransactionCollection,
    TransactionItem,
    User,
)
from schemas.transaction import TransactionRead
from schemas.transaction_item import TransactionItemCreate, TransactionItemRead
from utils.enums import Currency, PriceType, TransactionStatus, TransactionType

router = APIRouter(prefix="/transactions", tags=["Transactions"])


class TransactionCollectionItem(BaseModel):
    """Schema for collection item in transaction requests."""

    collection_id: Annotated[str, Field(description="ID of the collection")]
    price: Annotated[int, Field(ge=0, description="Collection price in cents")]
    currency: Annotated[Currency, Field(description="Currency of the collection price")]
    notes: Annotated[str | None, Field(description="Optional notes about this collection")] = None


class TransactionPurchaseRequest(BaseModel):
    """Request schema for purchasing items."""

    counterparty_id: Annotated[int, Field(description="ID of the counterparty")]
    items: Annotated[list[TransactionItemCreate], Field(description="List of items to purchase")]
    currency: Annotated[Currency, Field(description="Currency of the transaction")] = Currency.USD
    notes: Annotated[str | None, Field(description="Optional notes about the transaction")] = None
    transaction_date: Annotated[datetime | None, Field(description="Date and time of transaction")] = None


class TransactionCollectionPurchaseRequest(BaseModel):
    """Request schema for purchasing collections."""

    counterparty_id: Annotated[int, Field(description="ID of the counterparty")]
    collections: Annotated[list[TransactionCollectionItem], Field(description="List of collections to purchase")]
    currency: Annotated[Currency, Field(description="Currency of the transaction")] = Currency.USD
    notes: Annotated[str | None, Field(description="Optional notes about the transaction")] = None
    transaction_date: Annotated[datetime | None, Field(description="Date and time of transaction")] = None


class TransactionSaleRequest(BaseModel):
    """Request schema for selling items."""

    counterparty_id: Annotated[int, Field(description="ID of the counterparty")]
    items: Annotated[list[TransactionItemCreate], Field(description="List of items to sell")]
    currency: Annotated[Currency, Field(description="Currency of the transaction")] = Currency.USD
    notes: Annotated[str | None, Field(description="Optional notes about the transaction")] = None
    transaction_date: Annotated[datetime | None, Field(description="Date and time of transaction")] = None


class TransactionCollectionSaleRequest(BaseModel):
    """Request schema for selling collections."""

    counterparty_id: Annotated[int, Field(description="ID of the counterparty")]
    collections: Annotated[list[TransactionCollectionItem], Field(description="List of collections to sell")]
    currency: Annotated[Currency, Field(description="Currency of the transaction")] = Currency.USD
    notes: Annotated[str | None, Field(description="Optional notes about the transaction")] = None
    transaction_date: Annotated[datetime | None, Field(description="Date and time of transaction")] = None


async def verify_counterparty_ownership(
    counterparty_id: int,
    session: AsyncSession,
    user: User,
) -> Counterparty:
    """Verify that the counterparty belongs to the current user."""
    result: Result[Any] = await session.execute(
        select(Counterparty).where(
            Counterparty.id == counterparty_id,
            Counterparty.user_id == user.id,
        )
    )
    counterparty = result.scalar_one_or_none()

    if not counterparty:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Counterparty not found")

    return counterparty


async def verify_items_ownership(
    item_ids: list[str],
    session: AsyncSession,
    user: User,
) -> list[Item]:
    """Verify that all items belong to the current user."""
    result: Result[Any] = await session.execute(
        select(Item).where(
            Item.id.in_(item_ids),
            Item.user_id == user.id,
        )
    )
    items = list(result.scalars().all())

    if len(items) != len(item_ids):
        found_ids = {item.id for item in items}
        missing_ids = set(item_ids) - found_ids
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Items not found: {', '.join(missing_ids)}")

    return items


async def verify_collections_ownership(
    collection_ids: list[str],
    session: AsyncSession,
    user: User,
) -> list[Collection]:
    """Verify that all collections belong to the current user."""
    result: Result[Any] = await session.execute(
        select(Collection).where(
            Collection.id.in_(collection_ids),
            Collection.user_id == user.id,
        )
    )
    collections = list(result.scalars().all())

    if len(collections) != len(collection_ids):
        found_ids = {collection.id for collection in collections}
        missing_ids = set(collection_ids) - found_ids
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Collections not found: {', '.join(missing_ids)}"
        )

    return collections


async def distribute_collection_price_to_items(
    collection: Collection,
    total_price: int,
    currency: Currency,
    session: AsyncSession,
) -> list[tuple[Item, int]]:
    """
    Distribute collection price evenly among all items in the collection and its descendants.
    For hierarchical collections, gets all items from all descendant collections.
    Returns list of (item, price_per_item) tuples.
    """
    from sqlalchemy import select

    from models.item import Item

    # Get all items from this collection and all its descendants
    async def get_all_descendant_items(coll: Collection) -> list[Item]:
        """Recursively get all items from collection and its descendants."""
        all_items = []

        # Get direct items of this collection
        items_stmt = select(Item).where(Item.collection_id == coll.id)
        result = await session.execute(items_stmt)
        direct_items = list(result.scalars().all())
        all_items.extend(direct_items)

        # Get items from child collections recursively
        children_stmt = select(Collection).where(Collection.parent_id == coll.id)
        children_result = await session.execute(children_stmt)
        children = list(children_result.scalars().all())

        for child in children:
            child_items = await get_all_descendant_items(child)
            all_items.extend(child_items)

        return all_items

    all_items = await get_all_descendant_items(collection)

    if not all_items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Collection '{collection.name}' and its descendants have no items to distribute price to",
        )

    # Distribute price evenly (integer division)
    items_count = len(all_items)
    price_per_item = total_price // items_count
    remainder = total_price % items_count

    # Distribute the remainder among first few items to ensure total matches
    item_prices = []
    for i, item in enumerate(all_items):
        item_price = price_per_item + (1 if i < remainder else 0)
        item_prices.append((item, item_price))

    return item_prices


async def create_hierarchical_transaction_collections(
    root_collection: Collection,
    transaction_id: str,
    total_price: int,
    currency: Currency,
    session: AsyncSession,
    parent_tc_id: int | None = None,
) -> list[TransactionCollection]:
    """
    Create hierarchical TransactionCollection records for a collection and its descendants.
    Returns list of all created TransactionCollection objects.
    """
    from sqlalchemy import select

    # Create TransactionCollection for current collection
    # For root collection, use total_price. For children, calculate proportional price
    collection_price = total_price
    if parent_tc_id is not None:
        # For child collections, we'll distribute parent's price proportionally
        # This is a simplified approach - you might want more sophisticated pricing logic
        collection_price = 0  # Will be set by parent's price distribution

    transaction_collection = TransactionCollection(
        transaction_id=transaction_id,
        collection_id=root_collection.id,
        price=collection_price,
        currency=currency,
        parent_transaction_collection_id=parent_tc_id,
    )

    session.add(transaction_collection)
    await session.flush()  # Get the ID

    transaction_collections = [transaction_collection]

    # Get child collections
    children_stmt = select(Collection).where(Collection.parent_id == root_collection.id)
    children_result = await session.execute(children_stmt)
    children = list(children_result.scalars().all())

    # Recursively create TransactionCollections for children
    for child in children:
        child_tcs = await create_hierarchical_transaction_collections(
            child,
            transaction_id,
            0,  # Child price will be calculated during item distribution
            currency,
            session,
            transaction_collection.id,
        )
        transaction_collections.extend(child_tcs)

    return transaction_collections


@router.post("/purchase", response_model=TransactionRead, status_code=status.HTTP_201_CREATED)
async def purchase_items(
    purchase_data: TransactionPurchaseRequest,
    session: SessionDependency,
    current_user: User = Depends(current_active_user),
) -> Transaction:
    """Purchase items from a counterparty."""

    # Validate counterparty
    counterparty = await verify_counterparty_ownership(
        purchase_data.counterparty_id,
        session,
        current_user,
    )

    # Validate items
    item_ids = [item.item_id for item in purchase_data.items]
    await verify_items_ownership(item_ids, session, current_user)

    # Calculate total amount
    total_amount = sum(item.price for item in purchase_data.items)

    # Create transaction
    transaction = Transaction(
        user_id=current_user.id,
        counterparty_id=counterparty.id,
        transaction_type=TransactionType.PURCHASE,
        status=TransactionStatus.COMPLETED,
        total_amount=total_amount,
        currency=purchase_data.currency,
        notes=purchase_data.notes,
        transaction_date=purchase_data.transaction_date or datetime.utcnow(),
    )

    session.add(transaction)
    await session.flush()  # Get transaction ID

    # Create transaction items and update price history
    for item_data in purchase_data.items:
        # Create transaction item
        transaction_item = TransactionItem(
            transaction_id=transaction.id,
            item_id=item_data.item_id,
            price=item_data.price,
            currency=item_data.currency,
            notes=item_data.notes,
        )
        session.add(transaction_item)

        # Add to price history
        price_history = ItemPriceHistory(
            item_id=item_data.item_id,
            price=item_data.price,
            type=PriceType.PURCHASE,
            date=transaction.transaction_date.date(),
            currency=transaction_item.currency,
            transaction_item_id=None,  # Will be set after transaction_item is saved
        )
        session.add(price_history)

    await session.commit()
    await session.refresh(transaction)

    return transaction


@router.post("/purchase-collection", response_model=TransactionRead, status_code=status.HTTP_201_CREATED)
async def purchase_collections(
    purchase_data: TransactionCollectionPurchaseRequest,
    session: SessionDependency,
    current_user: User = Depends(current_active_user),
) -> Transaction:
    """Purchase collections from a counterparty (supports hierarchical collections)."""

    # Validate counterparty
    counterparty = await verify_counterparty_ownership(
        purchase_data.counterparty_id,
        session,
        current_user,
    )

    # Validate collections
    collection_ids = [collection.collection_id for collection in purchase_data.collections]
    collections = await verify_collections_ownership(collection_ids, session, current_user)

    # Calculate total amount
    total_amount = sum(collection.price for collection in purchase_data.collections)

    # Create transaction
    transaction = Transaction(
        user_id=current_user.id,
        counterparty_id=counterparty.id,
        transaction_type=TransactionType.PURCHASE,
        status=TransactionStatus.COMPLETED,
        total_amount=total_amount,
        currency=purchase_data.currency,
        notes=purchase_data.notes,
        transaction_date=purchase_data.transaction_date or datetime.utcnow(),
    )

    session.add(transaction)
    await session.flush()  # Get transaction ID

    # Process each collection
    for collection_data in purchase_data.collections:
        # Find the collection object
        collection = next(col for col in collections if col.id == collection_data.collection_id)

        # Create hierarchical transaction collection records
        transaction_collections = await create_hierarchical_transaction_collections(
            collection,
            transaction.id,
            collection_data.price,
            collection_data.currency,
            session,
        )

        # Get the root transaction collection (first one created)
        root_transaction_collection = transaction_collections[0]

        # Distribute collection price among all items (including items from descendant collections)
        item_prices = await distribute_collection_price_to_items(
            collection, collection_data.price, collection_data.currency, session
        )

        # Create transaction items and price history for each item
        for item, item_price in item_prices:
            # Find which transaction collection this item belongs to
            item_transaction_collection = None
            for tc in transaction_collections:
                if tc.collection_id == item.collection_id:
                    item_transaction_collection = tc
                    break

            # If item's collection not found in transaction collections, use root
            if item_transaction_collection is None:
                item_transaction_collection = root_transaction_collection

            # Create transaction item
            transaction_item = TransactionItem(
                transaction_id=transaction.id,
                item_id=item.id,
                price=item_price,
                currency=collection_data.currency,
                transaction_collection_id=item_transaction_collection.id,
                notes=f"From collection '{collection.name}': {collection_data.notes or ''}".strip(),
            )
            session.add(transaction_item)

            # Add to price history
            price_type = PriceType.COLLECTION_PURCHASE
            if item_transaction_collection.parent_transaction_collection_id is not None:
                # This item is from a descendant collection
                price_type = PriceType.COLLECTION_PURCHASE  # You might want a different type here

            price_history = ItemPriceHistory(
                item_id=item.id,
                price=item_price,
                type=price_type,
                date=transaction.transaction_date.date(),
                currency=collection_data.currency,
                transaction_item_id=None,  # Will be set after transaction_item is saved
            )
            session.add(price_history)

    await session.commit()
    await session.refresh(transaction)

    return transaction


@router.post("/sale", response_model=TransactionRead, status_code=status.HTTP_201_CREATED)
async def sell_items(
    sale_data: TransactionSaleRequest,
    session: SessionDependency,
    current_user: User = Depends(current_active_user),
) -> Transaction:
    """Sell items to a counterparty."""

    # Validate counterparty
    counterparty = await verify_counterparty_ownership(
        sale_data.counterparty_id,
        session,
        current_user,
    )

    # Validate items
    item_ids = [item.item_id for item in sale_data.items]
    items = await verify_items_ownership(item_ids, session, current_user)

    # Remove items from collections before selling individually
    for item in items:
        if item.collection_id is not None:
            item.collection_id = None

    # Calculate total amount
    total_amount = sum(item.price for item in sale_data.items)

    # Create transaction
    transaction = Transaction(
        user_id=current_user.id,
        counterparty_id=counterparty.id,
        transaction_type=TransactionType.SALE,
        status=TransactionStatus.COMPLETED,
        total_amount=total_amount,
        currency=sale_data.currency,
        notes=sale_data.notes,
        transaction_date=sale_data.transaction_date or datetime.utcnow(),
    )

    session.add(transaction)
    await session.flush()  # Get transaction ID

    # Create transaction items and update price history
    for item_data in sale_data.items:
        # Create transaction item
        transaction_item = TransactionItem(
            transaction_id=transaction.id,
            item_id=item_data.item_id,
            price=item_data.price,
            currency=item_data.currency,
            notes=item_data.notes,
        )
        session.add(transaction_item)

        # Add to price history
        price_history = ItemPriceHistory(
            item_id=item_data.item_id,
            price=item_data.price,
            type=PriceType.SALE,
            date=transaction.transaction_date.date(),
            currency=transaction_item.currency,
            transaction_item_id=None,  # Will be set after transaction_item is saved
        )
        session.add(price_history)

    await session.commit()
    await session.refresh(transaction)

    return transaction


@router.post("/sale-collection", response_model=TransactionRead, status_code=status.HTTP_201_CREATED)
async def sell_collections(
    sale_data: TransactionCollectionSaleRequest,
    session: SessionDependency,
    current_user: User = Depends(current_active_user),
) -> Transaction:
    """Sell collections to a counterparty (supports hierarchical collections)."""

    # Validate counterparty
    counterparty = await verify_counterparty_ownership(
        sale_data.counterparty_id,
        session,
        current_user,
    )

    # Validate collections
    collection_ids = [collection.collection_id for collection in sale_data.collections]
    collections = await verify_collections_ownership(collection_ids, session, current_user)

    # Calculate total amount
    total_amount = sum(collection.price for collection in sale_data.collections)

    # Create transaction
    transaction = Transaction(
        user_id=current_user.id,
        counterparty_id=counterparty.id,
        transaction_type=TransactionType.SALE,
        status=TransactionStatus.COMPLETED,
        total_amount=total_amount,
        currency=sale_data.currency,
        notes=sale_data.notes,
        transaction_date=sale_data.transaction_date or datetime.utcnow(),
    )

    session.add(transaction)
    await session.flush()  # Get transaction ID

    # Process each collection
    for collection_data in sale_data.collections:
        # Find the collection object
        collection = next(col for col in collections if col.id == collection_data.collection_id)

        # Create hierarchical transaction collection records
        transaction_collections = await create_hierarchical_transaction_collections(
            collection,
            transaction.id,
            collection_data.price,
            collection_data.currency,
            session,
        )

        # Get the root transaction collection (first one created)
        root_transaction_collection = transaction_collections[0]

        # Distribute collection price among all items (including items from descendant collections)
        item_prices = await distribute_collection_price_to_items(
            collection, collection_data.price, collection_data.currency, session
        )

        # Create transaction items and price history for each item
        for item, item_price in item_prices:
            # Find which transaction collection this item belongs to
            item_transaction_collection = None
            for tc in transaction_collections:
                if tc.collection_id == item.collection_id:
                    item_transaction_collection = tc
                    break

            # If item's collection not found in transaction collections, use root
            if item_transaction_collection is None:
                item_transaction_collection = root_transaction_collection

            # Create transaction item
            transaction_item = TransactionItem(
                transaction_id=transaction.id,
                item_id=item.id,
                price=item_price,
                currency=collection_data.currency,
                transaction_collection_id=item_transaction_collection.id,
                notes=f"From collection '{collection.name}': {collection_data.notes or ''}".strip(),
            )
            session.add(transaction_item)

            # Add to price history
            price_type = PriceType.COLLECTION_SALE
            if item_transaction_collection.parent_transaction_collection_id is not None:
                # This item is from a descendant collection
                price_type = PriceType.COLLECTION_SALE  # You might want a different type here

            price_history = ItemPriceHistory(
                item_id=item.id,
                price=item_price,
                type=price_type,
                date=transaction.transaction_date.date(),
                currency=collection_data.currency,
                transaction_item_id=None,  # Will be set after transaction_item is saved
            )
            session.add(price_history)

    await session.commit()
    await session.refresh(transaction)

    return transaction


@router.post("/{transaction_id}/cancel", response_model=TransactionRead)
async def cancel_transaction(
    transaction_id: UUID,
    session: SessionDependency,
    current_user: User = Depends(current_active_user),
) -> Transaction:
    """Cancel a transaction."""

    # Get transaction
    result: Result[Any] = await session.execute(
        select(Transaction)
        .options(selectinload(Transaction.transaction_items))
        .where(
            Transaction.id == str(transaction_id),
            Transaction.user_id == current_user.id,
        )
    )
    transaction = result.scalar_one_or_none()

    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

    # Check if transaction can be cancelled
    if transaction.status == TransactionStatus.CANCELLED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Transaction is already cancelled")

    if transaction.status not in [TransactionStatus.PENDING, TransactionStatus.COMPLETED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Only pending or completed transactions can be cancelled"
        )

    # Update transaction status
    transaction.status = TransactionStatus.CANCELLED

    # Update price history for sales
    if transaction.transaction_type == TransactionType.SALE:
        # For cancelled sales: change SALE/COLLECTION_SALE price history to CURRENT
        # This makes items available again at their sale price
        for transaction_item in transaction.transaction_items:
            # Find price history records for this item on transaction date
            price_history_result = await session.execute(
                select(ItemPriceHistory).where(
                    ItemPriceHistory.item_id == transaction_item.item_id,
                    ItemPriceHistory.date == transaction.transaction_date.date(),
                    ItemPriceHistory.type.in_([PriceType.SALE, PriceType.COLLECTION_SALE]),
                )
            )
            price_histories = price_history_result.scalars().all()

            # Change SALE or COLLECTION_SALE to CURRENT
            for price_history in price_histories:
                price_history.type = PriceType.CURRENT

    # Note: PURCHASE transaction cancellation not implemented in MVP
    # Users can manually delete items if needed

    await session.commit()
    await session.refresh(transaction)

    return transaction


@router.get("/", response_model=list[TransactionRead])
async def get_user_transactions(
    session: SessionDependency,
    current_user: User = Depends(current_active_user),
) -> list[Transaction]:
    """Get all transactions for the current user."""
    result: Result[Any] = await session.execute(
        select(Transaction).where(Transaction.user_id == current_user.id).order_by(Transaction.transaction_date.desc())
    )

    return list(result.scalars().all())


@router.get("/{transaction_id}", response_model=TransactionRead)
async def get_transaction(
    transaction_id: UUID,
    session: SessionDependency,
    current_user: User = Depends(current_active_user),
) -> Transaction:
    """Get a specific transaction with all details."""
    result: Result[Any] = await session.execute(
        select(Transaction)
        .options(
            selectinload(Transaction.transaction_items),
            selectinload(Transaction.counterparty),
        )
        .where(
            Transaction.id == str(transaction_id),
            Transaction.user_id == current_user.id,
        )
    )
    transaction = result.scalar_one_or_none()

    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

    return transaction


@router.get("/{transaction_id}/items", response_model=list[TransactionItemRead])
async def get_transaction_items(
    transaction_id: UUID,
    session: SessionDependency,
    current_user: User = Depends(current_active_user),
) -> list[TransactionItem]:
    """Get all items in a specific transaction."""
    # First verify transaction ownership
    transaction_result: Result[Any] = await session.execute(
        select(Transaction).where(
            Transaction.id == str(transaction_id),
            Transaction.user_id == current_user.id,
        )
    )
    transaction = transaction_result.scalar_one_or_none()

    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

    # Get transaction items
    result: Result[Any] = await session.execute(
        select(TransactionItem).where(TransactionItem.transaction_id == str(transaction_id))
    )

    return list(result.scalars().all())
