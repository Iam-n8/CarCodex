"""Add archived to maintenance visits

Revision ID: 85f50bf98967
Revises: ea0a8af5e8ff
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '85f50bf98967'
down_revision: Union[str, Sequence[str], None] = 'ea0a8af5e8ff'
branch_labels = None
depends_on = None


def upgrade() -> None:

    op.add_column(
        'maintenance_visits',
        sa.Column(
            'archived',
            sa.Boolean(),
            nullable=True
        )
    )


def downgrade() -> None:

    op.drop_column(
        'maintenance_visits',
        'archived'
    )
