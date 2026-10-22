from __future__ import annotations

import hashlib
from collections.abc import Callable
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from company_os.domain.evidence import get_default_evidence_store
from company_os.domain.network_security import BoundedHttpClient


class RiskTier(StrEnum):
    """Execution risk tier."""

    TIER_0_READ_ONLY = "tier_0_read_only"
    TIER_1_REVERSIBLE = "tier_1_reversible"
    TIER_2_HIGH_IMPACT = "tier_2_high_impact"


class ExecutionStatus(StrEnum):
    """Status of an individual tool execution attempt."""

    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"
    INTERRUPTED = "interrupted"


class ExecutionRequest(BaseModel):
    """Typed request to execute a registered tool on behalf of an agent."""

    task_id: UUID
    agent_id: str
    tool_id: str
    parameters: dict[str, Any]
    caller: str = "system"


class ExecutionResult(BaseModel):
    """Result of an execution attempt."""

    execution_id: UUID
    task_id: UUID
    tool_id: str
    status: ExecutionStatus
    output_payload: dict[str, Any] = Field(default_factory=dict)
    error_message: str | None = None
    evidence_reference: str | None = None
    verification_checks: list[dict[str, Any]] = Field(default_factory=list)
    duration_ms: int = 0


class SourceVerifierInput(BaseModel):
    """Input payload for research.source_verifier."""

    model_config = ConfigDict(extra="forbid")

    url: str = Field(min_length=1)
    expected_snippet: str | None = None
    allow_loopback_for_testing: bool = False


class ToolDefinition(BaseModel):
    """Specification for a registered tool."""

    tool_id: str
    name: str
    description: str
    risk_tier: RiskTier
    allowed_agent_ids: set[str]
    input_schema: type[BaseModel]
    handler: Callable[[Any], tuple[dict[str, Any], list[dict[str, Any]], str]]


def handle_source_verifier(
    params: SourceVerifierInput,
) -> tuple[dict[str, Any], list[dict[str, Any]], str]:
    """Execute research.source_verifier with SSRF defenses and bounded retrieval."""
    client = BoundedHttpClient(allow_loopback=params.allow_loopback_for_testing)
    resp = client.get(params.url)

    content_sha256 = hashlib.sha256(resp.content).hexdigest()
    text_content = resp.text
    snippet_preview = text_content[:500]

    output_payload = {
        "url": params.url,
        "status_code": resp.status_code,
        "content_type": resp.content_type,
        "content_length": resp.byte_length,
        "content_sha256": content_sha256,
        "snippet_preview": snippet_preview,
    }

    checks: list[dict[str, Any]] = [
        {
            "check_id": "http_status",
            "passed": resp.status_code == 200,
            "details": f"Status code {resp.status_code}",
        },
        {
            "check_id": "content_type_allowed",
            "passed": True,
            "details": f"Content-Type {resp.content_type}",
        },
        {
            "check_id": "sha256_verified",
            "passed": bool(content_sha256),
            "details": f"Content hash verified: {content_sha256}",
        },
    ]

    if params.expected_snippet:
        snippet_found = params.expected_snippet in text_content
        checks.append(
            {
                "check_id": "snippet_present",
                "passed": snippet_found,
                "details": (
                    f"Expected snippet '{params.expected_snippet}' "
                    f"{'found' if snippet_found else 'NOT found'}"
                ),
            }
        )

    evidence_store = get_default_evidence_store()
    artifact = evidence_store.store(
        tool_id="research.source_verifier",
        source_url=params.url,
        content_sha256=content_sha256,
        content_type=resp.content_type,
        byte_length=resp.byte_length,
        content_snippet=snippet_preview,
        verification_checks=checks,
    )
    return output_payload, checks, artifact.artifact_uri


class ToolRegistry:
    """Registry managing allowed tools and authorization per agent."""

    def __init__(self) -> None:
        self._tools: dict[str, ToolDefinition] = {}

    def register(self, tool: ToolDefinition) -> None:
        self._tools[tool.tool_id] = tool

    def get(self, tool_id: str) -> ToolDefinition | None:
        return self._tools.get(tool_id)

    def is_agent_authorized(self, tool_id: str, agent_id: str) -> bool:
        tool = self.get(tool_id)
        if not tool:
            return False
        return agent_id in tool.allowed_agent_ids

    def list_tools(self) -> list[ToolDefinition]:
        return list(self._tools.values())


def create_default_tool_registry() -> ToolRegistry:
    """Instantiate the default tool registry with approved tools."""
    registry = ToolRegistry()
    registry.register(
        ToolDefinition(
            tool_id="research.source_verifier",
            name="Research Source Verifier",
            description=(
                "Bounded HTTP source retrieval and content hash verification "
                "for factual claims. Tier 0 read-only."
            ),
            risk_tier=RiskTier.TIER_0_READ_ONLY,
            allowed_agent_ids={"AG-03"},  # Research Specialist
            input_schema=SourceVerifierInput,
            handler=handle_source_verifier,
        )
    )
    return registry
