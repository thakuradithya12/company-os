"""Pydantic schemas for the task API endpoints."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, field_validator

from company_os.domain.task_state import ActorType


class TaskCreateRequest(BaseModel):
    """Payload to submit a new task into the canonical task system.

    SECURITY NOTE:
    The `created_by` field is caller-supplied and records provenance / attribution.
    It does NOT represent authenticated or authorized identity. Caller-supplied identity
    must not be trusted for access control until authentication is integrated.
    """

    model_config = ConfigDict(extra="forbid")

    objective: str = Field(
        ...,
        min_length=1,
        description="The objective statement for the task.",
    )
    created_by: str = Field(
        ...,
        min_length=1,
        description=(
            "Provenance identifier of who submitted this task. "
            "Note: Not verified authentication."
        ),
    )
    input_payload: dict[str, Any] = Field(
        default_factory=dict,
        description="Arbitrary input payload for the task.",
    )
    acceptance_criteria: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Verification criteria required for task completion.",
    )
    priority: int = Field(
        default=100,
        description="Execution priority for scheduling.",
    )
    max_attempts: int = Field(
        default=3,
        ge=1,
        description="Maximum attempts allowed before marking failed.",
    )
    deadline_at: datetime | None = Field(
        default=None,
        description="Optional deadline timestamp.",
    )
    actor_type: ActorType = Field(
        default=ActorType.FOUNDER,
        description="Actor category submitting the task.",
    )
    request_id: str | None = Field(
        default=None,
        description="Optional correlation or idempotency tracking ID.",
    )

    @field_validator("objective", "created_by")
    @classmethod
    def validate_not_blank(cls, value: str, info: ValidationInfo) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError(f"{info.field_name} must not be empty or blank")
        return trimmed


class TaskResponse(BaseModel):
    """Durable task representation returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    objective: str
    status: str
    created_by: str
    priority: int
    input_payload: dict[str, Any]
    acceptance_criteria: list[dict[str, Any]]
    attempt_count: int
    max_attempts: int
    version: int
    deadline_at: datetime | None
    cancel_requested_at: datetime | None
    started_at: datetime | None
    completed_at: datetime | None
    assigned_agent_id: str | None = None
    routing_decision: dict[str, Any] | None = None
    last_error_code: str | None
    last_error_message: str | None
    created_at: datetime
    updated_at: datetime


class TaskRouteResponse(BaseModel):
    """Outcome of an agent routing operation."""

    task: TaskResponse
    routing_decision: dict[str, Any]


class TaskExecuteRequest(BaseModel):
    """Payload to trigger execution of an approved tool on a task."""

    model_config = ConfigDict(extra="forbid")

    tool_id: str = Field(..., min_length=1, description="Registered tool identifier.")
    parameters: dict[str, Any] = Field(
        default_factory=dict, description="Input parameters for the tool."
    )
    agent_id: str | None = Field(
        default=None, description="Optional override/explicit agent ID."
    )
    caller: str = Field(
        default="system",
        description="Provenance tracking of who triggered execution.",
    )
    request_id: str | None = Field(
        default=None, description="Optional request correlation ID."
    )


class TaskExecutionResponse(BaseModel):
    """Durable record of a tool execution attempt."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    task_id: UUID
    agent_id: str
    tool_id: str
    risk_tier: str
    status: str
    input_parameters: dict[str, Any]
    output_payload: dict[str, Any]
    error_message: str | None = None
    evidence_reference: str | None = None
    verification_checks: list[dict[str, Any]] = Field(default_factory=list)
    duration_ms: int = 0
    created_at: datetime
    updated_at: datetime


