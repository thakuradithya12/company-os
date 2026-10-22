from __future__ import annotations

from company_os.domain.agent_registry import (
    AgentAvailability,
    AgentSpec,
    TaskCategory,
    create_default_agent_registry,
)
from company_os.domain.task_router import (
    DeterministicTaskRouter,
    RoutingStatus,
)


def test_agent_spec_definition() -> None:
    agent = AgentSpec(
        id="AG-TEST",
        name="Test Specialist",
        description="Handles testing tasks",
        categories=frozenset({"testing", "qa"}),
        capabilities=frozenset({"run_tests", "inspect_results"}),
        availability=AgentAvailability.AVAILABLE,
        keywords=frozenset({"test", "testing", "verify"}),
    )
    assert agent.id == "AG-TEST"
    assert agent.is_available is True
    assert "qa" in agent.categories


def test_default_agent_registry_contains_approved_workforce() -> None:
    registry = create_default_agent_registry()
    agents = registry.list_agents()
    agent_ids = {a.id for a in agents}

    expected_ids = {
        "AG-01",
        "AG-02",
        "AG-03",
        "AG-04",
        "AG-05",
        "AG-06",
        "AG-07",
        "AG-08",
    }
    assert expected_ids.issubset(agent_ids)

    # Check AG-03 Research
    research_agent = registry.get("AG-03")
    assert research_agent is not None
    assert research_agent.name == "Research & Evidence Agent"
    assert "research_evidence" in research_agent.categories

    # Check AG-07 Solution Builder
    builder_agent = registry.get("AG-07")
    assert builder_agent is not None
    assert builder_agent.name == "Digital Solution Builder Agent"
    assert "software_builder" in builder_agent.categories


def test_registry_availability_update() -> None:
    registry = create_default_agent_registry()
    ag3 = registry.get("AG-03")
    assert ag3 is not None and ag3.is_available is True

    registry.set_availability("AG-03", AgentAvailability.UNAVAILABLE)
    ag3_updated = registry.get("AG-03")
    assert ag3_updated is not None and ag3_updated.is_available is False
    assert ag3_updated.availability == AgentAvailability.UNAVAILABLE

    available_agents = registry.list_agents(availability=AgentAvailability.AVAILABLE)
    assert "AG-03" not in {a.id for a in available_agents}


def test_router_explicit_agent_id() -> None:
    registry = create_default_agent_registry()
    router = DeterministicTaskRouter(registry)

    # Directly requested available agent
    decision = router.resolve(
        objective="Analyze competitive landscape",
        input_payload={"target_agent_id": "AG-03"},
    )
    assert decision.status == RoutingStatus.ROUTED
    assert decision.selected_agent_id == "AG-03"

    # Directly requested unknown agent
    unknown_decision = router.resolve(
        objective="Analyze competitive landscape",
        input_payload={"target_agent_id": "AG-99"},
    )
    assert unknown_decision.status == RoutingStatus.UNSUPPORTED
    assert unknown_decision.selected_agent_id is None


def test_router_explicit_category() -> None:
    registry = create_default_agent_registry()
    router = DeterministicTaskRouter(registry)

    decision = router.resolve(
        objective="Inspect candidate website performance",
        input_payload={"category": TaskCategory.WEBSITE_AUDIT.value},
    )
    assert decision.status == RoutingStatus.ROUTED
    assert decision.selected_agent_id == "AG-04"
    assert decision.matched_category == TaskCategory.WEBSITE_AUDIT.value


def test_router_objective_keyword_matching() -> None:
    registry = create_default_agent_registry()
    router = DeterministicTaskRouter(registry)

    # Research keywords
    res = router.resolve(objective="Perform deep market research on developer tooling")
    assert res.status == RoutingStatus.ROUTED
    assert res.selected_agent_id == "AG-03"

    # Builder keywords
    res_builder = router.resolve(objective="Build Next.js web application for client dashboard")
    assert res_builder.status == RoutingStatus.ROUTED
    assert res_builder.selected_agent_id == "AG-07"

    # Website audit keywords
    res_audit = router.resolve(objective="Run comprehensive website audit on target domain")
    assert res_audit.status == RoutingStatus.ROUTED
    assert res_audit.selected_agent_id == "AG-04"


def test_router_unavailable_agent_not_silently_routed() -> None:
    registry = create_default_agent_registry()
    registry.set_availability("AG-03", AgentAvailability.UNAVAILABLE)
    router = DeterministicTaskRouter(registry)

    decision = router.resolve(objective="Investigate competitor claims and evidence")
    assert decision.status == RoutingStatus.AGENT_UNAVAILABLE
    assert decision.selected_agent_id is None
    assert "AG-03" in decision.reason


def test_router_unsupported_task_not_routed() -> None:
    registry = create_default_agent_registry()
    router = DeterministicTaskRouter(registry)

    # Unsupported category
    decision_cat = router.resolve(
        objective="Calculate daily horoscope",
        input_payload={"category": "astrology_reading"},
    )
    assert decision_cat.status == RoutingStatus.UNSUPPORTED
    assert decision_cat.selected_agent_id is None

    # Unmatched objective text
    decision_text = router.resolve(objective="xyz abc 12345 foo bar")
    assert decision_text.status == RoutingStatus.UNSUPPORTED
    assert decision_text.selected_agent_id is None


def test_router_ambiguous_task_not_silently_routed() -> None:
    registry = create_default_agent_registry()
    router = DeterministicTaskRouter(registry)

    # Objective containing strong equal signals for both builder and research
    decision = router.resolve(objective="build research")
    assert decision.status == RoutingStatus.AMBIGUOUS
    assert decision.selected_agent_id is None
    assert len(decision.candidate_agent_ids) >= 2


def test_router_determinism() -> None:
    registry = create_default_agent_registry()
    router = DeterministicTaskRouter(registry)

    objective = "Audit security and performance of website"
    decisions = [router.resolve(objective=objective) for _ in range(10)]
    first = decisions[0]
    for d in decisions[1:]:
        assert d.status == first.status
        assert d.selected_agent_id == first.selected_agent_id
        assert d.matched_category == first.matched_category
        assert d.confidence == first.confidence
