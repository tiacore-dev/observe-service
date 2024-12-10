"""Добавлены поля tokens_input и tokens_output в AnalysisResult

Revision ID: dcded27e709a
Revises: 9f37a849c02a
Create Date: 2024-12-10 13:02:23.017412

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dcded27e709a'
down_revision: Union[str, None] = '9f37a849c02a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column('analysis_results', sa.Column('tokens_input', sa.Integer()))
    op.add_column('analysis_results', sa.Column('tokens_output', sa.Integer()))
    op.drop_column('analysis_results', 'tokens')  # Удаляем старое поле, если оно больше не используется

def downgrade():
    op.add_column('analysis_results', sa.Column('tokens', sa.Integer(), nullable=True))
    op.drop_column('analysis_results', 'tokens_input')
    op.drop_column('analysis_results', 'tokens_output')
