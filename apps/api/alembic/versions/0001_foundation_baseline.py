"""Initial migration baseline; domain tables are intentionally deferred.

Revision ID: 0001_foundation_baseline
Revises:
Create Date: 2026-10-21
"""

from __future__ import annotations

from collections.abc import Sequence

revision: str = "0001_foundation_baseline"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Establish the migration baseline without prematurely deciding domain tables."""
    # Alembic creates and maintains its version table. Task, agent, CRM, and memory
    # tables are added only in their approved platform work packages.
    pass


def downgrade() -> None:
    """The baseline has no domain changes to reverse."""
    pass
