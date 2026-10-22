
"""Canonical task states and legal transitions.

This module is deliberately independent of SQLAlchemy, FastAPI, and model providers so
state-machine behavior can be tested without infrastructure.
"""

from __future__ import annotations

from enum import StrEnum


class TaskStatus(StrEnum):
    QUEUED = "queued"
    PLANNING = "planning"
    READY = "ready"
    RUNNING = "running"
    AWAITING_APPROVAL = "awaiting_approval"
    VERIFYING = "verifying"
    REWORK = "rework"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCEL_REQUESTED = "cancel_requested"
    CANCELLED = "cancelled"
    UNKNOWN_OUTCOME = "unknown_outcome"


class ActorType(StrEnum):
    FOUNDER = "founder"
    SYSTEM = "system"
    AGENT = "agent"
    SERVICE = "service"


TERMINAL_TASK_STATES = frozenset(
    {TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED}
)

ALLOWED_TASK_TRANSITIONS: dict[TaskStatus, frozenset[TaskStatus]] = {
    TaskStatus.QUEUED: frozenset(
        {
            TaskStatus.PLANNING,
            TaskStatus.READY,
            TaskStatus.BLOCKED,
            TaskStatus.FAILED,
            TaskStatus.CANCEL_REQUESTED,
        }
    ),
    TaskStatus.PLANNING: frozenset(
        {
            TaskStatus.READY,
            TaskStatus.BLOCKED,
            TaskStatus.FAILED,
            TaskStatus.CANCEL_REQUESTED,
        }
    ),
    TaskStatus.READY: frozenset(
        {
            TaskStatus.RUNNING,
            TaskStatus.BLOCKED,
            TaskStatus.FAILED,
            TaskStatus.CANCEL_REQUESTED,
        }
    ),
    TaskStatus.RUNNING: frozenset(
        {
            TaskStatus.AWAITING_APPROVAL,
            TaskStatus.VERIFYING,
            TaskStatus.REWORK,
            TaskStatus.BLOCKED,
            TaskStatus.FAILED,
            TaskStatus.CANCEL_REQUESTED,
            TaskStatus.UNKNOWN_OUTCOME,
        }
    ),
    TaskStatus.AWAITING_APPROVAL: frozenset(
        {
            TaskStatus.READY,
            TaskStatus.BLOCKED,
            TaskStatus.FAILED,
            TaskStatus.CANCEL_REQUESTED,
        }
    ),
    TaskStatus.VERIFYING: frozenset(
        {
            TaskStatus.COMPLETED,
            TaskStatus.REWORK,
            TaskStatus.BLOCKED,
            TaskStatus.FAILED,
            TaskStatus.CANCEL_REQUESTED,
        }
    ),
    TaskStatus.REWORK: frozenset(
        {
            TaskStatus.READY,
            TaskStatus.RUNNING,
            TaskStatus.BLOCKED,
            TaskStatus.FAILED,
            TaskStatus.CANCEL_REQUESTED,
        }
    ),
    TaskStatus.BLOCKED: frozenset(
        {
            TaskStatus.QUEUED,
            TaskStatus.PLANNING,
            TaskStatus.READY,
            TaskStatus.FAILED,
            TaskStatus.CANCEL_REQUESTED,
        }
    ),
    TaskStatus.CANCEL_REQUESTED: frozenset(
        {
            TaskStatus.CANCELLED,
            TaskStatus.UNKNOWN_OUTCOME,
            TaskStatus.BLOCKED,
        }
    ),
    # Reconciliation is required; unknown outcomes cannot jump directly back to execution.
    TaskStatus.UNKNOWN_OUTCOME: frozenset(
        {
            TaskStatus.VERIFYING,
            TaskStatus.BLOCKED,
            TaskStatus.FAILED,
            TaskStatus.CANCELLED,
        }
    ),
    TaskStatus.COMPLETED: frozenset(),
    TaskStatus.FAILED: frozenset(),
    TaskStatus.CANCELLED: frozenset(),
}


def can_transition_task(current: TaskStatus, target: TaskStatus) -> bool:
    """Return whether a transition is explicitly allowed by the task state machine."""
    return target in ALLOWED_TASK_TRANSITIONS[current]
