"""Login in users

Revision ID: b4edd1b4395b
Revises: a888508bb264
Create Date: 2025-02-26 17:41:39.690624

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b4edd1b4395b'
down_revision: Union[str, None] = 'a888508bb264'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('login', sa.String))


def downgrade() -> None:
    op.drop_column('users', 'login')
