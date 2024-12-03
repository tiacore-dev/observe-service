"""User BigInteger

Revision ID: 1d29c9b3db97
Revises: a95309b6c57e
Create Date: 2024-12-02 12:51:54.823578

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1d29c9b3db97'
down_revision: Union[str, None] = 'a95309b6c57e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Изменяем тип столбца user_id с явным указанием приведения
    op.execute('ALTER TABLE users ALTER COLUMN user_id TYPE BIGINT USING user_id::BIGINT')



def downgrade() -> None:
    op.alter_column('users', 'user_id', existing_type=sa.BigInteger, type_=sa.String, nullable=False)
