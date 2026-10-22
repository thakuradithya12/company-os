
"""Transactional task creation and state-transition services."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from company_os.db.models.task import TaskAuditEventRecord, TaskRecord
from company_os.domain.task_state import ActorType, TaskStatus, can_transition_task


class TaskLifecycleError(Exception):
    """Base class for expected task lifecycle rejections."""


class TaskNotFound(TaskLifecycleError):
    """Raised when a requested task does not exist."""


class InvalidTaskTransition(TaskLifecycleError):
    """Raised when a task transition is not allowed."""


class StaleTaskVersion(TaskLifecycleError):
    """Raised when a command was based on an outdated task version."""


class CompletionVerificationRequired(TaskLifecycleError):
    """Raised when completion lacks passing acceptance evidence."""


def _parse_status(value: TaskStatus | str) -> TaskStatus:
    try:
        return value if isinstance(value, TaskStatus) else TaskStatus(value)
    except ValueError as exc:
        raise InvalidTaskTransition(f"Unknown task status: {value!r}") from exc


def _parse_actor(value: ActorType | str) -> ActorType:
    try:
        return value if isinstance(value, ActorType) else ActorType(value)
    except ValueError as exc:
        raise ValueError(f"Unknown actor type: {value!r}") from exc


def create_task(
    session: Session,
    *,
    objective: str,
    created_by: str,
    input_payload: dict[str, Any] | None = None,
    acceptance_criteria: list[dict[str, Any]] | None = None,
    priority: int = 100,
    max_attempts: int = 3,
    deadline_at: datetime | None = None,
    actor_type: ActorType | str = ActorType.FOUNDER,
    request_id: str | None = None,
) -> TaskRecord:
    """Add a queued task and its creation audit event to the caller's transaction.

    This function flushes but never commits; callers decide transaction boundaries.
    """
    normalized_objective = objective.strip()
    normalized_actor_id = created_by.strip()

    if not normalized_objective:
        raise ValueError("objective must not be empty")
    if not normalized_actor_id:
        raise ValueError("created_by must not be empty")
    if max_attempts < 1:
        raise ValueError("max_attempts must be at least 1")

    actor = _parse_actor(actor_type)

    task = TaskRecord(
        objective=normalized_objective,
        status=TaskStatus.QUEUED.value,
        created_by=normalized_actor_id,
        priority=priority,
        input_payload=input_payload or {},
        acceptance_criteria=acceptance_criteria or [],
        max_attempts=max_attempts,
        version=1,
        deadline_at=deadline_at,
    )

    session.add(task)
    session.flush()

    session.add(
        TaskAuditEventRecord(
            task_id=task.id,
            actor_type=actor.value,
            actor_id=normalized_actor_id,
            action="task.created",
            from_status=None,
            to_status=TaskStatus.QUEUED.value,
            from_version=None,
            to_version=1,
            reason="Task accepted into the canonical task system",
            event_data={
                "priority": priority,
                "max_attempts": max_attempts,
            },
            request_id=request_id,
        )
    )

    session.flush()
    return task


def transition_task(
    session: Session,
    *,
    task_id: UUID,
    target_status: TaskStatus | str,
    actor_type: ActorType | str,
    actor_id: str,
    reason: str,
    expected_version: int,
    request_id: str | None = None,
    error_code: str | None = None,
    error_message: str | None = None,
    verification_evidence: dict[str, Any] | None = None,
) -> TaskRecord:
    """Apply one version-checked state transition with an audit record atomically.

    The caller must commit or roll back the session. Completion requires passing
    acceptance checks and a non-empty evidence reference; model-generated completion
    text alone is not sufficient.
    """
    normalized_reason = reason.strip()
    normalized_actor_id = actor_id.strip()

    if not normalized_reason:
        raise ValueError("reason must not be empty")
    if not normalized_actor_id:
        raise ValueError("actor_id must not be empty")
    if expected_version < 1:
        raise ValueError("expected_version must be at least 1")

    target = _parse_status(target_status)
    actor = _parse_actor(actor_type)

    statement = (
        select(TaskRecord)
        .where(TaskRecord.id == task_id)
        .with_for_update()
        .execution_options(populate_existing=True)
    )

    task = session.scalars(statement).one_or_none()
    if task is None:
        raise TaskNotFound(f"Task {task_id} was not found")

    try:
        current = TaskStatus(task.status)
    except ValueError as exc:
        raise InvalidTaskTransition(
            f"Persisted task status is unknown: {task.status!r}"
        ) from exc

    if task.version != expected_version:
        raise StaleTaskVersion(
            f"Task {task_id} has version {task.version}; "
            f"command expected {expected_version}"
        )

    if not can_transition_task(current, target):
        raise InvalidTaskTransition(
            f"Transition {current.value!r} -> {target.value!r} is not allowed"
        )

    if target is TaskStatus.COMPLETED:
        evidence = verification_evidence or {}
        checks = evidence.get("checks")
        evidence_ref = evidence.get("evidence_ref")

        if (
            evidence.get("passed") is not True
            or not isinstance(checks, list)
            or not checks
        ):
            raise CompletionVerificationRequired(
                "A completed task requires passed acceptance checks "
                "and an evidence reference"
            )

        if not isinstance(evidence_ref, str) or not evidence_ref.strip():
            raise CompletionVerificationRequired(
                "A completed task requires a non-empty evidence_ref"
            )

    now = datetime.now(UTC)

    values: dict[str, Any] = {
        "status": target.value,
        "version": expected_version + 1,
        "updated_at": now,
        "last_error_code": error_code,
        "last_error_message": error_message,
    }

    if target is TaskStatus.RUNNING and task.started_at is None:
        values["started_at"] = now

    if target is TaskStatus.CANCEL_REQUESTED:
        values["cancel_requested_at"] = now

    if target is TaskStatus.COMPLETED:
        values["completed_at"] = now

    result = session.execute(
        update(TaskRecord)
        .where(
            TaskRecord.id == task_id,
            TaskRecord.version == expected_version,
            TaskRecord.status == current.value,
        )
        .values(**values)
        .execution_options(synchronize_session=False)
    )

    if result.rowcount != 1:
        raise StaleTaskVersion(
            f"Task {task_id} changed while the transition was being applied; "
            "reload and retry"
        )

    task.status = target.value
    task.version = expected_version + 1
    task.updated_at = now

    if "started_at" in values:
        task.started_at = now

    if "cancel_requested_at" in values:
        task.cancel_requested_at = now

    if "completed_at" in values:
        task.completed_at = now

    task.last_error_code = error_code
    task.last_error_message = error_message

    event_data: dict[str, Any] = {}

    if target is TaskStatus.COMPLETED:
        # Persist references and check outcomes, not arbitrary output contents or secrets.
        event_data["verification"] = verification_evidence

    if error_code:
        event_data["error_code"] = error_code

    session.add(
        TaskAuditEventRecord(
            task_id=task.id,
            actor_type=actor.value,
            actor_id=normalized_actor_id,
            action="task.transitioned",
            from_status=current.value,
            to_status=target.value,
            from_version=expected_version,
            to_version=expected_version + 1,
            reason=normalized_reason,
            event_data=event_data,
            request_id=request_id,
        )
    )

    session.flush()
    return task
