"""Controlled execution engine for Company OS with strict transaction boundaries."""

from __future__ import annotations

import time
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from company_os.db.models.task import (
    TaskAuditEventRecord,
    TaskExecutionRecord,
    TaskRecord,
)
from company_os.domain.task_state import (
    TERMINAL_TASK_STATES,
    ActorType,
    TaskStatus,
)
from company_os.domain.tools import (
    ExecutionResult,
    ExecutionStatus,
    ToolRegistry,
    create_default_tool_registry,
)
from company_os.services.task_lifecycle import (
    InvalidTaskTransition,
    TaskLifecycleError,
    transition_task,
)


class ExecutionEngineError(Exception):
    """Base exception for controlled execution engine errors."""


class TaskNotFound(ExecutionEngineError):
    """Raised when the target task does not exist."""


class TaskTerminalStateError(ExecutionEngineError):
    """Raised when attempting to execute on a task in a terminal state."""


class ConcurrentExecutionConflictError(ExecutionEngineError):
    """Raised when an execution conflict occurs (e.g. concurrent execution running)."""


class ToolNotFoundError(ExecutionEngineError):
    """Raised when the requested tool is not registered."""


class UnauthorizedToolError(ExecutionEngineError):
    """Raised when the assigned agent is not authorized for the requested tool."""


class ToolValidationError(ExecutionEngineError):
    """Raised when input parameters fail schema validation."""


def _sanitize_error_message(err: str | None) -> str:
    """Sanitize execution errors to prevent leaking raw internal details or payloads."""
    if not err:
        return "One or more verification checks failed"
    err_lower = err.lower()
    if "prohibited ip" in err_lower or "ssrf" in err_lower:
        return "Security error: Outbound request targeted a prohibited destination"
    if "timed out" in err_lower:
        return "Request timed out while contacting source"
    if "tls" in err_lower or "certificate" in err_lower:
        return "TLS verification failed while connecting to source"
    if "response size exceeded" in err_lower:
        return "Response size exceeded maximum allowed limit"
    if "unaccepted content type" in err_lower:
        return "Server returned an unaccepted content type"
    return "Connection error encountered during tool execution"


def execute_task_tool(
    session_factory: sessionmaker[Session] | Callable[[], Session],
    *,
    task_id: UUID,
    tool_id: str,
    parameters: dict[str, Any],
    agent_id: str | None = None,
    caller: str = "system",
    request_id: str | None = None,
    tool_registry: ToolRegistry | None = None,
) -> ExecutionResult:
    """Execute a registered tool on behalf of a task's agent with two-phase transactions.

    Phase 1 (Tx 1): Claim task, validate authorization & inputs, transition state canonical
                    ready -> running, persist initial TaskExecutionRecord.
    Phase 2 (No Tx): Perform bounded real tool execution without holding any DB locks.
    Phase 3 (Tx 2): Persist execution outcome, enforce canonical transition
                    running -> verifying -> completed (or allowed failure state).
    """
    registry = tool_registry or create_default_tool_registry()
    tool = registry.get(tool_id)
    if tool is None:
        raise ToolNotFoundError(f"Tool {tool_id!r} is not registered")

    try:
        validated_params = tool.input_schema(**parameters)
    except ValidationError as exc:
        raise ToolValidationError(f"Invalid parameters for {tool_id}: {exc}") from exc

    execution_id = uuid4()
    effective_agent_id: str
    now = datetime.now(UTC)

    # -------------------------------------------------------------------------
    # PHASE 1: Claim and Start (Transaction 1)
    # -------------------------------------------------------------------------
    with session_factory() as session:
        with session.begin():
            statement = (
                select(TaskRecord)
                .where(TaskRecord.id == task_id)
                .with_for_update()
                .execution_options(populate_existing=True)
            )
            task = session.scalars(statement).one_or_none()
            if task is None:
                raise TaskNotFound(f"Task {task_id} not found")

            try:
                current_status = TaskStatus(task.status)
            except ValueError as exc:
                raise ExecutionEngineError(f"Invalid task status {task.status!r}") from exc

            if current_status in TERMINAL_TASK_STATES:
                raise TaskTerminalStateError(
                    f"Task {task_id} is in terminal status {task.status!r} and cannot execute tools"
                )

            # Rule 1: Reject execution from queued - must be routed to ready first
            if current_status == TaskStatus.QUEUED:
                raise InvalidTaskTransition(
                    f"Task {task_id} is in 'queued' state; it must be routed to a specialist "
                    "and reach 'ready' before execution can begin"
                )

            if current_status not in {
                TaskStatus.READY,
                TaskStatus.REWORK,
                TaskStatus.RUNNING,
            }:
                raise InvalidTaskTransition(
                    f"Cannot execute tool on task in status {task.status!r}"
                )

            effective_agent_id = task.assigned_agent_id or agent_id or ""
            if not effective_agent_id:
                raise UnauthorizedToolError("No agent assigned or provided for task execution")

            if not registry.is_agent_authorized(tool_id, effective_agent_id):
                raise UnauthorizedToolError(
                    f"Agent {effective_agent_id!r} is not authorized to execute tool {tool_id!r}"
                )

            # Atomic concurrency check: reject if an execution is already RUNNING for this task
            running_exec = session.scalar(
                select(TaskExecutionRecord).where(
                    TaskExecutionRecord.task_id == task_id,
                    TaskExecutionRecord.status == ExecutionStatus.RUNNING.value,
                )
            )
            if running_exec is not None:
                raise ConcurrentExecutionConflictError(
                    f"Task {task_id} already has an active running execution ({running_exec.id})"
                )

            # Apply canonical state transition to RUNNING
            if current_status in {TaskStatus.READY, TaskStatus.REWORK}:
                transition_task(
                    session,
                    task_id=task.id,
                    target_status=TaskStatus.RUNNING,
                    actor_type=ActorType.AGENT,
                    actor_id=effective_agent_id,
                    reason=f"Started execution of tool {tool_id}",
                    expected_version=task.version,
                    request_id=request_id,
                )
                task.attempt_count += 1
            elif current_status == TaskStatus.RUNNING:
                # Barrier version bump for sequential tool execution
                task.version += 1
                task.updated_at = now

            execution_record = TaskExecutionRecord(
                id=execution_id,
                task_id=task_id,
                agent_id=effective_agent_id,
                tool_id=tool_id,
                risk_tier=tool.risk_tier.value,
                status=ExecutionStatus.RUNNING.value,
                input_parameters=parameters,
                output_payload={},
                error_message=None,
                evidence_reference=None,
                verification_checks=[],
                duration_ms=0,
                created_at=now,
                updated_at=now,
            )
            session.add(execution_record)

            session.add(
                TaskAuditEventRecord(
                    task_id=task_id,
                    actor_type=ActorType.AGENT.value,
                    actor_id=effective_agent_id,
                    action="execution.started",
                    from_status=current_status.value,
                    to_status=TaskStatus.RUNNING.value,
                    from_version=task.version - 1,
                    to_version=task.version,
                    reason=f"Started execution of tool {tool_id}",
                    event_data={
                        "execution_id": str(execution_id),
                        "tool_id": tool_id,
                        "risk_tier": tool.risk_tier.value,
                    },
                    request_id=request_id,
                )
            )

    # -------------------------------------------------------------------------
    # PHASE 2: Execute Outside Database Transaction
    # -------------------------------------------------------------------------
    start_time = time.monotonic()
    output_payload: dict[str, Any] = {}
    verification_checks: list[dict[str, Any]] = []
    evidence_reference: str | None = None
    raw_error_message: str | None = None

    try:
        output_payload, verification_checks, evidence_reference = tool.handler(
            validated_params
        )
    except Exception as exc:
        raw_error_message = str(exc)

    duration_ms = int((time.monotonic() - start_time) * 1000)
    sanitized_error = _sanitize_error_message(raw_error_message) if raw_error_message else None

    # -------------------------------------------------------------------------
    # PHASE 3: Persist Outcome & Completion Verification Gate (Transaction 2)
    # -------------------------------------------------------------------------
    with session_factory() as session:
        with session.begin():
            statement = (
                select(TaskRecord)
                .where(TaskRecord.id == task_id)
                .with_for_update()
                .execution_options(populate_existing=True)
            )
            task = session.scalars(statement).one()

            exec_record = session.scalar(
                select(TaskExecutionRecord)
                .where(TaskExecutionRecord.id == execution_id)
                .with_for_update()
            )
            if exec_record is None:
                raise ExecutionEngineError(
                    f"Execution record {execution_id} missing during outcome persistence"
                )

            # Determine execution outcome
            if raw_error_message is not None:
                final_exec_status = ExecutionStatus.FAILED
            else:
                checks_passed = bool(verification_checks) and all(
                    c.get("passed") is True for c in verification_checks
                )
                if checks_passed and bool(evidence_reference):
                    final_exec_status = ExecutionStatus.COMPLETED
                else:
                    final_exec_status = ExecutionStatus.BLOCKED

            exec_record.status = final_exec_status.value
            exec_record.output_payload = output_payload
            exec_record.error_message = sanitized_error
            exec_record.evidence_reference = evidence_reference
            exec_record.verification_checks = verification_checks
            exec_record.duration_ms = duration_ms
            exec_record.updated_at = datetime.now(UTC)

            # Evaluate task state transition using canonical state machine
            if final_exec_status == ExecutionStatus.COMPLETED:
                # Step 1: Canonical RUNNING -> VERIFYING
                transition_task(
                    session,
                    task_id=task.id,
                    target_status=TaskStatus.VERIFYING,
                    actor_type=ActorType.AGENT,
                    actor_id=effective_agent_id,
                    reason=f"Verifying execution results for tool {tool_id}",
                    expected_version=task.version,
                    request_id=request_id,
                )

                # Step 2: Canonical VERIFYING -> COMPLETED
                transition_task(
                    session,
                    task_id=task.id,
                    target_status=TaskStatus.COMPLETED,
                    actor_type=ActorType.AGENT,
                    actor_id=effective_agent_id,
                    reason="All verification checks passed with valid evidence",
                    expected_version=task.version,
                    request_id=request_id,
                    verification_evidence={
                        "passed": True,
                        "checks": verification_checks,
                        "evidence_ref": evidence_reference,
                    },
                )
            else:
                if task.attempt_count >= task.max_attempts:
                    target_status = TaskStatus.FAILED
                    error_code = "MAX_ATTEMPTS_EXCEEDED"
                else:
                    target_status = TaskStatus.BLOCKED
                    error_code = (
                        "EXECUTION_ERROR"
                        if raw_error_message is not None
                        else "EXECUTION_VERIFICATION_FAILED"
                    )

                error_reason = sanitized_error or "One or more verification checks failed"
                transition_task(
                    session,
                    task_id=task.id,
                    target_status=target_status,
                    actor_type=ActorType.AGENT,
                    actor_id=effective_agent_id,
                    reason=error_reason,
                    expected_version=task.version,
                    request_id=request_id,
                    error_code=error_code,
                    error_message=error_reason,
                )

    return ExecutionResult(
        execution_id=execution_id,
        task_id=task_id,
        tool_id=tool_id,
        status=final_exec_status,
        output_payload=output_payload,
        error_message=sanitized_error,
        evidence_reference=evidence_reference,
        verification_checks=verification_checks,
        duration_ms=duration_ms,
    )


def mark_interrupted_executions(
    session: Session,
    *,
    task_id: UUID | None = None,
) -> int:
    """Find RUNNING executions, mark as INTERRUPTED, and recover task to BLOCKED."""
    statement = select(TaskExecutionRecord).where(
        TaskExecutionRecord.status == ExecutionStatus.RUNNING.value
    )
    if task_id is not None:
        statement = statement.where(TaskExecutionRecord.task_id == task_id)

    records = session.scalars(statement).all()
    now = datetime.now(UTC)
    for record in records:
        record.status = ExecutionStatus.INTERRUPTED.value
        record.error_message = "Execution attempt was interrupted or crashed"
        record.updated_at = now

        # Canonical task recovery: transition from RUNNING to BLOCKED
        task = session.scalar(
            select(TaskRecord).where(TaskRecord.id == record.task_id).with_for_update()
        )
        if task is not None and task.status == TaskStatus.RUNNING.value:
            try:
                transition_task(
                    session,
                    task_id=task.id,
                    target_status=TaskStatus.BLOCKED,
                    actor_type=ActorType.SYSTEM,
                    actor_id="system:recovery",
                    reason="Execution attempt was interrupted or crashed",
                    expected_version=task.version,
                    error_code="EXECUTION_INTERRUPTED",
                    error_message="Execution attempt was interrupted or crashed",
                )
            except TaskLifecycleError:
                # If transition cannot be applied, ensure status is marked blocked safely
                task.status = TaskStatus.BLOCKED.value
                task.last_error_code = "EXECUTION_INTERRUPTED"
                task.last_error_message = "Execution attempt was interrupted or crashed"
                task.updated_at = now

    session.flush()
    return len(records)
