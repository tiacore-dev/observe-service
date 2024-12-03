"""Tokens in analysis

Revision ID: 529ce42e2d74
Revises: caf5ac512d89
Create Date: 2024-12-03 11:18:02.026608

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '529ce42e2d74'
down_revision: Union[str, None] = 'caf5ac512d89'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Добавляем временный столбец для восстановления старого типа message_id
    op.add_column('analysis_results', sa.Column('tokens', sa.Integer))


def downgrade() -> None:
    # Удаляем новый столбец message_id
    op.drop_column('analysis_results', 'tokens')
