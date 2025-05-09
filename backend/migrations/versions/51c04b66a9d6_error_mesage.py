"""
Error mesage.

Revision ID: 51c04b66a9d6
Revises: 8f3ca9e05e0a
Create Date: 2025-04-17 06:48:28.025429
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes
import sqlalchemy_utils


# revision identifiers, used by Alembic.
revision: str = '51c04b66a9d6'
down_revision: Union[str, None] = '8f3ca9e05e0a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Run', sa.Column('error_details', sa.JSON(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Run', 'error_details')
    # ### end Alembic commands ###
