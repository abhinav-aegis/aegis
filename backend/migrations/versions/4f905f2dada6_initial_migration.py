"""
Initial migration.

Revision ID: 4f905f2dada6
Revises:
Create Date: 2025-02-24 11:36:14.767940
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes
import sqlalchemy_utils
from backend.common.models.user_model import IGenderEnum


# revision identifiers, used by Alembic.
revision: str = '4f905f2dada6'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Media',
    sa.Column('title', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('description', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('path', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_Media_id'), 'Media', ['id'], unique=False)
    op.create_table('Role',
    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('description', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_Role_id'), 'Role', ['id'], unique=False)
    op.create_table('UserFollow',
    sa.Column('user_id', sa.Uuid(), nullable=False),
    sa.Column('target_user_id', sa.Uuid(), nullable=False),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('is_mutual', sa.Boolean(), server_default='0', nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_UserFollow_id'), 'UserFollow', ['id'], unique=False)
    op.create_table('ImageMedia',
    sa.Column('file_format', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('width', sa.Integer(), nullable=True),
    sa.Column('height', sa.Integer(), nullable=True),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('media_id', sa.Uuid(), nullable=True),
    sa.ForeignKeyConstraint(['media_id'], ['Media.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ImageMedia_id'), 'ImageMedia', ['id'], unique=False)
    op.create_table('User',
    sa.Column('first_name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('last_name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('email', sa.String(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('is_superuser', sa.Boolean(), nullable=False),
    sa.Column('birthdate', sa.DateTime(timezone=True), nullable=True),
    sa.Column('role_id', sa.Uuid(), nullable=True),
    sa.Column('phone', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('gender', sqlalchemy_utils.types.choice.ChoiceType(IGenderEnum), nullable=True),
    sa.Column('state', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('country', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('address', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('hashed_password', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('image_id', sa.Uuid(), nullable=True),
    sa.Column('follower_count', sa.BigInteger(), server_default='0', nullable=True),
    sa.Column('following_count', sa.BigInteger(), server_default='0', nullable=True),
    sa.ForeignKeyConstraint(['image_id'], ['ImageMedia.id'], ),
    sa.ForeignKeyConstraint(['role_id'], ['Role.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_User_email'), 'User', ['email'], unique=True)
    op.create_index(op.f('ix_User_hashed_password'), 'User', ['hashed_password'], unique=False)
    op.create_index(op.f('ix_User_id'), 'User', ['id'], unique=False)
    op.create_table('Group',
    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('description', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('created_by_id', sa.Uuid(), nullable=True),
    sa.ForeignKeyConstraint(['created_by_id'], ['User.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_Group_id'), 'Group', ['id'], unique=False)
    op.create_table('Team',
    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('headquarters', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('created_by_id', sa.Uuid(), nullable=True),
    sa.ForeignKeyConstraint(['created_by_id'], ['User.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_Team_id'), 'Team', ['id'], unique=False)
    op.create_index(op.f('ix_Team_name'), 'Team', ['name'], unique=False)
    op.create_table('Hero',
    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('secret_name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('age', sa.Integer(), nullable=True),
    sa.Column('team_id', sa.Uuid(), nullable=True),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('created_by_id', sa.Uuid(), nullable=True),
    sa.ForeignKeyConstraint(['created_by_id'], ['User.id'], ),
    sa.ForeignKeyConstraint(['team_id'], ['Team.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_Hero_age'), 'Hero', ['age'], unique=False)
    op.create_index(op.f('ix_Hero_id'), 'Hero', ['id'], unique=False)
    op.create_index(op.f('ix_Hero_name'), 'Hero', ['name'], unique=False)
    op.create_table('LinkGroupUser',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('group_id', sa.Uuid(), nullable=False),
    sa.Column('user_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['group_id'], ['Group.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['User.id'], ),
    sa.PrimaryKeyConstraint('id', 'group_id', 'user_id')
    )
    op.create_index(op.f('ix_LinkGroupUser_id'), 'LinkGroupUser', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_LinkGroupUser_id'), table_name='LinkGroupUser')
    op.drop_table('LinkGroupUser')
    op.drop_index(op.f('ix_Hero_name'), table_name='Hero')
    op.drop_index(op.f('ix_Hero_id'), table_name='Hero')
    op.drop_index(op.f('ix_Hero_age'), table_name='Hero')
    op.drop_table('Hero')
    op.drop_index(op.f('ix_Team_name'), table_name='Team')
    op.drop_index(op.f('ix_Team_id'), table_name='Team')
    op.drop_table('Team')
    op.drop_index(op.f('ix_Group_id'), table_name='Group')
    op.drop_table('Group')
    op.drop_index(op.f('ix_User_id'), table_name='User')
    op.drop_index(op.f('ix_User_hashed_password'), table_name='User')
    op.drop_index(op.f('ix_User_email'), table_name='User')
    op.drop_table('User')
    op.drop_index(op.f('ix_ImageMedia_id'), table_name='ImageMedia')
    op.drop_table('ImageMedia')
    op.drop_index(op.f('ix_UserFollow_id'), table_name='UserFollow')
    op.drop_table('UserFollow')
    op.drop_index(op.f('ix_Role_id'), table_name='Role')
    op.drop_table('Role')
    op.drop_index(op.f('ix_Media_id'), table_name='Media')
    op.drop_table('Media')
    # ### end Alembic commands ###
