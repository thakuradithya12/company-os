# WP-03A — Canonical Task Lifecycle and Audit Trail

**Phase:** 3 — Core platform before specialist agents
**Status:** Implementation candidate; acceptance required before WP-03B.
**Scope boundary:** This work package does not implement authentication, an HTTP task API, a worker queue, agent prompting, or external integrations.

## Objective

Establish a typed canonical task state machine and durable PostgreSQL persistence for task records and task audit events. This becomes the contract that subsequent authentication, task API, and worker work packages must use.

## Deliverables

- One canonical list of task and actor states.
- `tasks` and `task_audit_events` tables introduced by an additive Alembic migration.
- Application services to create a queued task and perform a version-checked state transition.
- Atomic task-state/audit persistence within the caller's database transaction.
- Required reason and actor identity on transitions.
- Optimistic concurrency checks to reject stale commands.
- A completion gate requiring passing checks and a durable evidence reference.
- Deterministic unit/integration tests for allowed transitions, invalid transitions, terminal states, stale versions, missing tasks, and completion evidence.

## State rules

- All states and legal transitions live in `company_os.domain.task_state`.
- Application code, not model output or UI state, validates transitions.
- `completed`, `failed`, and `cancelled` are terminal; reopening requires creating a new task or a separately approved future operation.
- `unknown_outcome` is reconciliation-only and cannot directly transition back to execution.
- Completion requires a structured verification payload where `passed` is `true`, `checks` is a non-empty list, and `evidence_ref` is a non-empty string.
- A task change increments its version and creates an audit record in the same transaction. Callers own commit/rollback.
- This audit table is append-only by application contract in this work package; database roles/triggers and broader audit domains are separate hardening work.

## Requirements mapping

- FR-002, FR-006, FR-007, FR-010, FR-015, FR-041.
- AT-001, AT-003, AT-008, AT-011 (the last is only partially addressed here; external-side-effect reconciliation is deferred).

## Validation commands

Run on the supported developer environment after applying this work package:

```powershell
uv run --locked --python 3.13.16 ruff check apps/api/src apps/api/tests
uv run --locked --python 3.13.16 pytest
$env:COMPANY_OS_ENVIRONMENT = 'development'
$env:COMPANY_OS_DATABASE_URL = 'postgresql+psycopg://company_os:company_os_dev_only@localhost:55432/company_os'
uv run --locked --python 3.13.16 alembic upgrade head
uv run --locked --python 3.13.16 alembic current
```

## Acceptance criteria

- [ ] Migration `0002_task_lifecycle_core` upgrades on PostgreSQL 17 and can be downgraded in a disposable test database.
- [ ] All task states and legal transition edges have deterministic test coverage.
- [ ] Invalid transitions leave task and audit state unchanged.
- [ ] Stale versions are rejected without changing task state.
- [ ] A valid transition increments the version exactly once and records the transition event.
- [ ] Task creation writes both task and creation event in the same caller-owned transaction.
- [ ] Completion without passing checks and evidence reference is rejected.
- [ ] Terminal states cannot be reopened by ordinary transition calls.
- [ ] Unknown external outcomes cannot jump directly back to execution.
- [ ] No task API, worker, model invocation, or business-agent implementation is added in this package.
- [ ] All required tests pass; CI passes; commit is pushed; founder accepts the work package before WP-03B starts.

## Known limitations

- The table is ready for application integration but is not exposed over HTTP in this package.
- Role/permission enforcement at the API boundary is not implemented yet; no external route should call these services until the authorization work package is accepted.
- Worker leases, attempt scheduling, retries, cancellation cleanup, transactional outbox/queue dispatch, and live updates remain later core-platform packages.
- Evidence references are validated structurally; trustworthiness and authorization of the evidence producer must be enforced by the future verification service and API boundary.
