"""
Evals.

Revision ID: 4b558fb6b4a8
Revises: cff748b57638
Create Date: 2025-04-02 00:43:26.613808
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes
import sqlalchemy_utils


# revision identifiers, used by Alembic.
revision: str = '4b558fb6b4a8'
down_revision: Union[str, None] = 'cff748b57638'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('EvaluationCache',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('evaluator_config_hash', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('input_hash', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('result', sa.JSON(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_EvaluationCache_evaluator_config_hash'), 'EvaluationCache', ['evaluator_config_hash'], unique=False)
    op.create_index(op.f('ix_EvaluationCache_id'), 'EvaluationCache', ['id'], unique=False)
    op.create_index(op.f('ix_EvaluationCache_input_hash'), 'EvaluationCache', ['input_hash'], unique=False)
    op.create_table('EvaluationJob',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('tenant_id', sa.Uuid(), nullable=True),
    sa.Column('task_id', sa.Uuid(), nullable=False),
    sa.Column('dataset_id', sa.Uuid(), nullable=True),
    sa.Column('team_ids', sa.JSON(), nullable=False),
    sa.Column('metrics', sa.JSON(), nullable=False),
    sa.Column('status', sa.Enum('PENDING', 'RUNNING', 'COMPLETED', 'FAILED', name='evaluationjobstatus'), nullable=False),
    sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('evaluation_component', sa.JSON(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_EvaluationJob_dataset_id'), 'EvaluationJob', ['dataset_id'], unique=False)
    op.create_index(op.f('ix_EvaluationJob_id'), 'EvaluationJob', ['id'], unique=False)
    op.create_index(op.f('ix_EvaluationJob_task_id'), 'EvaluationJob', ['task_id'], unique=False)
    op.create_index(op.f('ix_EvaluationJob_tenant_id'), 'EvaluationJob', ['tenant_id'], unique=False)
    op.create_table('EvaluationResult',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('job_id', sa.Uuid(), nullable=False),
    sa.Column('session_id', sa.Uuid(), nullable=False),
    sa.Column('team_id', sa.Uuid(), nullable=False),
    sa.Column('metric_name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('score', sa.Float(), nullable=False),
    sa.Column('std_dev', sa.Float(), nullable=True),
    sa.Column('confidence_interval', sa.JSON(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_EvaluationResult_id'), 'EvaluationResult', ['id'], unique=False)
    op.create_index(op.f('ix_EvaluationResult_job_id'), 'EvaluationResult', ['job_id'], unique=False)
    op.create_index(op.f('ix_EvaluationResult_metric_name'), 'EvaluationResult', ['metric_name'], unique=False)
    op.create_index(op.f('ix_EvaluationResult_session_id'), 'EvaluationResult', ['session_id'], unique=False)
    op.create_index(op.f('ix_EvaluationResult_team_id'), 'EvaluationResult', ['team_id'], unique=False)
    op.create_table('GroundTruthDataset',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('task_id', sa.Uuid(), nullable=False),
    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('description', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('label_uri', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_GroundTruthDataset_id'), 'GroundTruthDataset', ['id'], unique=False)
    op.create_index(op.f('ix_GroundTruthDataset_task_id'), 'GroundTruthDataset', ['task_id'], unique=False)
    op.create_table('GroundTruthItem',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('dataset_id', sa.Uuid(), nullable=False),
    sa.Column('tenant_id', sa.Uuid(), nullable=True),
    sa.Column('input_uri', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('ground_truth_label', sa.JSON(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_GroundTruthItem_dataset_id'), 'GroundTruthItem', ['dataset_id'], unique=False)
    op.create_index(op.f('ix_GroundTruthItem_id'), 'GroundTruthItem', ['id'], unique=False)
    op.create_index(op.f('ix_GroundTruthItem_tenant_id'), 'GroundTruthItem', ['tenant_id'], unique=False)
    op.create_table('LLMAPIKey',
    sa.Column('tenant_id', sa.Uuid(), nullable=False),
    sa.Column('user_id', sa.Uuid(), nullable=True),
    sa.Column('group_id', sa.Uuid(), nullable=True),
    sa.Column('provider', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('total_input_tokens', sa.Integer(), nullable=False),
    sa.Column('total_output_tokens', sa.Integer(), nullable=False),
    sa.Column('total_cost', sa.Float(), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('api_key', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_LLMAPIKey_api_key'), 'LLMAPIKey', ['api_key'], unique=True)
    op.create_index(op.f('ix_LLMAPIKey_id'), 'LLMAPIKey', ['id'], unique=False)
    op.create_table('UserFeedback',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('tenant_id', sa.Uuid(), nullable=True),
    sa.Column('session_id', sa.Uuid(), nullable=True),
    sa.Column('team_id', sa.Uuid(), nullable=True),
    sa.Column('feedback_type', sa.Enum('POSITIVE', 'NEGATIVE', 'RATING', name='feedbacktype'), nullable=False),
    sa.Column('rating', sa.Float(), nullable=True),
    sa.Column('comments', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_UserFeedback_id'), 'UserFeedback', ['id'], unique=False)
    op.create_index(op.f('ix_UserFeedback_session_id'), 'UserFeedback', ['session_id'], unique=False)
    op.create_index(op.f('ix_UserFeedback_team_id'), 'UserFeedback', ['team_id'], unique=False)
    op.create_index(op.f('ix_UserFeedback_tenant_id'), 'UserFeedback', ['tenant_id'], unique=False)
    op.create_table('LLMErrorLog',
    sa.Column('tenant_id', sa.Uuid(), nullable=False),
    sa.Column('user_id', sa.Uuid(), nullable=True),
    sa.Column('group_id', sa.Uuid(), nullable=True),
    sa.Column('provider', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('model', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('request_id', sa.Uuid(), nullable=False),
    sa.Column('vendor_request_id', sa.String(), nullable=True),
    sa.Column('batch_job_id', sa.String(), nullable=True),
    sa.Column('error_type', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('error_message', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('status_code', sa.Integer(), nullable=True),
    sa.Column('response_data', sa.String(), nullable=True),
    sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('api_key_id', sa.UUID(), nullable=True),
    sa.ForeignKeyConstraint(['api_key_id'], ['LLMAPIKey.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_LLMErrorLog_api_key_id'), 'LLMErrorLog', ['api_key_id'], unique=False)
    op.create_index(op.f('ix_LLMErrorLog_batch_job_id'), 'LLMErrorLog', ['batch_job_id'], unique=False)
    op.create_index(op.f('ix_LLMErrorLog_id'), 'LLMErrorLog', ['id'], unique=False)
    op.create_index(op.f('ix_LLMErrorLog_request_id'), 'LLMErrorLog', ['request_id'], unique=False)
    op.create_index(op.f('ix_LLMErrorLog_timestamp'), 'LLMErrorLog', ['timestamp'], unique=False)
    op.create_index(op.f('ix_LLMErrorLog_vendor_request_id'), 'LLMErrorLog', ['vendor_request_id'], unique=False)
    op.create_table('LLMUsage',
    sa.Column('tenant_id', sa.Uuid(), nullable=False),
    sa.Column('user_id', sa.Uuid(), nullable=True),
    sa.Column('group_id', sa.Uuid(), nullable=True),
    sa.Column('provider', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('model', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('vendor_request_id', sa.String(), nullable=True),
    sa.Column('batch_job_id', sa.String(), nullable=True),
    sa.Column('input_tokens', sa.Integer(), nullable=False),
    sa.Column('output_tokens', sa.Integer(), nullable=False),
    sa.Column('total_tokens', sa.Integer(), nullable=False),
    sa.Column('cost', sa.Float(), nullable=False),
    sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('api_key_id', sa.UUID(), nullable=True),
    sa.ForeignKeyConstraint(['api_key_id'], ['LLMAPIKey.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_LLMUsage_api_key_id'), 'LLMUsage', ['api_key_id'], unique=False)
    op.create_index(op.f('ix_LLMUsage_batch_job_id'), 'LLMUsage', ['batch_job_id'], unique=False)
    op.create_index(op.f('ix_LLMUsage_group_id'), 'LLMUsage', ['group_id'], unique=False)
    op.create_index(op.f('ix_LLMUsage_id'), 'LLMUsage', ['id'], unique=False)
    op.create_index(op.f('ix_LLMUsage_tenant_id'), 'LLMUsage', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_LLMUsage_timestamp'), 'LLMUsage', ['timestamp'], unique=False)
    op.create_index(op.f('ix_LLMUsage_user_id'), 'LLMUsage', ['user_id'], unique=False)
    op.create_index(op.f('ix_LLMUsage_vendor_request_id'), 'LLMUsage', ['vendor_request_id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_LLMUsage_vendor_request_id'), table_name='LLMUsage')
    op.drop_index(op.f('ix_LLMUsage_user_id'), table_name='LLMUsage')
    op.drop_index(op.f('ix_LLMUsage_timestamp'), table_name='LLMUsage')
    op.drop_index(op.f('ix_LLMUsage_tenant_id'), table_name='LLMUsage')
    op.drop_index(op.f('ix_LLMUsage_id'), table_name='LLMUsage')
    op.drop_index(op.f('ix_LLMUsage_group_id'), table_name='LLMUsage')
    op.drop_index(op.f('ix_LLMUsage_batch_job_id'), table_name='LLMUsage')
    op.drop_index(op.f('ix_LLMUsage_api_key_id'), table_name='LLMUsage')
    op.drop_table('LLMUsage')
    op.drop_index(op.f('ix_LLMErrorLog_vendor_request_id'), table_name='LLMErrorLog')
    op.drop_index(op.f('ix_LLMErrorLog_timestamp'), table_name='LLMErrorLog')
    op.drop_index(op.f('ix_LLMErrorLog_request_id'), table_name='LLMErrorLog')
    op.drop_index(op.f('ix_LLMErrorLog_id'), table_name='LLMErrorLog')
    op.drop_index(op.f('ix_LLMErrorLog_batch_job_id'), table_name='LLMErrorLog')
    op.drop_index(op.f('ix_LLMErrorLog_api_key_id'), table_name='LLMErrorLog')
    op.drop_table('LLMErrorLog')
    op.drop_index(op.f('ix_UserFeedback_tenant_id'), table_name='UserFeedback')
    op.drop_index(op.f('ix_UserFeedback_team_id'), table_name='UserFeedback')
    op.drop_index(op.f('ix_UserFeedback_session_id'), table_name='UserFeedback')
    op.drop_index(op.f('ix_UserFeedback_id'), table_name='UserFeedback')
    op.drop_table('UserFeedback')
    op.drop_index(op.f('ix_LLMAPIKey_id'), table_name='LLMAPIKey')
    op.drop_index(op.f('ix_LLMAPIKey_api_key'), table_name='LLMAPIKey')
    op.drop_table('LLMAPIKey')
    op.drop_index(op.f('ix_GroundTruthItem_tenant_id'), table_name='GroundTruthItem')
    op.drop_index(op.f('ix_GroundTruthItem_id'), table_name='GroundTruthItem')
    op.drop_index(op.f('ix_GroundTruthItem_dataset_id'), table_name='GroundTruthItem')
    op.drop_table('GroundTruthItem')
    op.drop_index(op.f('ix_GroundTruthDataset_task_id'), table_name='GroundTruthDataset')
    op.drop_index(op.f('ix_GroundTruthDataset_id'), table_name='GroundTruthDataset')
    op.drop_table('GroundTruthDataset')
    op.drop_index(op.f('ix_EvaluationResult_team_id'), table_name='EvaluationResult')
    op.drop_index(op.f('ix_EvaluationResult_session_id'), table_name='EvaluationResult')
    op.drop_index(op.f('ix_EvaluationResult_metric_name'), table_name='EvaluationResult')
    op.drop_index(op.f('ix_EvaluationResult_job_id'), table_name='EvaluationResult')
    op.drop_index(op.f('ix_EvaluationResult_id'), table_name='EvaluationResult')
    op.drop_table('EvaluationResult')
    op.drop_index(op.f('ix_EvaluationJob_tenant_id'), table_name='EvaluationJob')
    op.drop_index(op.f('ix_EvaluationJob_task_id'), table_name='EvaluationJob')
    op.drop_index(op.f('ix_EvaluationJob_id'), table_name='EvaluationJob')
    op.drop_index(op.f('ix_EvaluationJob_dataset_id'), table_name='EvaluationJob')
    op.drop_table('EvaluationJob')
    op.drop_index(op.f('ix_EvaluationCache_input_hash'), table_name='EvaluationCache')
    op.drop_index(op.f('ix_EvaluationCache_id'), table_name='EvaluationCache')
    op.drop_index(op.f('ix_EvaluationCache_evaluator_config_hash'), table_name='EvaluationCache')
    op.drop_table('EvaluationCache')
    # ### end Alembic commands ###
