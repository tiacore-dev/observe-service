"""Add messages and chats tables

Revision ID: 20ab3dfc9268
Revises: 529ce42e2d74
Create Date: 2024-12-06 12:01:11.111449

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '20ab3dfc9268'
down_revision: Union[str, None] = '529ce42e2d74'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'chats',
        sa.Column('chat_id', sa.BigInteger(), nullable=False),
        sa.Column('chat_name', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('chat_id')
    )


def downgrade() -> None:
    op.drop_table('chats')