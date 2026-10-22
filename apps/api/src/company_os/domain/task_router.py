"""Deterministic task routing engine for Company OS."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Any

from company_os.domain.agent_registry import (
    AgentRegistry,
    AgentSpec,
    create_default_agent_registry,
)


class RoutingStatus(StrEnum):
    ROUTED = "routed"
    AMBIGUOUS = "ambiguous"
    UNSUPPORTED = "unsupported"
    AGENT_UNAVAILABLE = "agent_unavailable"


@dataclass(frozen=True)
class RoutingDecision:
    """Immutable outcome of a task routing determination."""

    status: RoutingStatus
    selected_agent_id: str | None
    matched_category: str | None
    confidence: float
    reason: str
    candidate_agent_ids: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["status"] = self.status.value
        return data


class DeterministicTaskRouter:
    """Evaluates task objectives and payloads deterministically to select an agent specialist."""

    def __init__(self, registry: AgentRegistry | None = None) -> None:
        self._registry = registry or create_default_agent_registry()

    def resolve(
        self,
        objective: str,
        input_payload: dict[str, Any] | None = None,
    ) -> RoutingDecision:
        payload = input_payload or {}

        # 1. Check for explicit agent ID request
        target_agent_id = (
            payload.get("target_agent_id")
            or payload.get("requested_agent_id")
            or payload.get("agent_id")
        )
        if target_agent_id:
            spec = self._registry.get(str(target_agent_id))
            if spec is None:
                return RoutingDecision(
                    status=RoutingStatus.UNSUPPORTED,
                    selected_agent_id=None,
                    matched_category=None,
                    confidence=0.0,
                    reason=f"Requested agent ID {target_agent_id!r} is not registered in workforce",
                    candidate_agent_ids=[],
                )
            if not spec.is_available:
                return RoutingDecision(
                    status=RoutingStatus.AGENT_UNAVAILABLE,
                    selected_agent_id=None,
                    matched_category=sorted(spec.categories)[0] if spec.categories else None,
                    confidence=1.0,
                    reason=(
                        f"Agent {spec.id} ({spec.name}) is registered but currently "
                        f"{spec.availability.value}"
                    ),
                    candidate_agent_ids=[spec.id],
                )
            return RoutingDecision(
                status=RoutingStatus.ROUTED,
                selected_agent_id=spec.id,
                matched_category=sorted(spec.categories)[0] if spec.categories else None,
                confidence=1.0,
                reason=f"Explicitly assigned to registered specialist {spec.id} ({spec.name})",
                candidate_agent_ids=[spec.id],
            )

        # 2. Check for explicit category request
        category = payload.get("category") or payload.get("task_category")
        if category:
            category_str = str(category).strip().lower()
            matching_agents = self._registry.find_by_category(category_str)
            if not matching_agents:
                return RoutingDecision(
                    status=RoutingStatus.UNSUPPORTED,
                    selected_agent_id=None,
                    matched_category=category_str,
                    confidence=0.0,
                    reason=f"No registered agent supports task category {category_str!r}",
                    candidate_agent_ids=[],
                )
            if len(matching_agents) > 1:
                candidates = [a.id for a in matching_agents]
                return RoutingDecision(
                    status=RoutingStatus.AMBIGUOUS,
                    selected_agent_id=None,
                    matched_category=category_str,
                    confidence=0.5,
                    reason=f"Multiple specialists match category {category_str!r}: {candidates}",
                    candidate_agent_ids=candidates,
                )

            spec = matching_agents[0]
            if not spec.is_available:
                return RoutingDecision(
                    status=RoutingStatus.AGENT_UNAVAILABLE,
                    selected_agent_id=None,
                    matched_category=category_str,
                    confidence=1.0,
                    reason=(
                        f"Specialist {spec.id} for category {category_str!r} is currently "
                        f"{spec.availability.value}"
                    ),
                    candidate_agent_ids=[spec.id],
                )
            return RoutingDecision(
                status=RoutingStatus.ROUTED,
                selected_agent_id=spec.id,
                matched_category=category_str,
                confidence=1.0,
                reason=(
                    f"Matched to specialist {spec.id} ({spec.name}) by explicit "
                    f"category {category_str!r}"
                ),
                candidate_agent_ids=[spec.id],
            )

        # 3. Deterministic keyword and semantic rule matching on objective
        return self._score_objective(objective)

    def _score_objective(self, objective: str) -> RoutingDecision:
        normalized_text = objective.strip().lower()
        if not normalized_text:
            return RoutingDecision(
                status=RoutingStatus.UNSUPPORTED,
                selected_agent_id=None,
                matched_category=None,
                confidence=0.0,
                reason="Task objective is empty",
                candidate_agent_ids=[],
            )

        agents = self._registry.list_agents()
        scores: dict[AgentSpec, int] = {}

        for agent in agents:
            score = 0
            for kw in sorted(agent.keywords, key=len, reverse=True):
                pattern = r"\b" + re.escape(kw) + r"\b"
                matches = len(re.findall(pattern, normalized_text))
                if matches > 0:
                    # Multi-word phrase gets higher weight
                    weight = 2 if " " in kw else 1
                    score += matches * weight
            if score > 0:
                scores[agent] = score

        if not scores:
            return RoutingDecision(
                status=RoutingStatus.UNSUPPORTED,
                selected_agent_id=None,
                matched_category=None,
                confidence=0.0,
                reason="Task objective does not match any registered specialist keywords",
                candidate_agent_ids=[],
            )

        max_score = max(scores.values())
        top_agents = [agent for agent, score in scores.items() if score == max_score]

        if len(top_agents) > 1:
            candidate_ids = [a.id for a in sorted(top_agents, key=lambda a: a.id)]
            return RoutingDecision(
                status=RoutingStatus.AMBIGUOUS,
                selected_agent_id=None,
                matched_category=None,
                confidence=float(max_score),
                reason=f"Objective matched multiple specialists with equal score: {candidate_ids}",
                candidate_agent_ids=candidate_ids,
            )

        chosen = top_agents[0]
        if not chosen.is_available:
            return RoutingDecision(
                status=RoutingStatus.AGENT_UNAVAILABLE,
                selected_agent_id=None,
                matched_category=sorted(chosen.categories)[0] if chosen.categories else None,
                confidence=float(max_score),
                reason=(
                    f"Specialist {chosen.id} matched objective but is currently "
                    f"{chosen.availability.value}"
                ),
                candidate_agent_ids=[chosen.id],
            )

        matched_cat = sorted(chosen.categories)[0] if chosen.categories else None
        confidence = min(1.0, max_score / 3.0)

        return RoutingDecision(
            status=RoutingStatus.ROUTED,
            selected_agent_id=chosen.id,
            matched_category=matched_cat,
            confidence=confidence,
            reason=(
                f"Deterministically matched to {chosen.id} ({chosen.name}) "
                "by objective keywords"
            ),
            candidate_agent_ids=[chosen.id],
        )
