# 08 — API Contracts

## 1. General rules

- Prefix application APIs with `/api/v1` until a versioning change is needed.
- Use JSON with schema validation and generated OpenAPI documentation.
- Use stable identifiers rather than exposing sequential database IDs where avoidable.
- Return consistent errors with an error code, human-readable message, request/trace ID, and safe remediation guidance.
- Enforce authorization, rate limits, validation, idempotency, and resource scopes server-side.
- Do not include secrets, internal stack traces, raw provider credentials, or unfiltered sensitive prompts in responses.
- Use pagination for collection APIs and explicit sort order.
- Apply optimistic concurrency/version checks for policy, proposal, approval, and other sensitive edits.

## 2. API domains

Initial API domains, not a promise to implement them all in the first coding phase:

- `/auth`: login/session/logout, session info, MFA status where implemented.
- `/objectives`: create and inspect founder objectives.
- `/plans`: view plan versions, acceptance criteria, dependencies, and clarification requests.
- `/tasks`: canonical task creation, retrieval, and specialist routing (`POST /tasks`, `GET /tasks/{task_id}`, `POST /tasks/{task_id}/route`, and `/api/v1/tasks`). NOTE: in the current phase prior to authentication, `created_by` is caller-supplied metadata and must not be treated as authenticated identity. See `docs/20_WP03B_TASK_API_AND_SUBMISSION.md` and `docs/21_WP03C_AGENT_REGISTRY_AND_ROUTING.md`.
- `/workforce`: list approved capability definitions, inspect status, edit through authorized governance flow.
- `/approvals`: list, inspect, approve, reject, or request changes to a specific proposal version.
- `/memory`: search and manage memory within the operator's access scope.
- `/research`: create research job, inspect sources, reports, and publication status.
- `/businesses` and `/leads`: inspect opportunities, qualification, website audit evidence, and contact eligibility.
- `/communications`: drafts, approved sends/calls, provider status, outcomes, and opt-out/suppression controls.
- `/deals`: requirements, proposals, pricing rules, negotiation history, terms and approval status.
- `/projects`: project requirements, milestones, deliverables, previews and release status.
- `/integrations`: connection state and safe configuration metadata, never raw secrets.
- `/audit`: filtered audit history under strong access controls.
- `/health`: health/readiness endpoints; only non-sensitive fields are exposed publicly.

## 3. Command versus query

Queries read persisted state. Commands request a state change. The API validates and persists the command; a worker performs long-running execution asynchronously. Task-creating endpoints return an accepted response with an objective/task ID and status URL rather than holding the HTTP request open while a model works.

Example conceptual response:

```json
{
  "request_id": "req-id",
  "objective_id": "objective-id",
  "status": "queued",
  "status_url": "/api/v1/objectives/objective-id"
}
```

The exact envelope and status codes must be implemented consistently. This example is illustrative, not final generated OpenAPI.

## 4. Idempotency and concurrency

- State-changing endpoints that may be retried should accept an idempotency key or use a client command ID.
- Replaying the same key with the same payload returns the existing command outcome; reusing a key with a different payload is rejected.
- Use database transactions for state changes and related audit records.
- Use a transactional outbox or equivalent mechanism so persisted work is not silently lost between database commit and queue dispatch.
- Use entity versions/ETags for sensitive edits and reject stale approval payloads.

## 5. Live events

Live updates should include event ID, entity ID, event type, state version, timestamp, and trace ID. The client deduplicates event IDs and ignores older state versions. Sensitive payloads are omitted. On reconnect, the client fetches canonical state and resumes from a cursor when available.

## 6. Authentication and errors

Unauthenticated private requests return an appropriate 401; authenticated but unauthorized requests return 403 or a policy-safe denial. Prior to the full authentication work package, endpoints that accept caller-supplied identifiers (such as `created_by` on `/tasks`) record them strictly for provenance/audit attribution, NOT verified authentication. Validation errors identify the input field without exposing secrets. Provider errors are mapped to stable categories such as `timeout`, `rate_limited`, `unavailable`, `invalid_output`, `permission_denied`, `budget_exceeded`, `policy_blocked`, and `unknown_external_outcome`.

## 7. API acceptance requirements

- OpenAPI schema validates and is generated from the actual code.
- Authentication/authorization tests exist for each protected domain.
- No endpoint can mark a task complete without the state machine's checks.
- Cancel/retry/pause commands handle races and repeated requests safely.
- User-controlled URLs, file paths, shell arguments, and integration identifiers are validated to prevent SSRF, path traversal, command injection, and IDOR.
- All side-effect APIs consult the policy/approval system before execution.
