# WP-03C Implementation Plan: Agent Registry & Task Routing

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Establish a deterministic, typed agent registry, task-routing engine, database persistence model/migration, and audit logging for Company OS tasks.

**Architecture:** A domain-level `AgentRegistry` holding typed `AgentSpec` records (the 8 approved roles), a deterministic `DeterministicTaskRouter` evaluating objectives and payloads, a database migration adding `assigned_agent_id` and `routing_decision` to `tasks`, and a transactional service `route_task()` that updates task state, persists the assignment, and logs audit events.

**Tech Stack:** Python 3.13, FastAPI, SQLAlchemy 2.0, Alembic, PostgreSQL / SQLite.

**Spec:** `docs/17_AGENT_CLASSIFICATION.md`, `docs/agent-specs/`, `docs/01_PRODUCT_REQUIREMENTS.md`.

## Global Constraints

- Never silently route unsupported, ambiguous, or unavailable tasks to an arbitrary agent.
- Do not mark a task `completed` upon routing.
- Do not implement autonomous model execution, shell access, or external side effects in this work package.
- Maintain existing `/health/live`, `/health/ready`, and task API compatibility.
- Preserve unrelated local change `apps/web/next-env.d.ts`.

## Review Focus

1. **Unsupported tasks:** Objective or category has zero matching registered capabilities -> must return `RoutingStatus.UNSUPPORTED`, set task to `blocked`, and not assign any agent.
2. **Ambiguous tasks:** Objective or category matches multiple agents with equal score -> must return `RoutingStatus.AMBIGUOUS`, list all candidates, set task to `blocked`, and not assign any agent.
3. **Unavailable agent:** Matched agent has availability `UNAVAILABLE` / `MAINTENANCE` / `DISABLED` -> must return `RoutingStatus.AGENT_UNAVAILABLE`, set task to `blocked`, and not assign any fallback agent.
4. **Deterministic tie-breaking:** Same input objective/payload must always evaluate to the exact same routing outcome.
5. **Atomic audit trail:** Routing updates must persist `task.assigned_agent_id`, version bump, and `task.routed` or `task.routing_failed` audit event within one transaction.

---

### Task 1: Domain Agent Registry & Task Router

**Files:**
- Create: `apps/api/src/company_os/domain/agent_registry.py`
- Create: `apps/api/src/company_os/domain/task_router.py`
- Modify: `apps/api/src/company_os/domain/__init__.py`
- Test: `apps/api/tests/test_agent_registry.py`

**Interfaces:**
- Produces: `AgentAvailability`, `AgentSpec`, `AgentRegistry`, `create_default_agent_registry()`
- Produces: `RoutingStatus`, `RoutingDecision`, `DeterministicTaskRouter`

- [ ] **Step 1: Write failing unit tests for AgentRegistry and DeterministicTaskRouter**
- [ ] **Step 2: Run test to verify it fails**
- [ ] **Step 3: Implement domain models in `agent_registry.py` and `task_router.py`**
- [ ] **Step 4: Run tests to verify they pass**

---

### Task 2: Database Migration for Task Routing Fields

**Files:**
- Create: `apps/api/alembic/versions/0003_task_agent_routing.py`
- Modify: `apps/api/src/company_os/db/models/task.py`
- Test: `apps/api/tests/test_task_routing_migration.py`

**Interfaces:**
- Produces: `TaskRecord.assigned_agent_id`, `TaskRecord.routing_decision`

- [ ] **Step 1: Write failing test verifying database columns and migration downgrade/upgrade**
- [ ] **Step 2: Run test to verify it fails**
- [ ] **Step 3: Add migration `0003_task_agent_routing.py` and update `TaskRecord`**
- [ ] **Step 4: Run test to verify it passes**

---

### Task 3: Task Routing Application Service & Audit Logging

**Files:**
- Create: `apps/api/src/company_os/services/task_routing.py`
- Modify: `apps/api/src/company_os/services/__init__.py`
- Test: `apps/api/tests/test_task_routing_service.py`

**Interfaces:**
- Produces: `route_task(session, task_id, router=None, request_id=None)`

- [ ] **Step 1: Write failing tests for `route_task` (success, unsupported, ambiguous, unavailable, missing task, audit records)**
- [ ] **Step 2: Run tests to verify they fail**
- [ ] **Step 3: Implement `route_task` in `apps/api/src/company_os/services/task_routing.py`**
- [ ] **Step 4: Run tests to verify they pass**

---

### Task 4: API Endpoint `POST /tasks/{task_id}/route` & Schema Updates

**Files:**
- Modify: `apps/api/src/company_os/api/schemas.py`
- Modify: `apps/api/src/company_os/api/tasks.py`
- Modify: `apps/api/tests/test_tasks_api.py`

**Interfaces:**
- Produces: `POST /tasks/{task_id}/route`, `POST /api/v1/tasks/{task_id}/route`
- Produces: Updated `TaskResponse` containing `assigned_agent_id` and `routing_decision`

- [ ] **Step 1: Write failing tests in `test_tasks_api.py` for `/tasks/{task_id}/route` and updated response schema**
- [ ] **Step 2: Run test to verify it fails**
- [ ] **Step 3: Update `schemas.py` and `tasks.py`**
- [ ] **Step 4: Run tests to verify they pass**

---

### Task 5: Documentation & Full Repository Verification

**Files:**
- Create: `docs/21_WP03C_AGENT_REGISTRY_AND_ROUTING.md`
- Modify: `docs/08_API_CONTRACTS.md`

- [ ] **Step 1: Write WP-03C documentation**
- [ ] **Step 2: Update API contracts**
- [ ] **Step 3: Run Ruff check, full pytest suite, and `scripts/check.ps1`**
- [ ] **Step 4: Commit and push clean diff**
