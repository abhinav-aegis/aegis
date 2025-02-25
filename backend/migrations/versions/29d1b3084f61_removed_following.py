"""
Removed Following.

Revision ID: 29d1b3084f61
Revises: 87f264cf9918
Create Date: 2025-02-25 00:57:42.427535
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes
import sqlalchemy_utils
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '29d1b3084f61'
down_revision: Union[str, None] = '87f264cf9918'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_UserFollow_id', table_name='UserFollow')
    op.drop_table('UserFollow')
    op.drop_column('User', 'following_count')
    op.drop_column('User', 'follower_count')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('User', sa.Column('follower_count', sa.BIGINT(), server_default=sa.text("'0'::bigint"), autoincrement=False, nullable=True))
    op.add_column('User', sa.Column('following_count', sa.BIGINT(), server_default=sa.text("'0'::bigint"), autoincrement=False, nullable=True))
    op.create_table('UserFollow',
    sa.Column('user_id', sa.UUID(), autoincrement=False, nullable=False),
    sa.Column('target_user_id', sa.UUID(), autoincrement=False, nullable=False),
    sa.Column('id', sa.UUID(), autoincrement=False, nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('is_mutual', sa.BOOLEAN(), server_default=sa.text('false'), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='UserFollow_pkey')
    )
    op.create_index('ix_UserFollow_id', 'UserFollow', ['id'], unique=False)
    # ### end Alembic commands ###
