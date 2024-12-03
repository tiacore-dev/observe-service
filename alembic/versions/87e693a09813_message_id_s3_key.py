"""Message_id, s3_key

Revision ID: 87e693a09813
Revises: 1d29c9b3db97
Create Date: 2024-12-02 14:48:28.785273

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '87e693a09813'
down_revision: Union[str, None] = '1d29c9b3db97'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Добавляем временный столбец для нового типа message_id, временно nullable=True
    op.add_column('messages', sa.Column('message_id_temp', sa.String(length=36), nullable=True))

    # Копируем данные из старого message_id в новый временный столбец
    op.execute('UPDATE messages SET message_id_temp = message_id::text')

    # Делаем временный столбец NOT NULL
    with op.batch_alter_table('messages') as batch_op:
        batch_op.alter_column('message_id_temp', nullable=False)

    # Удаляем старый столбец message_id
    op.drop_column('messages', 'message_id')

    # Переименовываем временный столбец в message_id
    op.alter_column('messages', 'message_id_temp', new_column_name='message_id')

    # Замена image_url на s3_key
    op.add_column('messages', sa.Column('s3_key', sa.String, nullable=True))
    op.drop_column('messages', 'image_url')


def downgrade() -> None:
    # Добавляем временный столбец для восстановления старого типа message_id
    op.add_column('messages', sa.Column('message_id_temp', sa.BigInteger, nullable=True))

    # Копируем данные из нового message_id в временный столбец
    op.execute('UPDATE messages SET message_id_temp = message_id::bigint')

    # Удаляем новый столбец message_id
    op.drop_column('messages', 'message_id')

    # Переименовываем временный столбец обратно в message_id
    op.alter_column('messages', 'message_id_temp', new_column_name='message_id')

    # Восстанавливаем primary key на message_id
    with op.batch_alter_table('messages') as batch_op:
        batch_op.drop_constraint('messages_pkey', type_='primary')
        batch_op.create_primary_key('messages_pkey', ['message_id'])

    # Восстановление image_url вместо s3_key
    op.add_column('messages', sa.Column('image_url', sa.String, nullable=True))
    op.drop_column('messages', 's3_key')
