# AG-08 — Independent Quality & Acceptance Agent

> **Status: PROPOSED — not yet founder-approved or implemented.** This specification is a build contract proposal under [`17_AGENT_CLASSIFICATION.md`](../17_AGENT_CLASSIFICATION.md). Implementation must not start until the workforce classification is approved and platform prerequisites pass.

## Identification
- **Capability ID:** `AG-08`
- **Name:** Independent Quality & Acceptance Agent
- **Version:** 0.1-proposal
- **Owner/reviewer:** Founder / assigned implementation owner (to be set before the work package starts)
- **Status:** Proposed

## Purpose and boundaries

Independently review a produced result against the versioned task brief, acceptance criteria, evidence and deterministic test outputs. Return pass, rework or blocked with cited failures. The final state transition remains deterministic and may require founder approval.

### In scope
- Independently review a produced result against the versioned task brief, acceptance criteria, evidence and deterministic test outputs. Return pass, rework or blocked with cited failures. The final state transition remains deterministic and may require founder approval.
- Return typed, auditable results using the shared runtime contract.
- Report uncertainty, missing inputs, failed checks, and blockers explicitly.

### Explicitly out of scope
- Cannot waive explicit acceptance criteria, invent evidence, approve its own changes, silently ignore failed tests, or mark completed based solely on its own narrative.
- Bypassing task engine, tool gateway, server-side permissions, or required quality gates.
- Storing hidden state outside the approved data/memory interfaces.

### Required inputs
- Original objective/brief, versioned acceptance criteria, producer output/artifact references, source/evidence list, test outputs, policy decisions relevant to the task.

### Expected outputs/artifacts
- Typed review decision: pass/rework/blocked; criterion-by-criterion results; evidence references; defects by severity; missing checks; uncertainty; concrete rework request or reason for escalation.

### Upstream dependencies
- Task schema and artifact registry
- Deterministic test runner/results
- Read-only task/evidence scopes
- Producer role output

### Downstream consumers
- Task state machine; responsible producer for rework; founder for blocker/appeal

## Tools and authority
- **Allowed tools/integrations:** ['Read task brief, artifacts, sources, logs and test results; run approved read-only checks; request deterministic validation. Cannot change artifact or approval records it reviews.']
- **Read scopes:** Read-only scoped evidence for the current task; only the minimum cross-artifact context necessary.
- **Write scopes:** Review report and defect findings only. No edits to producer artifact, no policy changes, no approval/signature, no direct terminal state mutation.
- **Prohibited actions:** Cannot waive explicit acceptance criteria, invent evidence, approve its own changes, silently ignore failed tests, or mark completed based solely on its own narrative.
- **External side effects:** If criteria are ambiguous or contradictory, return blocked and ask for founder resolution instead of redefining acceptance post hoc. Where the same model is reused, record non-independent limitations.
- **Approval gates:** If criteria are ambiguous or contradictory, return blocked and ask for founder resolution instead of redefining acceptance post hoc. Where the same model is reused, record non-independent limitations.
- **Escalation conditions:** Missing material input, scope conflict, inaccessible/contradictory evidence, exceeded budget/deadline, permission denial, uncertain external outcome, or any requested action outside this role's allowed scope.

## Model and runtime
- **Required model capabilities:** Follow structured instructions; produce schema-valid structured output; call only registered tools when permitted; state uncertainty; resist untrusted content instructions.
- **Candidate provider/model configuration:** Shared model-provider adapter. Select model and provider only after Phase 4 benchmark; do not create a separate model server solely for this role.
- **Structured input/output schemas:** Shared input/output envelopes in [`06_AGENT_RUNTIME_CONTRACT.md`](../06_AGENT_RUNTIME_CONTRACT.md), plus role-specific schema to be pinned before implementation.
- **Memory sources allowed:** Use versioned QA rubrics and accepted non-sensitive defect patterns; do not update standards from a single judgment without review.
- **Memory write/promote policy:** Use versioned QA rubrics and accepted non-sensitive defect patterns; do not update standards from a single judgment without review. Only validated facts/procedures with provenance and approved retention may be promoted; every write is scoped and auditable.
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
  - Output claims success but a required test fails → rework/blocked.
  - Every failure maps to a specific acceptance criterion and evidence.
  - Missing source for a factual claim prevents full pass if the criterion requires provenance.
- **Negative/adversarial cases:**
  - Reviewer cannot access another client’s artifacts.
  - A changed artifact invalidates stale review and requires re-review.
  - Model-generated pass is rejected if deterministic quality gate fails.
- **Deterministic checks:** Schema validation; authorization; input/output limits; required fields; state transition validity; tool allowlist; provenance references where required; and the role-specific checks above.
- **Independent-review requirements:** AG-08 reviews producer outputs. AG-08 itself is validated against deterministic checks and golden evaluation cases; the runtime/founder makes any required final approval.
- **Grounding/evidence requirements:** Independently review a produced result against the versioned task brief, acceptance criteria, evidence and deterministic test outputs. Return pass, rework or blocked with cited failures. The final state transition remains deterministic and may require founder approval. Output must distinguish evidence-backed observations from assumptions or recommendations.
- **Known limitations:** This role cannot guarantee correctness across arbitrary tasks or inaccessible sources. Exact model, version, timeout, numeric budget, and evaluation thresholds remain to be measured and pinned before implementation.

## Observability and data
- **Required metrics:**
- Review agreement with deterministic checks
- Defect detection rate
- False-pass/false-fail rate on evaluation set
- Rework loop count
- Evidence references per decision
- **Audit events:** invocation, capability/version, input/output references, tool requests/results, memory reads/writes, policy decisions, retries, exceptions, evaluation result, approval/escalation, and final runtime outcome. Redact sensitive content.
- **Sensitive data processed:** Use least-privilege read-only access; redact irrelevant personal data and secrets from review context.
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
