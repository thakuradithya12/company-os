"""API endpoints for canonical task creation and inspection."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from company_os.api.dependencies import get_db_session, get_session_factory
from company_os.api.schemas import (
    TaskCreateRequest,
    TaskExecuteRequest,
    TaskExecutionResponse,
    TaskResponse,
    TaskRouteResponse,
)
from company_os.db.models.task import TaskExecutionRecord, TaskRecord
from company_os.services.execution_engine import (
    ConcurrentExecutionConflictError,
    TaskTerminalStateError,
    ToolNotFoundError,
    ToolValidationError,
    UnauthorizedToolError,
    execute_task_tool,
)
from company_os.services.execution_engine import (
    TaskNotFound as ExecutionTaskNotFound,
)
from company_os.services.task_lifecycle import (
    InvalidTaskTransition,
    TaskLifecycleError,
    TaskNotFound,
    create_task,
)
from company_os.services.task_routing import route_task

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post(
    "",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit a new objective-sized task",
    description=(
        "Accepts a new task into the canonical task system in the 'queued' state. "
        "Persists the task record and initial 'task.created' audit event atomically "
        "in one transaction.\n\n"
        "SECURITY LIMITATION: Caller-supplied 'created_by' records provenance/attribution "
        "and is NOT authenticated identity. Caller-supplied identity must not be trusted "
        "for access control until authentication is integrated in subsequent work packages."
    ),
)
def create_new_task(
    payload: TaskCreateRequest,
    request: Request,
    session: Annotated[Session, Depends(get_db_session)],
) -> TaskRecord:
    """Create a new queued task and initial audit event atomically."""
    request_id = payload.request_id or request.headers.get("x-request-id")
    try:
        with session.begin():
            return create_task(
                session,
                objective=payload.objective,
                created_by=payload.created_by,
                input_payload=payload.input_payload,
                acceptance_criteria=payload.acceptance_criteria,
                priority=payload.priority,
                max_attempts=payload.max_attempts,
                deadline_at=payload.deadline_at,
                actor_type=payload.actor_type,
                request_id=request_id,
            )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except TaskLifecycleError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Retrieve a task by ID",
    description="Fetches a canonical task by its unique UUID.",
)
def get_task_by_id(
    task_id: UUID,
    session: Annotated[Session, Depends(get_db_session)],
) -> TaskRecord:
    """Fetch a task by UUID or return 404."""
    task = session.scalar(select(TaskRecord).where(TaskRecord.id == task_id))
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found",
        )
    return task


@router.post(
    "/{task_id}/route",
    response_model=TaskRouteResponse,
    summary="Route a task to a registered specialist",
    description=(
        "Evaluates a task's objective and input payload against the approved "
        "workforce registry, assigns the specialist if supported and available, "
        "and records the decision in the task audit history."
    ),
)
def route_task_endpoint(
    task_id: UUID,
    request: Request,
    session: Annotated[Session, Depends(get_db_session)],
) -> TaskRouteResponse:
    """Deterministically route a task and persist the decision."""
    request_id = request.headers.get("x-request-id")
    try:
        with session.begin():
            task, decision = route_task(
                session,
                task_id=task_id,
                request_id=request_id,
            )
    except TaskNotFound as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except InvalidTaskTransition as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    return TaskRouteResponse(
        task=TaskResponse.model_validate(task),
        routing_decision=decision.to_dict(),
    )


@router.post(
    "/{task_id}/execute",
    response_model=TaskExecutionResponse,
    summary="Execute an approved tool on a task",
    description=(
        "Executes a registered tool within strict risk boundaries. "
        "Enforces two-phase transaction isolation (no database transaction held "
        "during network/tool execution), input schema validation, agent authorization, "
        "and a completion verification gate."
    ),
)
def execute_task_tool_endpoint(
    task_id: UUID,
    payload: TaskExecuteRequest,
    request: Request,
    session_factory: Annotated[sessionmaker[Session], Depends(get_session_factory)],
    session: Annotated[Session, Depends(get_db_session)],
) -> TaskExecutionRecord:
    """Execute a registered tool for an assigned task agent."""
    request_id = payload.request_id or request.headers.get("x-request-id")
    try:
        result = execute_task_tool(
            session_factory,
            task_id=task_id,
            tool_id=payload.tool_id,
            parameters=payload.parameters,
            agent_id=payload.agent_id,
            caller=payload.caller,
            request_id=request_id,
        )
    except ExecutionTaskNotFound as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except ToolNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except UnauthorizedToolError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc
    except ToolValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except (TaskTerminalStateError, ConcurrentExecutionConflictError) as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    exec_record = session.scalar(
        select(TaskExecutionRecord).where(TaskExecutionRecord.id == result.execution_id)
    )
    if exec_record is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Execution record was not persisted",
        )
    return exec_record


@router.get(
    "/{task_id}/executions",
    response_model=list[TaskExecutionResponse],
    summary="Retrieve execution history for a task",
    description=(
        "Returns all recorded execution attempts for the given task ordered by creation time."
    ),
)
def get_task_executions_endpoint(
    task_id: UUID,
    session: Annotated[Session, Depends(get_db_session)],
) -> list[TaskExecutionRecord]:
    """Retrieve execution records for a task."""
    task = session.scalar(select(TaskRecord).where(TaskRecord.id == task_id))
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found",
        )
    executions = session.scalars(
        select(TaskExecutionRecord)
        .where(TaskExecutionRecord.task_id == task_id)
        .order_by(TaskExecutionRecord.created_at)
    ).all()
    return list(executions)
