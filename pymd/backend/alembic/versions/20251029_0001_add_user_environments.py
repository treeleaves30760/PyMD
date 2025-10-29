"""Add user environments tables

Revision ID: 20251029_0001
Revises: 20250118_0000
Create Date: 2025-10-29 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '20251029_0001'
down_revision: Union[str, None] = '20250118_0000'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create user_environments table
    op.create_table(
        'user_environments',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('python_version', sa.String(length=20), nullable=False, server_default='3.11'),
        sa.Column('volume_name', sa.String(length=255), nullable=False),
        sa.Column('status', sa.Enum('ACTIVE', 'CREATING', 'ERROR', 'DELETED', name='environmentstatus'), nullable=False, server_default='ACTIVE'),
        sa.Column('total_size_bytes', sa.BigInteger(), nullable=False, server_default='0'),
        sa.Column('package_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_used_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_env_user_id', 'user_environments', ['user_id'], unique=False)
    op.create_index('idx_env_last_used', 'user_environments', ['last_used_at'], unique=False)
    op.create_index('idx_env_user_name', 'user_environments', ['user_id', 'name'], unique=True)
    op.create_index(op.f('ix_user_environments_volume_name'), 'user_environments', ['volume_name'], unique=True)

    # Create environment_packages table
    op.create_table(
        'environment_packages',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('environment_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('package_name', sa.String(length=255), nullable=False),
        sa.Column('version', sa.String(length=100), nullable=True),
        sa.Column('size_bytes', sa.BigInteger(), nullable=True),
        sa.Column('installed_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['environment_id'], ['user_environments.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_pkg_env_id', 'environment_packages', ['environment_id'], unique=False)
    op.create_index('idx_pkg_env_name', 'environment_packages', ['environment_id', 'package_name'], unique=True)

    # Create environment_executions table
    op.create_table(
        'environment_executions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('environment_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('document_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('status', sa.Enum('QUEUED', 'RUNNING', 'COMPLETED', 'FAILED', 'TIMEOUT', 'CANCELLED', name='executionstatus'), nullable=False, server_default='QUEUED'),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('execution_time_ms', sa.Integer(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['environment_id'], ['user_environments.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_exec_env_id', 'environment_executions', ['environment_id'], unique=False)
    op.create_index('idx_exec_doc_id', 'environment_executions', ['document_id'], unique=False)
    op.create_index('idx_exec_status', 'environment_executions', ['status'], unique=False)
    op.create_index('idx_exec_created', 'environment_executions', ['started_at'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index('idx_exec_created', table_name='environment_executions')
    op.drop_index('idx_exec_status', table_name='environment_executions')
    op.drop_index('idx_exec_doc_id', table_name='environment_executions')
    op.drop_index('idx_exec_env_id', table_name='environment_executions')
    op.drop_table('environment_executions')
    op.execute("DROP TYPE IF EXISTS executionstatus")

    op.drop_index('idx_pkg_env_name', table_name='environment_packages')
    op.drop_index('idx_pkg_env_id', table_name='environment_packages')
    op.drop_table('environment_packages')

    op.drop_index(op.f('ix_user_environments_volume_name'), table_name='user_environments')
    op.drop_index('idx_env_user_name', table_name='user_environments')
    op.drop_index('idx_env_last_used', table_name='user_environments')
    op.drop_index('idx_env_user_id', table_name='user_environments')
    op.drop_table('user_environments')
    op.execute("DROP TYPE IF EXISTS environmentstatus")
