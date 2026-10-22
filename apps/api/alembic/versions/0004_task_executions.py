"""Add task_executions table for controlled execution tracking.

Revision ID: 0004_task_executions
Revises: 0003_task_agent_routing
Create Date: 2026-10-22
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0004_task_executions"
down_revision: str | None = "0003_task_agent_routing"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create task_executions table."""
    op.create_table(
        "task_executions",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("task_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("agent_id", sa.String(length=32), nullable=False),
        sa.Column("tool_id", sa.String(length=80), nullable=False),
        sa.Column("risk_tier", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=32), server_default="running", nullable=False),
        sa.Column("input_parameters", sa.JSON(), nullable=False),
        sa.Column("output_payload", sa.JSON(), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("evidence_reference", sa.String(length=256), nullable=True),
        sa.Column("verification_checks", sa.JSON(), nullable=False),
        sa.Column("duration_ms", sa.Integer(), server_default="0", nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint(
            "status IN ('running', 'completed', 'failed', 'blocked', 'interrupted')",
            name="ck_task_executions_status",
        ),
        sa.CheckConstraint(
            "risk_tier IN ('tier_0_read_only', 'tier_1_reversible', 'tier_2_high_impact')",
            name="ck_task_executions_risk_tier",
        ),
        sa.ForeignKeyConstraint(["task_id"], ["tasks.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_task_executions_task_id", "task_executions", ["task_id"])
    op.create_index("ix_task_executions_status", "task_executions", ["status"])


def downgrade() -> None:
    """Drop task_executions table."""
    op.drop_index("ix_task_executions_status", table_name="task_executions")
    op.drop_index("ix_task_executions_task_id", table_name="task_executions")
    op.drop_table("task_executions")
