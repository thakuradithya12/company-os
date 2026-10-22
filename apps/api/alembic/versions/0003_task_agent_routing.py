"""Add assigned_agent_id and routing_decision to tasks.

Revision ID: 0003_task_agent_routing
Revises: 0002_task_lifecycle_core
Create Date: 2026-10-22
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0003_task_agent_routing"
down_revision: str | None = "0002_task_lifecycle_core"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add assigned_agent_id and routing_decision columns to tasks."""
    op.add_column("tasks", sa.Column("assigned_agent_id", sa.String(length=32), nullable=True))
    op.add_column("tasks", sa.Column("routing_decision", sa.JSON(), nullable=True))
    op.create_index("ix_tasks_assigned_agent_id", "tasks", ["assigned_agent_id"])


def downgrade() -> None:
    """Remove assigned_agent_id and routing_decision columns from tasks."""
    op.drop_index("ix_tasks_assigned_agent_id", table_name="tasks")
    op.drop_column("tasks", "routing_decision")
    op.drop_column("tasks", "assigned_agent_id")
