# WP-03B — Task API and End-to-End Task Submission

**Phase:** 3 — Core platform before specialist agents  
**Status:** Complete; verified with unit/integration API tests.  
**Scope boundary:** This work package provides HTTP submission and retrieval for canonical tasks. It does not implement worker leases, background execution, agent orchestration, or full authentication middleware.

## Objective

Expose HTTP endpoints `POST /tasks` and `GET /tasks/{task_id}` (with `/api/v1` aliases) backed by the canonical task lifecycle service (`create_task()`). Persist task records and initial audit events atomically in one transaction, enforce strict input validation, sanitize database failure responses, and document security boundaries.

## Deliverables

1. **Task Submission (`POST /tasks` & `POST /api/v1/tasks`):**
   - Integrates `create_task()` from `company_os.services.task_lifecycle`.
   - Persists a new `TaskRecord` (status `queued`, version 1) and its `task.created` `TaskAuditEventRecord` atomically in a single database transaction.
   - Returns HTTP 201 Created with the full serialized `TaskResponse`.

2. **Task Retrieval (`GET /tasks/{task_id}` & `GET /api/v1/tasks/{task_id}`):**
   - Retrieves a task by its canonical UUID.
   - Returns HTTP 200 OK with the serialized `TaskResponse`.
   - Returns a clear HTTP 404 Not Found error when the task does not exist.
   - Returns HTTP 422 Unprocessable Entity when `task_id` is not a valid UUID.

3. **Validation and Error Sanitization:**
   - Enforces non-blank `objective` and `created_by`.
   - Rejects non-positive `max_attempts` (< 1) and invalid actor types.
   - Catches database unconfigured or unreachable errors and maps them to HTTP 503 Service Unavailable.
   - Sanitizes responses: no credentials, database connection strings, or raw exception tracebacks are ever exposed to callers.

4. **Automated Test Suite (`apps/api/tests/test_tasks_api.py`):**
   - 18 automated API tests covering creation, full payload options, atomic database persistence, audit event verification, retrieval, 404 missing task handling, 422 input validation errors, unconfigured database handling, unreachable database credential protection, route prefixes, and provenance attribution.

## API Contract

### 1. `POST /tasks` (and `/api/v1/tasks`)

Creates and queues a new task.

**Headers:**
- `Content-Type: application/json`
- `X-Request-ID` *(optional)*: Correlation identifier for request tracing.

**Request Payload:**
```json
{
  "objective": "Build automated revenue report",
  "created_by": "founder:alice",
  "input_payload": {"period": "2026-Q3"},
  "acceptance_criteria": [{"id": "revenue-reconciled", "required": true}],
  "priority": 100,
  "max_attempts": 3,
  "deadline_at": "2026-11-01T00:00:00Z",
  "actor_type": "founder",
  "request_id": "req-xyz-123"
}
```

- `objective` (string, required, min length 1): Objective statement for the task; cannot be empty or whitespace.
- `created_by` (string, required, min length 1): Origin identifier for audit attribution; cannot be empty or whitespace.
- `input_payload` (object, optional, default `{}`): Arbitrary structured task input data.
- `acceptance_criteria` (array of objects, optional, default `[]`): Verification criteria required for completion.
- `priority` (integer, optional, default `100`): Execution priority for scheduling.
- `max_attempts` (integer, optional, default `3`, minimum `1`): Maximum execution attempts before failure.
- `deadline_at` (ISO 8601 string, optional, default `null`): Optional completion deadline.
- `actor_type` (string enum, optional, default `"founder"`): One of `"founder"`, `"system"`, `"agent"`, `"service"`.
- `request_id` (string, optional, default `null`): Correlation ID. If omitted, `X-Request-ID` header is used.

**Response `201 Created`:**
```json
{
  "id": "e4f8d228-5c0a-4938-b76e-5da709328f80",
  "objective": "Build automated revenue report",
  "status": "queued",
  "created_by": "founder:alice",
  "priority": 100,
  "input_payload": {"period": "2026-Q3"},
  "acceptance_criteria": [{"id": "revenue-reconciled", "required": true}],
  "attempt_count": 0,
  "max_attempts": 3,
  "version": 1,
  "deadline_at": "2026-11-01T00:00:00Z",
  "cancel_requested_at": null,
  "started_at": null,
  "completed_at": null,
  "last_error_code": null,
  "last_error_message": null,
  "created_at": "2026-10-22T06:30:00Z",
  "updated_at": "2026-10-22T06:30:00Z"
}
```

**Errors:**
- `422 Unprocessable Entity`: Invalid request payload (missing fields, blank strings, `max_attempts < 1`, invalid enum).
- `503 Service Unavailable`: Database not configured or unavailable.

---

### 2. `GET /tasks/{task_id}` (and `/api/v1/tasks/{task_id}`)

Retrieves an existing task by its UUID.

**Path Parameters:**
- `task_id` (UUID, required): Canonical task UUID.

**Response `200 OK`:**
Returns the `TaskResponse` object matching the schema above.

**Errors:**
- `404 Not Found`: Task with the specified ID does not exist (`{"detail": "Task <uuid> not found"}`).
- `422 Unprocessable Entity`: `task_id` is not a valid UUID.
- `503 Service Unavailable`: Database not configured or unavailable.

---

## Security Limitation: Caller-Supplied `created_by` is NOT Authentication

> [!WARNING]
> **CRITICAL SECURITY BOUNDARY LIMITATION:**
> The `created_by` field in `POST /tasks` is currently a caller-supplied metadata field recording provenance and audit trail attribution. **It is NOT authenticated or verified identity.**
> 
> In Phase 3 (WP-03A and WP-03B), core data structures, state machines, and API endpoints are built before the authentication and authorization layer. As a result:
> 1. Any caller who reaches the endpoint can provide an arbitrary string as `created_by` (e.g., `"founder:alice"`, `"system:cron"`).
> 2. The API does not verify cryptographic signatures, session cookies, or JWT bearer tokens in this package.
> 3. Downstream services and operators **MUST NOT** rely on `created_by` for access control, authorization decisions, or elevated execution privileges until an authentication gateway/middleware is deployed.
> 4. When authentication is introduced in subsequent work packages, `created_by` will be populated or strictly validated from the verified session context.

## Validation Commands

Run on the developer environment:

```powershell
uv run --locked --python 3.13.16 ruff check apps/api/src apps/api/tests
uv run --locked --python 3.13.16 pytest
powershell -ExecutionPolicy Bypass -File scripts/check.ps1
```
