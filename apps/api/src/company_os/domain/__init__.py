"""Domain-level contracts for Company OS."""

from company_os.domain.agent_registry import (
    AgentAvailability,
    AgentRegistry,
    AgentSpec,
    TaskCategory,
    create_default_agent_registry,
)
from company_os.domain.task_router import (
    DeterministicTaskRouter,
    RoutingDecision,
    RoutingStatus,
)
from company_os.domain.task_state import (
    ActorType,
    TaskStatus,
    can_transition_task,
)

__all__ = [
    "ActorType",
    "AgentAvailability",
    "AgentRegistry",
    "AgentSpec",
    "DeterministicTaskRouter",
    "RoutingDecision",
    "RoutingStatus",
    "TaskCategory",
    "TaskStatus",
    "can_transition_task",
    "create_default_agent_registry",
]
