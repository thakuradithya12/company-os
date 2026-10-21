# AG-02 — Planning & Orchestration Agent

> **Status: PROPOSED — not yet founder-approved or implemented.** This specification is a build contract proposal under [`17_AGENT_CLASSIFICATION.md`](../17_AGENT_CLASSIFICATION.md). Implementation must not start until the workforce classification is approved and platform prerequisites pass.

## Identification
- **Capability ID:** `AG-02`
- **Name:** Planning & Orchestration Agent
- **Version:** 0.1-proposal
- **Owner/reviewer:** Founder / assigned implementation owner (to be set before the work package starts)
- **Status:** Proposed

## Purpose and boundaries

Propose plans and dependency graphs for a bounded objective, select only registered capabilities, and aggregate typed outcomes. A deterministic task/workflow engine—not the model—owns task IDs, state transitions, permissions, scheduling, retries, cancellation and recovery.

### In scope
- Propose plans and dependency graphs for a bounded objective, select only registered capabilities, and aggregate typed outcomes. A deterministic task/workflow engine—not the model—owns task IDs, state transitions, permissions, scheduling, retries, cancellation and recovery.
- Return typed, auditable results using the shared runtime contract.
- Report uncertainty, missing inputs, failed checks, and blockers explicitly.

### Explicitly out of scope
- Cannot grant permissions, change policies/budgets, waive acceptance tests, mark complete by itself, directly run host shell, contact customers, accept deals, or force retry of uncertain side effects.
- Bypassing task engine, tool gateway, server-side permissions, or required quality gates.
- Storing hidden state outside the approved data/memory interfaces.

### Required inputs
- Approved structured objective, registered capability catalog, current policy/limits, available resources, prior approved procedures.

### Expected outputs/artifacts
- Versioned plan; tasks and dependencies; capability IDs; per-task inputs/outputs; acceptance criteria; resource estimates; risk/approval flags; unresolved assumptions.

### Upstream dependencies
- Objective schema
- Capability registry
- Deterministic policy service and durable task engine
- Memory/retrieval interfaces

### Downstream consumers
- Durable task engine
- Selected capability roles
- AG-08 review path

## Tools and authority
- **Allowed tools/integrations:** ['Read capability catalog and approved procedures; propose structured plan; request re-plan; aggregate persisted task results.']
- **Read scopes:** Objective scope, allowed capability metadata, relevant procedure memory, task outcomes in scope.
- **Write scopes:** Plan proposals only; execution engine validates/persists accepted plan. Cannot directly set terminal state or invoke unregistered tools.
- **Prohibited actions:** Cannot grant permissions, change policies/budgets, waive acceptance tests, mark complete by itself, directly run host shell, contact customers, accept deals, or force retry of uncertain side effects.
- **External side effects:** Material scope, budget, deadline, risk, external side effect, or authority change requires founder decision per policy.
- **Approval gates:** Material scope, budget, deadline, risk, external side effect, or authority change requires founder decision per policy.
- **Escalation conditions:** Missing material input, scope conflict, inaccessible/contradictory evidence, exceeded budget/deadline, permission denial, uncertain external outcome, or any requested action outside this role's allowed scope.

## Model and runtime
- **Required model capabilities:** Follow structured instructions; produce schema-valid structured output; call only registered tools when permitted; state uncertainty; resist untrusted content instructions.
- **Candidate provider/model configuration:** Shared model-provider adapter. Select model and provider only after Phase 4 benchmark; do not create a separate model server solely for this role.
- **Structured input/output schemas:** Shared input/output envelopes in [`06_AGENT_RUNTIME_CONTRACT.md`](../06_AGENT_RUNTIME_CONTRACT.md), plus role-specific schema to be pinned before implementation.
- **Memory sources allowed:** Read only approved procedural patterns and current policy; propose proven reusable workflow only after outcome evidence; never overwrite policy memory.
- **Memory write/promote policy:** Read only approved procedural patterns and current policy; propose proven reusable workflow only after outcome evidence; never overwrite policy memory. Only validated facts/procedures with provenance and approved retention may be promoted; every write is scoped and auditable.
- **Timeout and maximum steps:** Finite per-task limits are mandatory. Numerical defaults must be benchmarked, documented in policy/configuration, and tested before this role is enabled; missing values must fail closed rather than mean unlimited.
- **Cost/token/resource limits:** Per-role budgets for duration, model calls, tokens where provider supports them, output bytes, tool calls, concurrency, and monetary spend must be configured before implementation. No unbounded loops.
- **Retry and fallback rules:** Retry only classified transient failures with bounded backoff. Do not retry external side effects when outcome is unknown until reconciliation. Report partial/blocked when fallback could change correctness or authority.

## Quality
- **Acceptance criteria:**
  - The role's required input schema is validated and missing required data is handled without fabricated assumptions.
  - Output conforms to the versioned role schema and shared runtime envelope.
  - Every tool/action request is independently checked by the tool gateway and policy service.
  - Results include relevant evidence, limitations and checks actually performed.
  - Required role-specific evaluation cases below pass; no blocking defect remains.
- **Positive evaluation cases:**
  - Objective decomposed into valid tasks with dependency graph and explicit acceptance criteria.
  - Missing capability → blocked/escalated, not hallucinated capability.
  - Dependency cycle or unknown role → rejected by deterministic validator.
- **Negative/adversarial cases:**
  - Provider result says complete without evidence → task remains unaccepted.
  - Unknown call outcome → no duplicate retry; reconciliation required.
- **Deterministic checks:** Schema validation; authorization; input/output limits; required fields; state transition validity; tool allowlist; provenance references where required; and the role-specific checks above.
- **Independent-review requirements:** AG-08 reviews producer outputs. AG-08 itself is validated against deterministic checks and golden evaluation cases; the runtime/founder makes any required final approval.
- **Grounding/evidence requirements:** Propose plans and dependency graphs for a bounded objective, select only registered capabilities, and aggregate typed outcomes. A deterministic task/workflow engine—not the model—owns task IDs, state transitions, permissions, scheduling, retries, cancellation and recovery. Output must distinguish evidence-backed observations from assumptions or recommendations.
- **Known limitations:** This role cannot guarantee correctness across arbitrary tasks or inaccessible sources. Exact model, version, timeout, numeric budget, and evaluation thresholds remain to be measured and pinned before implementation.

## Observability and data
- **Required metrics:**
- Plan validation pass rate
- Replan frequency and reason
- Unowned-task count (target zero)
- Blocked tasks by cause
- Plan estimate versus actual where measurable
- **Audit events:** invocation, capability/version, input/output references, tool requests/results, memory reads/writes, policy decisions, retries, exceptions, evaluation result, approval/escalation, and final runtime outcome. Redact sensitive content.
- **Sensitive data processed:** Cross-company planning metadata may include client work; honor client/project data scopes.
- **Retention requirements:** Follow [`05_SECURITY_PRIVACY_AND_GOVERNANCE.md`](../05_SECURITY_PRIVACY_AND_GOVERNANCE.md) and the task/domain retention policy. Do not invent a retention period; it must be specified before production.
- **Access restrictions:** Role-scoped least privilege; server-enforced permissions; no direct database credentials, secrets, unrestricted filesystem/network, or direct state mutation.

## Readiness gate
- [x] Role is proposed as a distinct initial responsibility and checked against the classification inventory.
- [x] Proposed purpose and boundaries are documented.
- [x] Proposed inputs, outputs, and dependencies are documented.
- [x] Permission boundaries and prohibited actions are documented.
- [x] Candidate acceptance and adversarial evaluations are identified.
- [ ] Exact role schemas, numeric resource budgets, model choice, and thresholds are pinned before implementation.
- [ ] Dependencies and integration contracts are approved.
- [ ] Founder approves this role and the overall workforce classification.
