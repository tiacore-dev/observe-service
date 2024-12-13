"""Добавить время запуска анализа

Revision ID: a888508bb264
Revises: 31238137d25d
Create Date: 2024-12-13 12:09:47.908487

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a888508bb264'
down_revision: Union[str, None] = '31238137d25d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('chats', sa.Column('analysis_time', sa.Time(), nullable=True))
    op.add_column('chats', sa.Column('send_time', sa.Time(), nullable=True))


def downgrade() -> None:
    op.drop_column('chats', 'analysis_time')
    op.drop_column('chats', 'send_time')