"""Initial migration

Revision ID: a95309b6c57e
Revises: 
Create Date: 2024-12-02 12:41:19.051943

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a95309b6c57e'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Создание таблицы users
    op.create_table(
        'users',
        sa.Column('user_id', sa.String, primary_key=True, autoincrement=False),
        sa.Column('username', sa.String, nullable=True),  # Имя пользователя
    )

    # Создание таблицы messages
    op.create_table(
        'messages',
        sa.Column('message_id', sa.BigInteger, primary_key=True),  # Уникальный ID сообщения
        sa.Column('timestamp', sa.DateTime, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),  # Время отправки
        sa.Column('user_id', sa.BigInteger, nullable=False),  # ID пользователя
        sa.Column('chat_id', sa.BigInteger, nullable=False),  # ID чата
        sa.Column('text', sa.Text, nullable=True),  # Текст сообщения
        sa.Column('image_url', sa.String, nullable=True),  # URL изображения
    )


def downgrade() -> None:
    # Удаление таблиц в обратной миграции
    op.drop_table('messages')
    op.drop_table('users')
