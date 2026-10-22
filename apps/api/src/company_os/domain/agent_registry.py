"""Domain model for agent capabilities, availability, and workforce registry."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class AgentAvailability(StrEnum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    DISABLED = "disabled"
    MAINTENANCE = "maintenance"


class TaskCategory(StrEnum):
    INTAKE_COMMAND = "intake_command"
    PLANNING_ORCHESTRATION = "planning_orchestration"
    RESEARCH_EVIDENCE = "research_evidence"
    BUSINESS_DISCOVERY = "business_discovery"
    WEBSITE_AUDIT = "website_audit"
    CONTENT_PRODUCTION = "content_production"
    CLIENT_ACQUISITION = "client_acquisition"
    DEAL_PROPOSAL = "deal_proposal"
    SOFTWARE_BUILDER = "software_builder"
    QUALITY_ASSURANCE = "quality_assurance"


@dataclass(frozen=True)
class AgentSpec:
    """Immutable specification of a registered specialist role."""

    id: str
    name: str
    description: str
    categories: frozenset[str]
    capabilities: frozenset[str]
    availability: AgentAvailability = AgentAvailability.AVAILABLE
    keywords: frozenset[str] = field(default_factory=frozenset)
    version: str = "0.1.0"

    @property
    def is_available(self) -> bool:
        return self.availability == AgentAvailability.AVAILABLE


class AgentRegistry:
    """In-memory registry of approved specialist agents."""

    def __init__(self) -> None:
        self._agents: dict[str, AgentSpec] = {}

    def register(self, spec: AgentSpec) -> None:
        self._agents[spec.id] = spec

    def get(self, agent_id: str) -> AgentSpec | None:
        return self._agents.get(agent_id)

    def list_agents(
        self, availability: AgentAvailability | None = None
    ) -> list[AgentSpec]:
        agents = sorted(self._agents.values(), key=lambda a: a.id)
        if availability is not None:
            return [a for a in agents if a.availability == availability]
        return agents

    def set_availability(
        self, agent_id: str, availability: AgentAvailability
    ) -> None:
        spec = self._agents.get(agent_id)
        if spec is None:
            raise KeyError(f"Agent {agent_id!r} is not registered")
        updated = AgentSpec(
            id=spec.id,
            name=spec.name,
            description=spec.description,
            categories=spec.categories,
            capabilities=spec.capabilities,
            availability=availability,
            keywords=spec.keywords,
            version=spec.version,
        )
        self._agents[agent_id] = updated

    def find_by_category(self, category: str) -> list[AgentSpec]:
        return [
            a
            for a in sorted(self._agents.values(), key=lambda a: a.id)
            if category in a.categories
        ]


def create_default_agent_registry() -> AgentRegistry:
    """Construct the registry initialized with the 8 founder-approved agent roles."""
    registry = AgentRegistry()

    registry.register(
        AgentSpec(
            id="AG-01",
            name="Founder Command & Intake Agent",
            description="Clarifies founder intent and structures incoming business commands.",
            categories=frozenset({
                TaskCategory.INTAKE_COMMAND.value,
            }),
            capabilities=frozenset({
                "clarify_intent",
                "structure_objective",
                "query_system_status",
            }),
            keywords=frozenset({
                "intake",
                "clarify",
                "command",
                "founder",
                "status",
            }),
        )
    )

    registry.register(
        AgentSpec(
            id="AG-02",
            name="Planning & Orchestration Agent",
            description=(
                "Decomposes objectives into versioned task graphs and assigns capabilities."
            ),
            categories=frozenset({
                TaskCategory.PLANNING_ORCHESTRATION.value,
            }),
            capabilities=frozenset({
                "decompose_workflow",
                "assign_capabilities",
                "estimate_resources",
            }),
            keywords=frozenset({
                "plan",
                "planning",
                "orchestrate",
                "orchestration",
                "decompose",
                "breakdown",
                "task graph",
            }),
        )
    )

    registry.register(
        AgentSpec(
            id="AG-03",
            name="Research & Evidence Agent",
            description=(
                "Collects approved sources, compares claims, and produces evidence findings."
            ),
            categories=frozenset({
                TaskCategory.RESEARCH_EVIDENCE.value,
            }),
            capabilities=frozenset({
                "source_collection",
                "claim_verification",
                "niche_intelligence",
            }),
            keywords=frozenset({
                "research",
                "investigate",
                "evidence",
                "market research",
                "niche",
                "competitor",
                "sources",
                "claims",
            }),
        )
    )

    registry.register(
        AgentSpec(
            id="AG-04",
            name="Business Discovery & Website Audit Agent",
            description=(
                "Identifies target businesses and performs technical audits of digital presence."
            ),
            categories=frozenset({
                TaskCategory.BUSINESS_DISCOVERY.value,
                TaskCategory.WEBSITE_AUDIT.value,
            }),
            capabilities=frozenset({
                "prospect_discovery",
                "website_audit",
                "technical_rubric_evaluation",
            }),
            keywords=frozenset({
                "audit",
                "website audit",
                "prospect",
                "business discovery",
                "leads",
                "qualification",
                "domain inspection",
            }),
        )
    )

    registry.register(
        AgentSpec(
            id="AG-05",
            name="Content & Information Product Agent",
            description=(
                "Transforms verified research into audience guides, reports, and content drafts."
            ),
            categories=frozenset({
                TaskCategory.CONTENT_PRODUCTION.value,
            }),
            capabilities=frozenset({
                "draft_report",
                "produce_guide",
                "editorial_synthesis",
            }),
            keywords=frozenset({
                "content",
                "article",
                "blog post",
                "report draft",
                "whitepaper",
                "guide",
                "copywriting",
                "information product",
            }),
        )
    )

    registry.register(
        AgentSpec(
            id="AG-06",
            name="Client Acquisition & Deal Agent",
            description=(
                "Prepares outreach drafts, structures proposals, and tracks deal negotiation."
            ),
            categories=frozenset({
                TaskCategory.CLIENT_ACQUISITION.value,
                TaskCategory.DEAL_PROPOSAL.value,
            }),
            capabilities=frozenset({
                "draft_outreach",
                "structure_proposal",
                "deal_tracking",
            }),
            keywords=frozenset({
                "deal",
                "proposal",
                "pitch",
                "outreach",
                "negotiation",
                "client acquisition",
                "sales",
            }),
        )
    )

    registry.register(
        AgentSpec(
            id="AG-07",
            name="Digital Solution Builder Agent",
            description=(
                "Implements software deliverables, web components, and automated solutions."
            ),
            categories=frozenset({
                TaskCategory.SOFTWARE_BUILDER.value,
            }),
            capabilities=frozenset({
                "software_build",
                "web_development",
                "automation_scripting",
            }),
            keywords=frozenset({
                "build",
                "develop",
                "software",
                "web application",
                "website builder",
                "landing page",
                "code",
                "frontend",
                "backend",
                "api",
            }),
        )
    )

    registry.register(
        AgentSpec(
            id="AG-08",
            name="Independent Quality & Acceptance Agent",
            description="Reviews outputs against acceptance criteria, evidence, and quality tests.",
            categories=frozenset({
                TaskCategory.QUALITY_ASSURANCE.value,
            }),
            capabilities=frozenset({
                "acceptance_verification",
                "evidence_review",
                "quality_gate",
            }),
            keywords=frozenset({
                "verify",
                "verification",
                "acceptance test",
                "quality review",
                "qa",
                "rubric inspection",
            }),
        )
    )

    return registry
