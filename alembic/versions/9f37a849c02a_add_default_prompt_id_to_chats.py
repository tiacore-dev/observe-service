"""Add default_prompt_id to chats

Revision ID: 9f37a849c02a
Revises: 20ab3dfc9268
Create Date: 2024-12-09 15:36:50.025187

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9f37a849c02a'
down_revision: Union[str, None] = '20ab3dfc9268'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Добавляем временный столбец для нового типа message_id, временно nullable=True
    op.add_column('chats', sa.Column('default_prompt_id', sa.String, nullable=True))


def downgrade() -> None:
    op.drop_column('chats', 'default_prompt_id')
