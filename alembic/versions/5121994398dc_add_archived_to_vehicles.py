"""Add archived to vehicles

Revision ID: 5121994398dc
Revises: 85f50bf98967
Create Date: 2026-07-09 15:57:19.754364

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5121994398dc'
down_revision: Union[str, Sequence[str], None] = '85f50bf98967'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """Upgrade schema."""

    op.add_column(
        'maintenance_schedule',
        sa.Column(
            'archived',
            sa.Boolean(),
            nullable=True
        )
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_column(
        'maintenance_schedule',
        'archived'
    )