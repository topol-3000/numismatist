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
    Counterparty,
    Item,
    ItemPriceHistory,
    Transaction,
    TransactionItem,
    User,
)
from schemas.transaction import TransactionRead
from schemas.transaction_item import TransactionItemCreate, TransactionItemRead
from utils.enums import Currency, PriceType, TransactionStatus, TransactionType

router = APIRouter(prefix="/transactions", tags=["Transactions"])


class TransactionPurchaseRequest(BaseModel):
    """Request schema for purchasing items."""

    counterparty_id: Annotated[int, Field(description="ID of the counterparty")]
    items: Annotated[list[TransactionItemCreate], Field(description="List of items to purchase")]
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
    await verify_items_ownership(item_ids, session, current_user)

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

    # For cancelled transactions, we could add reverse price history entries
    # but for MVP we'll just mark transaction as cancelled

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
