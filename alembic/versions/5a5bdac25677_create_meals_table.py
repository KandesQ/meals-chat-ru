"""create meals table

Revision ID: 5a5bdac25677
Revises: 
Create Date: 2026-01-27 21:36:40.944159

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5a5bdac25677'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "meals",
        sa.Column("id", sa.BigInteger, primary_key=True),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("calories", sa.Integer, nullable=False),
        sa.Column("protein_grams", sa.Numeric(6, 2), nullable=False),
        sa.Column("carbs_grams", sa.Numeric(6, 2), nullable=False),
        sa.Column("fat_grams", sa.Numeric(6, 2), nullable=False),
        sa.Column("likely_ingredients", sa.JSON, nullable=False),
        sa.Column("user_telegram_account_id", sa.BigInteger, nullable=False),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), nullable=False)
    )


def downgrade() -> None:
    """Downgrade schema."""
    pass
