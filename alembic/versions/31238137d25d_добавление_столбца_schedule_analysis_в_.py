"""Добавление столбца schedule_analysis в таблицу chats

Revision ID: 31238137d25d
Revises: dcded27e709a
Create Date: 2024-12-10 15:28:32.930863

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '31238137d25d'
down_revision: Union[str, None] = 'dcded27e709a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column('chats', sa.Column('schedule_analysis', sa.Boolean, default=False))


def downgrade():
    op.drop_column('chats', 'schedule_analysis')