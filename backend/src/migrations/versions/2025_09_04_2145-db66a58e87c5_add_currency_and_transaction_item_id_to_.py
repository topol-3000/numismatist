"""add_currency_and_transaction_item_id_to_item_price_history

Revision ID: db66a58e87c5
Revises: bc45f5e24e74
Create Date: 2025-09-04 21:45:23.517248

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'db66a58e87c5'
down_revision: Union[str, None] = 'bc45f5e24e74'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Ensure currency enum exists (safe to run multiple times)
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'currency') THEN
                CREATE TYPE currency AS ENUM ('USD', 'EUR');
            END IF;
        END
        $$;
    """)

    op.add_column('item_price_history', sa.Column('currency', sa.Enum('USD', 'EUR', name='currency', create_type=False), server_default='USD', nullable=False))
    op.add_column('item_price_history', sa.Column('transaction_item_id', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_item_price_history_transaction_item_id'), 'item_price_history', ['transaction_item_id'], unique=False)
    op.create_foreign_key(op.f('fk_item_price_history_transaction_item_id_transaction_items'), 'item_price_history', 'transaction_items', ['transaction_item_id'], ['id'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(op.f('fk_item_price_history_transaction_item_id_transaction_items'), 'item_price_history', type_='foreignkey')
    op.drop_index(op.f('ix_item_price_history_transaction_item_id'), table_name='item_price_history')
    op.drop_column('item_price_history', 'transaction_item_id')
    op.drop_column('item_price_history', 'currency')
