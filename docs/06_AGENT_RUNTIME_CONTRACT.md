# 06 — Agent Runtime Contract

> This document defines how any future agent role must integrate with Company OS. It does **not** decide the number or classification of agents.

## 1. Purpose

All roles must use the same auditable contract so the orchestrator can delegate work without relying on free-form handoffs, hidden state, or agent-specific ad hoc behavior.

## 2. Required role specification

Before a role is implemented, its specification must define:
- unique role/capability ID and version;
- business purpose and measurable responsibilities;
- allowed inputs and required input schema;
- output schema and artifact expectations;
- skills/tools it may use, with permission scopes;
- forbidden actions and escalation conditions;
- model/provider requirements and fallback behavior;
- context/memory sources and write policy;
- time, token/cost, retries, concurrency, and output-size limits;
- acceptance criteria and evaluation cases;
- dependency interfaces and error handling;
- observable metrics and audit requirements;
- owner/reviewer and change history.

Use `docs/templates/AGENT_ROLE_SPEC_TEMPLATE.md` during the later role-classification phase.

## 3. Input envelope

At minimum:

```json
{
  "task_id": "stable-task-id",
  "attempt_id": "stable-attempt-id",
  "objective": "precise task objective",
  "capability_id": "registered-capability-id",
  "capability_version": "version",
  "inputs": [],
  "constraints": [],
  "acceptance_criteria": [],
  "allowed_tools": [],
  "data_scope": [],
  "deadline": "timestamp-or-null",
  "budgets": {
    "max_steps": 0,
    "max_duration_seconds": 0,
    "max_output_bytes": 0,
    "max_model_calls": 0
  },
  "trace_id": "correlation-id"
}
```

The values above are illustrative schema fields; actual types and constraints must be finalized in API/schema implementation. Zero values mean “not configured” only if the schema explicitly defines that behavior; do not infer unlimited permission from a missing limit.

## 4. Output envelope

The runtime expects a typed result with:
- status: `success`, `partial`, `needs_input`, `blocked`, or `failure`;
- concise result summary;
- typed output fields or artifact references;
- source/evidence references when factual claims are made;
- tests/checks run and outcomes;
- uncertainty, assumptions, and limitations;
- error code/category when relevant;
- proposed next step or escalation reason;
- trace and attempt identifiers.

Validate output against a schema. Reject malformed outputs; do not trust an unvalidated string that claims to be JSON. A `success` result can still fail acceptance criteria and must be evaluated by the runtime.

## 5. Tool call lifecycle

1. Model proposes a tool and arguments.
2. Runtime confirms the tool is registered and enabled.
3. Runtime validates input schema and normalizes arguments.
4. Runtime checks user authorization, role scope, policy, quotas, approval record, and risk tier.
5. Runtime checks idempotency/reconciliation needs.
6. Tool executes with timeout and isolation.
7. Result is validated, redacted where necessary, persisted, and linked to the execution trace.
8. The task state machine is updated by deterministic application logic.

Tool calls are not authorized because a model asks for them. Unknown tools and out-of-scope arguments fail closed.

## 6. Memory contract

- Read only the memory scopes allowed by the active task.
- Cite memory/source IDs for important factual or policy-derived claims.
- Do not write a procedural memory item directly from a single unverified output.
- Propose reusable knowledge with source/outcome evidence; the knowledge policy decides whether to promote it.
- Treat retrieved memory as context, not as a replacement for current authorization and policy.

## 7. Inter-agent communication

Use explicit task IDs and schema-validated messages. A handoff states what was requested, what was done, what evidence exists, what remains, and what receiving capability is expected to do. Avoid unbounded conversations between agents. The orchestrator remains responsible for dependency tracking and conflict resolution.

## 8. Verification model

Verification should combine deterministic checks (schema, tests, calculations, source reachability, policy checks) with independent semantic review where needed. A reviewing agent should receive the objective, acceptance criteria, the result, and evidence; it should not be asked simply whether the producer did a good job. Where independence is weak because the same model or prompt is reused, record that limitation.

## 9. Completion and escalation

A role returns partial/blocked status when it lacks data, access, authority, confidence, or time. It must not invent sources, claim external actions succeeded without provider confirmation, silently broaden scope, or conceal failed checks. Escalations go to the founder/dashboard with a specific decision request.

## 10. Required metrics

At minimum record: task success/failure/partial counts, acceptance pass rate, retry count, time to first output, total duration, model/tool use, cost when available, exception categories, and human intervention points. Metrics must be derived from persisted events and should be disaggregated by capability version.
