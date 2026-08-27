"""Link documents to maintenance visits

Revision ID: dd46d2694333
Revises: 07ee23af1528
Create Date: 2026-07-07 12:56:59.124679

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dd46d2694333'
down_revision: Union[str, Sequence[str], None] = '07ee23af1528'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade() -> None:

    op.add_column(
        'documents',
        sa.Column(
            'maintenance_visit_id',
            sa.Integer(),
            nullable=True
        )
    )


    # ### end Alembic commands ###


def downgrade() -> None:
    op.drop_column(
        'documents',
        'maintenance_visit_id'
    )

    # ### end Alembic commands ###
