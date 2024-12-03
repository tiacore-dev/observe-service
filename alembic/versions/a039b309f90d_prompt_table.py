"""Prompt Table

Revision ID: a039b309f90d
Revises: 87e693a09813
Create Date: 2024-12-02 16:42:05.995160

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a039b309f90d'
down_revision: Union[str, None] = '87e693a09813'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Создание таблицы prompts
    op.create_table(
        'prompts',
        sa.Column('prompt_id', sa.String, primary_key=True),  # Primary key
        sa.Column('prompt_name', sa.String(length=255), nullable=False),  # Название промпта
        sa.Column('text', sa.Text, nullable=True),  # Текст промпта
        sa.Column('use_automatic', sa.Boolean, nullable=True, server_default='false'),  # Булевый столбец
    )


def downgrade() -> None:
    # Удаление таблицы prompts
    op.drop_table('prompts')
