"""Add canonical task records and task transition audit trail.

Revision ID: 0002_task_lifecycle_core
Revises: 0001_foundation_baseline
Create Date: 2026-10-21
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002_task_lifecycle_core"
down_revision: str | None = "0001_foundation_baseline"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create the durable task record and append-only-by-contract audit table."""
    op.create_table(
        "tasks",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("objective", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=32), server_default="queued", nullable=False),
        sa.Column("created_by", sa.String(length=128), nullable=False),
        sa.Column("priority", sa.Integer(), server_default="100", nullable=False),
        sa.Column("input_payload", sa.JSON(), nullable=False),
        sa.Column("acceptance_criteria", sa.JSON(), nullable=False),
        sa.Column("attempt_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("max_attempts", sa.Integer(), server_default="3", nullable=False),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.Column("deadline_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancel_requested_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_error_code", sa.String(length=80), nullable=True),
        sa.Column("last_error_message", sa.Text(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint(
            "status IN ('queued', 'planning', 'ready', 'running', 'awaiting_approval', "
            "'verifying', 'rework', 'blocked', 'completed', 'failed', 'cancel_requested', "
            "'cancelled', 'unknown_outcome')",
            name="ck_tasks_status",
        ),
        sa.CheckConstraint("version >= 1", name="ck_tasks_version_positive"),
        sa.CheckConstraint("attempt_count >= 0", name="ck_tasks_attempt_count_nonnegative"),
        sa.CheckConstraint("max_attempts >= 1", name="ck_tasks_max_attempts_positive"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_tasks_status_created_at", "tasks", ["status", "created_at"])

    op.create_table(
        "task_audit_events",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("task_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("actor_type", sa.String(length=20), nullable=False),
        sa.Column("actor_id", sa.String(length=128), nullable=False),
        sa.Column("action", sa.String(length=80), nullable=False),
        sa.Column("from_status", sa.String(length=32), nullable=True),
        sa.Column("to_status", sa.String(length=32), nullable=True),
        sa.Column("from_version", sa.Integer(), nullable=True),
        sa.Column("to_version", sa.Integer(), nullable=True),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("event_data", sa.JSON(), nullable=False),
        sa.Column("request_id", sa.String(length=128), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint(
            "actor_type IN ('founder', 'system', 'agent', 'service')",
            name="ck_task_audit_events_actor_type",
        ),
        sa.ForeignKeyConstraint(["task_id"], ["tasks.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_task_audit_events_task_created_at", "task_audit_events", ["task_id", "created_at"]
    )


def downgrade() -> None:
    """Remove only objects introduced by this revision."""
    op.drop_index("ix_task_audit_events_task_created_at", table_name="task_audit_events")
    op.drop_table("task_audit_events")
    op.drop_index("ix_tasks_status_created_at", table_name="tasks")
    op.drop_table("tasks")
