"""create user_goals table

Revision ID: ba4280774a46
Revises: 5a5bdac25677
Create Date: 2026-02-13 16:44:55.349624

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ba4280774a46'
down_revision: Union[str, Sequence[str], None] = '5a5bdac25677'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "user_goals",
        sa.Column("id", sa.BigInteger, primary_key=True),
        sa.Column("user_telegram_id", sa.BigInteger, nullable=False),
        sa.Column("protein_percent", sa.Integer, nullable=False),
        sa.Column("carbs_percent", sa.Integer, nullable=False),
        sa.Column("fat_percent", sa.Integer, nullable=False)
    )





def downgrade() -> None:
    """Downgrade schema."""
    pass
