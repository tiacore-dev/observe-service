"""Analysis

Revision ID: caf5ac512d89
Revises: 56d488794227
Create Date: 2024-12-02 19:02:55.947520

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'caf5ac512d89'
down_revision: Union[str, None] = '56d488794227'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        'analysis_results',
        sa.Column('analysis_id', sa.String, primary_key=True),
        sa.Column('prompt_id', sa.String,  nullable=False),
        sa.Column('result_text', sa.Text, nullable=False),
        sa.Column('timestamp', sa.DateTime, nullable=False),
        sa.Column('filters', sa.String)
    )


def downgrade():
    op.drop_table('analysis_results')
