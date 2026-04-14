"""add agent_type to tasks

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-04-15
"""
from alembic import op
import sqlalchemy as sa

revision = 'c3d4e5f6a7b8'
down_revision = 'b2c3d4e5f6a7'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('tasks', sa.Column('agent_type', sa.String(), nullable=True))


def downgrade():
    op.drop_column('tasks', 'agent_type')
