"""project workflow — cahier_de_charge, approval flow, subtasks

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-04-14 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new values to project_status enum (PostgreSQL only allows ADD VALUE)
    op.execute("ALTER TYPE project_status ADD VALUE IF NOT EXISTS 'pending_approval'")
    op.execute("ALTER TYPE project_status ADD VALUE IF NOT EXISTS 'approved'")

    # Add cahier_de_charge and rejection_note to projects
    op.add_column('projects', sa.Column('cahier_de_charge', sa.Text(), nullable=True))
    op.add_column('projects', sa.Column('rejection_note', sa.String(), nullable=True))

    # Add parent_task_id to tasks (subtasks)
    op.add_column('tasks', sa.Column('parent_task_id', sa.UUID(), nullable=True))
    op.create_foreign_key('fk_tasks_parent_task_id', 'tasks', 'tasks', ['parent_task_id'], ['id'])


def downgrade() -> None:
    op.drop_constraint('fk_tasks_parent_task_id', 'tasks', type_='foreignkey')
    op.drop_column('tasks', 'parent_task_id')
    op.drop_column('projects', 'rejection_note')
    op.drop_column('projects', 'cahier_de_charge')
    # Note: PostgreSQL does not support removing enum values — manual rollback needed
