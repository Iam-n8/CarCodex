"""Add vendor id to maintenance visits

Revision ID: ea0a8af5e8ff
Revises: 548ec0541ef9
Create Date: 2026-07-09 09:41:42.317267

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ea0a8af5e8ff'
down_revision: Union[str, Sequence[str], None] = '548ec0541ef9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column(
        'maintenance_visits',
        sa.Column(
            'vendor_id',
            sa.Integer(),
            nullable=True
        )
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_column(
        'maintenance_visits',
        'vendor_id'
    )