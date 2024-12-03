"""Admin Table

Revision ID: 56d488794227
Revises: a039b309f90d
Create Date: 2024-12-02 17:29:46.547920

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '56d488794227'
down_revision: Union[str, None] = 'a039b309f90d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Создаем таблицу admins
    op.create_table(
        'admins',
        sa.Column('user_id', sa.String, primary_key=True),  # Primary Key
        sa.Column('username', sa.String, nullable=True),  # Имя пользователя
        sa.Column('login', sa.String, unique=True, nullable=False),  # Email или логин
        sa.Column('password_hash', sa.String, nullable=True),  # Хеш пароля, может быть NULL
    )


def downgrade() -> None:
    # Удаляем таблицу admins
    op.drop_table('admins')
