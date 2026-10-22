"""Durable task and task-audit persistence records."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import (
    JSON,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from company_os.db.base import Base
from company_os.domain.task_state import ActorType, TaskStatus

_TASK_STATUS_SQL = ", ".join(f"'{status.value}'" for status in TaskStatus)
_ACTOR_TYPE_SQL = ", ".join(f"'{actor.value}'" for actor in ActorType)


class TaskRecord(Base):
    """Canonical database record for an objective-sized task."""

    __tablename__ = "tasks"
    __table_args__ = (
        CheckConstraint(f"status IN ({_TASK_STATUS_SQL})", name="ck_tasks_status"),
        CheckConstraint("version >= 1", name="ck_tasks_version_positive"),
        CheckConstraint("attempt_count >= 0", name="ck_tasks_attempt_count_nonnegative"),
        CheckConstraint("max_attempts >= 1", name="ck_tasks_max_attempts_positive"),
        Index("ix_tasks_status_created_at", "status", "created_at"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    objective: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, default=TaskStatus.QUEUED.value,
        server_default=TaskStatus.QUEUED.value,
    )
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    priority: Mapped[int] = mapped_column(
        Integer, nullable=False, default=100, server_default="100"
    )
    input_payload: Mapped[dict[str, Any]] = mapped_column(
        JSON, nullable=False, default=dict
    )
    acceptance_criteria: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON, nullable=False, default=list
    )
    attempt_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )
    max_attempts: Mapped[int] = mapped_column(
        Integer, nullable=False, default=3, server_default="3"
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1, server_default="1")
    deadline_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cancel_requested_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_error_code: Mapped[str | None] = mapped_column(String(80), nullable=True)
    last_error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    audit_events: Mapped[list[TaskAuditEventRecord]] = relationship(
        back_populates="task", order_by="TaskAuditEventRecord.created_at", passive_deletes=True
    )


class TaskAuditEventRecord(Base):
    """Append-only-by-contract audit entry for a task command or state change."""

    __tablename__ = "task_audit_events"
    __table_args__ = (
        CheckConstraint(
            f"actor_type IN ({_ACTOR_TYPE_SQL})", name="ck_task_audit_events_actor_type"
        ),
        Index("ix_task_audit_events_task_created_at", "task_id", "created_at"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    task_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("tasks.id", ondelete="RESTRICT"),
        nullable=False,
    )
    actor_type: Mapped[str] = mapped_column(String(20), nullable=False)
    actor_id: Mapped[str] = mapped_column(String(128), nullable=False)
    action: Mapped[str] = mapped_column(String(80), nullable=False)
    from_status: Mapped[str | None] = mapped_column(String(32), nullable=True)
    to_status: Mapped[str | None] = mapped_column(String(32), nullable=True)
    from_version: Mapped[int | None] = mapped_column(Integer, nullable=True)
    to_version: Mapped[int | None] = mapped_column(Integer, nullable=True)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    event_data: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    request_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    task: Mapped[TaskRecord] = relationship(back_populates="audit_events")
