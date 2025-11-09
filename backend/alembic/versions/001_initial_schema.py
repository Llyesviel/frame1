"""Initial schema with all tables

Revision ID: 001
Revises: 
Create Date: 2024-11-09 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create roles table
    op.create_table(
        'roles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_roles')),
        sa.UniqueConstraint('name', name=op.f('uq_roles_name'))
    )
    op.create_index(op.f('ix_name'), 'roles', ['name'], unique=True)

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], name=op.f('fk_users_role_id_roles')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_users')),
        sa.UniqueConstraint('email', name=op.f('uq_users_email'))
    )
    op.create_index(op.f('ix_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_role_id'), 'users', ['role_id'], unique=False)
    op.create_index(op.f('ix_is_active'), 'users', ['is_active'], unique=False)

    # Create projects table
    op.create_table(
        'projects',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('manager_id', sa.Integer(), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['manager_id'], ['users.id'], name=op.f('fk_projects_manager_id_users')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_projects'))
    )
    op.create_index(op.f('ix_manager_id'), 'projects', ['manager_id'], unique=False)
    op.create_index(op.f('ix_start_date'), 'projects', ['start_date'], unique=False)
    op.create_index(op.f('ix_end_date'), 'projects', ['end_date'], unique=False)

    # Create project_stages table
    op.create_table(
        'project_stages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], name=op.f('fk_project_stages_project_id_projects')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_project_stages'))
    )
    op.create_index(op.f('ix_project_id'), 'project_stages', ['project_id'], unique=False)
    op.create_index('ix_project_stages_project_id_name', 'project_stages', ['project_id', 'name'], unique=False)

    # Create defect_statuses table
    op.create_table(
        'defect_statuses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_defect_statuses')),
        sa.UniqueConstraint('name', name=op.f('uq_defect_statuses_name'))
    )
    op.create_index(op.f('ix_name'), 'defect_statuses', ['name'], unique=True)

    # Create defects table
    op.create_table(
        'defects',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('stage_id', sa.Integer(), nullable=True),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('priority', sa.Enum('low', 'medium', 'high', 'critical', name='priorityenum'), nullable=False),
        sa.Column('status_id', sa.Integer(), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('assigned_to', sa.Integer(), nullable=True),
        sa.Column('due_date', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint('length(title) <= 255', name=op.f('ck_defects_title_length')),
        sa.ForeignKeyConstraint(['assigned_to'], ['users.id'], name=op.f('fk_defects_assigned_to_users')),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], name=op.f('fk_defects_created_by_users')),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], name=op.f('fk_defects_project_id_projects')),
        sa.ForeignKeyConstraint(['stage_id'], ['project_stages.id'], name=op.f('fk_defects_stage_id_project_stages')),
        sa.ForeignKeyConstraint(['status_id'], ['defect_statuses.id'], name=op.f('fk_defects_status_id_defect_statuses')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_defects'))
    )
    op.create_index(op.f('ix_project_id'), 'defects', ['project_id'], unique=False)
    op.create_index(op.f('ix_stage_id'), 'defects', ['stage_id'], unique=False)
    op.create_index(op.f('ix_status_id'), 'defects', ['status_id'], unique=False)
    op.create_index(op.f('ix_created_by'), 'defects', ['created_by'], unique=False)
    op.create_index(op.f('ix_assigned_to'), 'defects', ['assigned_to'], unique=False)
    op.create_index(op.f('ix_priority'), 'defects', ['priority'], unique=False)
    op.create_index(op.f('ix_due_date'), 'defects', ['due_date'], unique=False)
    op.create_index('ix_defects_project_id_status_id', 'defects', ['project_id', 'status_id'], unique=False)

    # Create comments table
    op.create_table(
        'comments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('defect_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['defect_id'], ['defects.id'], name=op.f('fk_comments_defect_id_defects'), ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_comments_user_id_users')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_comments'))
    )
    op.create_index(op.f('ix_defect_id'), 'comments', ['defect_id'], unique=False)
    op.create_index(op.f('ix_user_id'), 'comments', ['user_id'], unique=False)
    op.create_index(op.f('ix_created_at'), 'comments', ['created_at'], unique=False)

    # Create attachments table
    op.create_table(
        'attachments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('defect_id', sa.Integer(), nullable=False),
        sa.Column('file_name', sa.String(length=255), nullable=False),
        sa.Column('file_path', sa.String(length=512), nullable=False),
        sa.Column('uploaded_by', sa.Integer(), nullable=False),
        sa.Column('uploaded_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.ForeignKeyConstraint(['defect_id'], ['defects.id'], name=op.f('fk_attachments_defect_id_defects'), ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['uploaded_by'], ['users.id'], name=op.f('fk_attachments_uploaded_by_users')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_attachments'))
    )
    op.create_index(op.f('ix_defect_id'), 'attachments', ['defect_id'], unique=False)
    op.create_index(op.f('ix_uploaded_by'), 'attachments', ['uploaded_by'], unique=False)
    op.create_index(op.f('ix_is_deleted'), 'attachments', ['is_deleted'], unique=False)

    # Create history_logs table
    op.create_table(
        'history_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('defect_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('action_type', sa.Enum('CREATE', 'UPDATE', 'STATUS_CHANGE', 'COMMENT_ADDED', name='actiontypeenum'), nullable=False),
        sa.Column('old_value', sa.Text(), nullable=True),
        sa.Column('new_value', sa.Text(), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['defect_id'], ['defects.id'], name=op.f('fk_history_logs_defect_id_defects'), ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_history_logs_user_id_users')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_history_logs'))
    )
    op.create_index(op.f('ix_defect_id'), 'history_logs', ['defect_id'], unique=False)
    op.create_index(op.f('ix_user_id'), 'history_logs', ['user_id'], unique=False)
    op.create_index(op.f('ix_action_type'), 'history_logs', ['action_type'], unique=False)
    op.create_index(op.f('ix_timestamp'), 'history_logs', ['timestamp'], unique=False)
    op.create_index('ix_history_logs_defect_id_timestamp', 'history_logs', ['defect_id', 'timestamp'], unique=False)

    # Create reports table
    op.create_table(
        'reports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('report_type', sa.String(length=100), nullable=False),
        sa.Column('generated_by', sa.Integer(), nullable=False),
        sa.Column('file_path', sa.String(length=512), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['generated_by'], ['users.id'], name=op.f('fk_reports_generated_by_users')),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], name=op.f('fk_reports_project_id_projects')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_reports'))
    )
    op.create_index(op.f('ix_project_id'), 'reports', ['project_id'], unique=False)
    op.create_index(op.f('ix_generated_by'), 'reports', ['generated_by'], unique=False)
    op.create_index(op.f('ix_report_type'), 'reports', ['report_type'], unique=False)
    op.create_index(op.f('ix_created_at'), 'reports', ['created_at'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('reports')
    op.drop_table('history_logs')
    op.drop_table('attachments')
    op.drop_table('comments')
    op.drop_table('defects')
    op.drop_table('defect_statuses')
    op.drop_table('project_stages')
    op.drop_table('projects')
    op.drop_table('users')
    op.drop_table('roles')
    
    # Drop enum types
    op.execute('DROP TYPE IF EXISTS actiontypeenum')
    op.execute('DROP TYPE IF EXISTS priorityenum')
