"""Add bitcoin_prices table

Revision ID: 3d5c42d3a6e7
Revises: 9d578e490089
Create Date: 2025-01-17 12:19:50.157410

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3d5c42d3a6e7'
down_revision: Union[str, None] = '9d578e490089'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
