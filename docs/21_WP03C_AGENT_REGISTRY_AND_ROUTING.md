# WP-03C — Agent Registry & Task Routing

**Phase:** 3 — Core platform before specialist agents  
**Status:** Complete; verified with unit/integration tests and database migrations.  
**Scope boundary:** This work package provides a typed agent registry, deterministic task-to-agent routing, persistence of routing decisions, and audit logging. It does not implement autonomous model execution, shell access, arbitrary tool invocation, or external business actions.

## Objective

Establish a deterministic, testable agent registry and task-routing capability for Company OS. Tasks submitted to the platform are evaluated against the founder-approved workforce registry, assigned to an appropriate specialist if supported and available, persisted with their assignment and routing rationale, and tracked in the task audit history.

## Deliverables

1. **Typed Agent Specification & Workforce Registry:**
   - Implemented in `company_os.domain.agent_registry`.
   - Defines `AgentSpec` with stable agent IDs (`AG-01` to `AG-08`), role names, descriptions, categories, capabilities, keywords, and explicit availability state (`AgentAvailability`: `available`, `unavailable`, `disabled`, `maintenance`).
   - Default registry initialized with the 8 founder-approved roles from `docs/17_AGENT_CLASSIFICATION.md`.

2. **Deterministic Task Router:**
   - Implemented in `company_os.domain.task_router.DeterministicTaskRouter`.
   - Evaluates task objectives and structured inputs deterministically without non-deterministic LLM calls.
   - Evaluates requests in strict priority:
     1. Explicit target agent ID (`target_agent_id`, `requested_agent_id`, `agent_id` in `input_payload`).
     2. Explicit task category (`category` or `task_category` in `input_payload`).
     3. Deterministic keyword and phrase matching across task `objective`.

3. **Explicit Handling of Failure Cases (Default-Safe):**
   - **Unsupported tasks:** When a task matches no registered capabilities, it is NOT silently routed to an arbitrary agent. The router produces `RoutingStatus.UNSUPPORTED`, the task transitions to `blocked` with error code `ROUTING_UNSUPPORTED`, and `assigned_agent_id` remains `null`.
   - **Ambiguous tasks:** When a task produces equal match scores across multiple specialists with no tie-breaker, the router produces `RoutingStatus.AMBIGUOUS` with candidate IDs, the task transitions to `blocked` with error code `ROUTING_AMBIGUOUS`, and `assigned_agent_id` remains `null`.
   - **Unavailable agents:** When the matching specialist is in an unavailable state (`unavailable`, `disabled`, `maintenance`), the router produces `RoutingStatus.AGENT_UNAVAILABLE`, the task transitions to `blocked` with error code `AGENT_UNAVAILABLE`, and no fallback agent is silently assigned.

4. **Persistence & Database Migration:**
   - Migration `0003_task_agent_routing.py` adds `assigned_agent_id` (`String(32)`, indexed) and `routing_decision` (`JSON`) to the `tasks` table.
   - Fully reversible with a clean `downgrade()` implementation.

5. **Audit Trail Recording:**
   - Records `task.routed` when successfully assigned to a specialist (transitioning `queued` -> `ready`).
   - Records `task.routing_failed` when routing fails due to unsupported, ambiguous, or unavailable status (transitioning `queued` -> `blocked`).
   - Stores full `RoutingDecision` payload in `event_data` including `status`, `selected_agent_id`, `matched_category`, `confidence`, `reason`, and `candidate_agent_ids`.

6. **Routing API Endpoint:**
   - `POST /tasks/{task_id}/route` (and `/api/v1/tasks/{task_id}/route`).
   - Returns HTTP 200 with `TaskRouteResponse` (`task` and `routing_decision`).
   - Returns HTTP 404 for missing tasks.
   - Returns HTTP 409 Conflict for terminal tasks (`completed`, `failed`, `cancelled`).

---

## Approved Agent Roles in Default Registry

| Agent ID | Name | Primary Categories | Key Capabilities |
|---|---|---|---|
| `AG-01` | Founder Command & Intake Agent | `intake_command` | Clarify intent, structure objectives, query status |
| `AG-02` | Planning & Orchestration Agent | `planning_orchestration` | Decompose workflows, assign capabilities, estimate resources |
| `AG-03` | Research & Evidence Agent | `research_evidence` | Source collection, claim verification, niche intelligence |
| `AG-04` | Business Discovery & Website Audit Agent | `business_discovery`, `website_audit` | Prospect discovery, website audit, technical rubric evaluation |
| `AG-05` | Content & Information Product Agent | `content_production` | Draft reports, produce guides, editorial synthesis |
| `AG-06` | Client Acquisition & Deal Agent | `client_acquisition`, `deal_proposal` | Draft outreach, structure proposals, deal tracking |
| `AG-07` | Digital Solution Builder Agent | `software_builder` | Software build, web development, automation scripting |
| `AG-08` | Independent Quality & Acceptance Agent | `quality_assurance` | Acceptance verification, evidence review, quality gate |

---

## Routing API Contract: `POST /tasks/{task_id}/route`

**Path Parameters:**
- `task_id` (UUID, required): Canonical task UUID.

**Headers:**
- `X-Request-ID` *(optional)*: Correlation identifier for audit tracing.

**Response `200 OK` (Successful Route):**
```json
{
  "task": {
    "id": "e4f8d228-5c0a-4938-b76e-5da709328f80",
    "objective": "Perform deep market research on enterprise observability",
    "status": "ready",
    "created_by": "founder:alice",
    "priority": 100,
    "input_payload": {},
    "acceptance_criteria": [],
    "attempt_count": 0,
    "max_attempts": 3,
    "version": 2,
    "assigned_agent_id": "AG-03",
    "routing_decision": {
      "status": "routed",
      "selected_agent_id": "AG-03",
      "matched_category": "research_evidence",
      "confidence": 1.0,
      "reason": "Deterministically matched to AG-03 (Research & Evidence Agent) by objective keywords",
      "candidate_agent_ids": ["AG-03"]
    },
    "last_error_code": null,
    "last_error_message": null,
    "created_at": "2026-10-22T06:30:00Z",
    "updated_at": "2026-10-22T06:31:00Z"
  },
  "routing_decision": {
    "status": "routed",
    "selected_agent_id": "AG-03",
    "matched_category": "research_evidence",
    "confidence": 1.0,
    "reason": "Deterministically matched to AG-03 (Research & Evidence Agent) by objective keywords",
    "candidate_agent_ids": ["AG-03"]
  }
}
```

**Response `200 OK` (Unsupported Route):**
```json
{
  "task": {
    "id": "f8a12345-5c0a-4938-b76e-5da709328f80",
    "objective": "Calculate daily horoscope for Aries",
    "status": "blocked",
    "assigned_agent_id": null,
    "routing_decision": {
      "status": "unsupported",
      "selected_agent_id": null,
      "matched_category": null,
      "confidence": 0.0,
      "reason": "Task objective does not match any registered specialist keywords",
      "candidate_agent_ids": []
    },
    "last_error_code": "ROUTING_UNSUPPORTED",
    "last_error_message": "Task objective does not match any registered specialist keywords"
  },
  "routing_decision": {
    "status": "unsupported",
    "selected_agent_id": null,
    "matched_category": null,
    "confidence": 0.0,
    "reason": "Task objective does not match any registered specialist keywords",
    "candidate_agent_ids": []
  }
}
```

---

## Validation Commands

```powershell
uv run --locked --python 3.13.16 ruff check apps/api/src apps/api/tests
uv run --locked --python 3.13.16 pytest
powershell -ExecutionPolicy Bypass -File scripts/check.ps1
```
