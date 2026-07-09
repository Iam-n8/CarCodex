"""Add vendors

Revision ID: 548ec0541ef9
Revises: dd46d2694333
Create Date: 2026-07-08 08:14:02.730320

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '548ec0541ef9'
down_revision: Union[str, Sequence[str], None] = 'dd46d2694333'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:

    op.create_table(
        'vendors',

        sa.Column('id', sa.Integer(), nullable=False),

        sa.Column('name', sa.String(), nullable=True),

        sa.Column('vendor_type', sa.String(), nullable=True),

        sa.Column('address_1', sa.String(), nullable=True),
        sa.Column('address_2', sa.String(), nullable=True),

        sa.Column('city', sa.String(), nullable=True),
        sa.Column('state', sa.String(), nullable=True),
        sa.Column('zip_code', sa.String(), nullable=True),

        sa.Column('phone', sa.String(), nullable=True),
        sa.Column('email', sa.String(), nullable=True),

        sa.Column('website', sa.String(), nullable=True),

        sa.Column('primary_contact', sa.String(), nullable=True),

        sa.Column('notes', sa.String(), nullable=True),

        sa.Column('is_preferred', sa.Boolean(), nullable=True),

        sa.Column('archived', sa.Boolean(), nullable=True),

        sa.PrimaryKeyConstraint('id')
    )

def downgrade() -> None:
    op.drop_table('vendors')

    # ### end Alembic commands ###
