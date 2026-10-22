"""Transactional task routing application service."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from company_os.db.models.task import TaskAuditEventRecord, TaskRecord
from company_os.domain.task_router import (
    DeterministicTaskRouter,
    RoutingDecision,
    RoutingStatus,
)
from company_os.domain.task_state import (
    TERMINAL_TASK_STATES,
    ActorType,
    TaskStatus,
)
from company_os.services.task_lifecycle import (
    InvalidTaskTransition,
    TaskNotFound,
)


def route_task(
    session: Session,
    *,
    task_id: UUID,
    router: DeterministicTaskRouter | None = None,
    actor_id: str = "system:router",
    request_id: str | None = None,
) -> tuple[TaskRecord, RoutingDecision]:
    """Deterministically route a task to an approved specialist and record the decision.

    The task must exist and not be in a terminal state.
    On successful routing:
      - task.assigned_agent_id is set to the selected agent ID
      - task.routing_decision is recorded
      - task state transitions from queued to ready
      - audit event 'task.routed' is persisted
    On unsupported, ambiguous, or unavailable routing:
      - task.assigned_agent_id remains None
      - task.routing_decision is recorded
      - task transitions to blocked with appropriate last_error_code
      - audit event 'task.routing_failed' is persisted

    Flushes within the caller's transaction; caller commits or rolls back.
    """
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
        current_status = TaskStatus(task.status)
    except ValueError as exc:
        raise InvalidTaskTransition(
            f"Persisted task status is unknown: {task.status!r}"
        ) from exc

    if current_status in TERMINAL_TASK_STATES:
        raise InvalidTaskTransition(
            f"Task {task_id} is in terminal state {task.status!r} and cannot be routed"
        )

    active_router = router or DeterministicTaskRouter()
    decision = active_router.resolve(
        objective=task.objective,
        input_payload=task.input_payload,
    )

    now = datetime.now(UTC)
    prior_status = task.status
    prior_version = task.version
    new_version = prior_version + 1

    task.version = new_version
    task.updated_at = now
    task.routing_decision = decision.to_dict()

    if decision.status == RoutingStatus.ROUTED:
        target_status = TaskStatus.READY
        task.assigned_agent_id = decision.selected_agent_id
        task.status = target_status.value
        task.last_error_code = None
        task.last_error_message = None
        action = "task.routed"
    else:
        target_status = TaskStatus.BLOCKED
        task.assigned_agent_id = None
        task.status = target_status.value
        if decision.status == RoutingStatus.AGENT_UNAVAILABLE:
            task.last_error_code = "AGENT_UNAVAILABLE"
        elif decision.status == RoutingStatus.AMBIGUOUS:
            task.last_error_code = "ROUTING_AMBIGUOUS"
        else:
            task.last_error_code = "ROUTING_UNSUPPORTED"
        task.last_error_message = decision.reason
        action = "task.routing_failed"

    session.add(
        TaskAuditEventRecord(
            task_id=task.id,
            actor_type=ActorType.SYSTEM.value,
            actor_id=actor_id,
            action=action,
            from_status=prior_status,
            to_status=target_status.value,
            from_version=prior_version,
            to_version=new_version,
            reason=decision.reason,
            event_data=decision.to_dict(),
            request_id=request_id,
        )
    )

    session.flush()
    return task, decision
