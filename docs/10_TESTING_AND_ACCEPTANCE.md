# 10 — Testing and Acceptance

## 1. Test philosophy

Every requirement that affects user-visible behavior, data integrity, security, external side effects, or completion status needs a measurable check. Test cases should exist before or alongside implementation, not be invented after a feature is called finished.

## 2. Test layers

- **Static checks:** formatter, linter, type checking, dependency/audit checks where practical, secret scanning, migration validation.
- **Unit tests:** state transitions, policy decisions, schema validation, idempotency, redaction, scoring/calculation utilities, memory scoping.
- **Integration tests:** database transactions, broker dispatch, worker lease/heartbeat, model adapter, tool gateway, provider webhook signatures, and storage access.
- **API tests:** auth, access controls, validation, pagination, concurrency, rate limits, error envelope, and task commands.
- **UI tests:** critical navigation, forms, permissions-aware controls, loading/error/empty states, accessibility basics, stale/reconnect behavior.
- **End-to-end tests:** objective creation through planning, delegation, execution, verification, approval, and final report.
- **Evaluation tests:** representative task cases, grounded claims, correct refusal/escalation, tool argument quality, structured output validity, and robustness to adversarial instructions.
- **Failure-injection tests:** worker crash, database interruption, broker interruption, model timeout, rate limiting, duplicate delivery, partial response, unknown external outcome, and forced task termination.
- **Security tests:** prompt injection, SSRF, path traversal, IDOR, authorization bypass, secret leakage, unsafe output rendering, excessive agency, and denial-of-service boundaries.
- **Operational tests:** clean install, migration from supported schema, backup restoration, rollback, alert delivery, and emergency stop.

## 3. Release gate format

Each phase/work package must provide:
1. Scope and changed files.
2. Requirements covered.
3. Test commands actually executed.
4. Results and summaries.
5. Relevant logs/artifacts or CI run URL.
6. Known limitations and any skipped tests with reason.
7. Security impact and rollback procedure.
8. Open defects classified by severity.

No test may be reported as passing if it was not executed. A skipped test is not a pass. Mock-based test evidence must be distinguished from real integration evidence.

## 4. Core acceptance scenarios

### AT-001 — Objective persistence
Submitting an objective creates a durable record with a stable ID before execution starts. Refreshing the browser preserves the objective and its state.

### AT-002 — Task orchestration
A known fixture objective produces a versioned plan and subtasks with explicit dependencies, valid schemas, and acceptance criteria.

### AT-003 — State integrity
Invalid state transitions are rejected by backend code. A model response cannot directly force a terminal `completed` state.

### AT-004 — Recovery after restart
Stop the API/worker during a test task. Restart the services. The system reconciles task/queue state and either resumes safely, reports blocked/failed, or requests reconciliation; it does not lose the record or duplicate external actions.

### AT-005 — Cancellation
Cancel a long-running sandboxed task. New subtasks stop dispatching, the worker terminates within configured boundaries, temporary resources are cleaned, and the UI reports actual status.

### AT-006 — Tool permission
An agent without permission tries to invoke an external side-effect tool. The call is rejected, recorded, and no side effect occurs.

### AT-007 — Approval version binding
Approve a particular proposal version, then change the proposal. The stale approval cannot authorize the modified proposal.

### AT-008 — Independent quality gate
Provide an output that claims success but fails an acceptance check. The task cannot be marked completed; it enters rework or failed state with evidence.

### AT-009 — Research provenance
A generated report contains sources and retrieval dates for factual claims, flags conflicting or stale evidence, and labels assumptions separately.

### AT-010 — Memory scope
A task for one customer cannot retrieve another customer's private memory or artifact, even if a semantic search would rank it highly.

### AT-011 — External side-effect idempotency
Simulate timeout after the provider may have accepted a call/message. The task becomes `unknown_outcome` and reconciliation prevents an automatic duplicate.

### AT-012 — Suppression and opt-out
A suppressed/opted-out contact is blocked at the server-side final action boundary regardless of agent instructions or UI state.

### AT-013 — Honest dashboard
Simulate stale events and a disconnected WebSocket. The UI indicates stale/disconnected state and reconciles from the database when reconnected.

### AT-014 — Secret protection
Insert test credentials into known secret fields and confirm they do not appear in normal logs, model prompts, web responses, or generated memory.

### AT-015 — Backup restoration
Restore a backup into an isolated environment and confirm that key business records, task state, relationships, and access scopes are valid.

## 5. AI-specific evaluation

For each future role, build a small versioned evaluation suite from representative inputs, edge cases, adversarial inputs, and known expected constraints. Compare outputs against explicit rubrics, not only another model's opinion. Evaluate grounding, completeness, correctness, calibrated uncertainty, authorized tool use, refusal/escalation, and regression from prompt/model changes.

Model updates, prompt changes, tool schema changes, memory-policy changes, and orchestration changes can affect behavior and require the relevant suite to run again.

## 6. Quality policy

- No open critical defect at any release gate.
- No known high-severity security defect at production release.
- All required phase tests pass; skipped tests need explicit risk approval and cannot substitute for critical safety/security checks.
- The current work package is closed only after its deliverables and acceptance evidence are attached to the Git checkpoint.
- If a blocking defect appears, stop progression, reproduce it, fix it, add a regression test, and rerun the affected suite.
