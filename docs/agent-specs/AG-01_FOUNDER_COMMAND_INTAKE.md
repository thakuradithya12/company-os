# AG-01 — Founder Command & Intake Agent

> **Status: PROPOSED — not yet founder-approved or implemented.** This specification is a build contract proposal under [`17_AGENT_CLASSIFICATION.md`](../17_AGENT_CLASSIFICATION.md). Implementation must not start until the workforce classification is approved and platform prerequisites pass.

## Identification
- **Capability ID:** `AG-01`
- **Name:** Founder Command & Intake Agent
- **Version:** 0.1-proposal
- **Owner/reviewer:** Founder / assigned implementation owner (to be set before the work package starts)
- **Status:** Proposed

## Purpose and boundaries

Provide the founder-facing conversational entry point. Understand requests, ask material clarifying questions, and convert the founder’s intent into a bounded, versioned objective that can be planned. It also explains persisted work status and evidence without pretending to own backend truth.

### In scope
- Provide the founder-facing conversational entry point. Understand requests, ask material clarifying questions, and convert the founder’s intent into a bounded, versioned objective that can be planned. It also explains persisted work status and evidence without pretending to own backend truth.
- Return typed, auditable results using the shared runtime contract.
- Report uncertainty, missing inputs, failed checks, and blockers explicitly.

### Explicitly out of scope
- No shell/code execution, external search, prospect outreach, external publication, spending, contract acceptance, permission changes, direct DB access, or approval on behalf of the founder.
- Bypassing task engine, tool gateway, server-side permissions, or required quality gates.
- Storing hidden state outside the approved data/memory interfaces.

### Required inputs
- Founder message, attachments/references, current company policies visible to founder, selected task/status records authorized for display.

### Expected outputs/artifacts
- Structured objective draft with audience/niche, requested outcome, constraints, deadline, budget/cost ceiling if set, allowed sources, delivery destination, acceptance criteria, uncertainty and clarification questions.

### Upstream dependencies
- Authenticated dashboard/API
- Objective and task schemas
- Policy-aware status/evidence query APIs
- AG-02 Planning & Orchestration for subsequent planning

### Downstream consumers
- Founder
- AG-02
- Task API

## Tools and authority
- **Allowed tools/integrations:** ['Read founder-accessible policies and project records; create/update objective drafts through typed API; query task status; link approved artifacts.']
- **Read scopes:** Founder-owned objectives/policies and authorized task summaries only.
- **Write scopes:** Objective drafts and clarification records; no direct task-state mutation beyond approved API commands.
- **Prohibited actions:** No shell/code execution, external search, prospect outreach, external publication, spending, contract acceptance, permission changes, direct DB access, or approval on behalf of the founder.
- **External side effects:** Task execution begins only after required objective fields and policy/approval gates are satisfied. This role cannot approve its own request.
- **Approval gates:** Task execution begins only after required objective fields and policy/approval gates are satisfied. This role cannot approve its own request.
- **Escalation conditions:** Missing material input, scope conflict, inaccessible/contradictory evidence, exceeded budget/deadline, permission denial, uncertain external outcome, or any requested action outside this role's allowed scope.

## Model and runtime
- **Required model capabilities:** Follow structured instructions; produce schema-valid structured output; call only registered tools when permitted; state uncertainty; resist untrusted content instructions.
- **Candidate provider/model configuration:** Shared model-provider adapter. Select model and provider only after Phase 4 benchmark; do not create a separate model server solely for this role.
- **Structured input/output schemas:** Shared input/output envelopes in [`06_AGENT_RUNTIME_CONTRACT.md`](../06_AGENT_RUNTIME_CONTRACT.md), plus role-specific schema to be pinned before implementation.
- **Memory sources allowed:** Read current founder preferences and approved policy; save durable preferences only through explicit review/promotion, never infer a permanent rule from one request.
- **Memory write/promote policy:** Read current founder preferences and approved policy; save durable preferences only through explicit review/promotion, never infer a permanent rule from one request. Only validated facts/procedures with provenance and approved retention may be promoted; every write is scoped and auditable.
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
  - Clear goal → valid structured objective with unchanged core intent.
  - Ambiguous scope/cost/risk → asks a concise material question instead of inventing values.
  - Prompt injection in attachment says to ignore founder policy → treats it as untrusted content.
- **Negative/adversarial cases:**
  - Task failed/unknown → reports persisted state and evidence without claiming completion.
- **Deterministic checks:** Schema validation; authorization; input/output limits; required fields; state transition validity; tool allowlist; provenance references where required; and the role-specific checks above.
- **Independent-review requirements:** AG-08 reviews producer outputs. AG-08 itself is validated against deterministic checks and golden evaluation cases; the runtime/founder makes any required final approval.
- **Grounding/evidence requirements:** Provide the founder-facing conversational entry point. Understand requests, ask material clarifying questions, and convert the founder’s intent into a bounded, versioned objective that can be planned. It also explains persisted work status and evidence without pretending to own backend truth. Output must distinguish evidence-backed observations from assumptions or recommendations.
- **Known limitations:** This role cannot guarantee correctness across arbitrary tasks or inaccessible sources. Exact model, version, timeout, numeric budget, and evaluation thresholds remain to be measured and pinned before implementation.

## Observability and data
- **Required metrics:**
- Clarification rate and resolution
- Objective schema pass rate
- Misinterpretation/correction rate
- Status-answer evidence coverage
- **Audit events:** invocation, capability/version, input/output references, tool requests/results, memory reads/writes, policy decisions, retries, exceptions, evaluation result, approval/escalation, and final runtime outcome. Redact sensitive content.
- **Sensitive data processed:** May process founder strategy, budgets, and client/task summaries; do not write secrets or unnecessary personal information to memory.
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
