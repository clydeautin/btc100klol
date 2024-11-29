"""adding prompt and image_link tables

Revision ID: bc8bfb87f94e
Revises: 3edb3fbd6fc2
Create Date: 2024-11-29 15:03:19.266415

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bc8bfb87f94e'
down_revision: Union[str, None] = '3edb3fbd6fc2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('prompt',
    sa.Column('prompt_text', sa.Text(), nullable=False),
    sa.Column('prompt_date', sa.Date(), nullable=False),
    sa.Column('prompt_type', sa.Enum('GET_HOLIDAYS', 'GENERATE_IMAGE_SAD', 'GENERATE_IMAGE_HAPPY', name='prompttype'), nullable=False),
    sa.Column('status', sa.Enum('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED', name='taskstatus'), server_default='PENDING', nullable=False),
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('created', sa.DateTime(), nullable=False),
    sa.Column('created_ts', sa.Integer(), nullable=False),
    sa.Column('last_modified', sa.DateTime(), nullable=False),
    sa.Column('last_modified_ts', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('prompt')
    # ### end Alembic commands ###