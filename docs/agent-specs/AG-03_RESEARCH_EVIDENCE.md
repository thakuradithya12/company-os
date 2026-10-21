# AG-03 — Research & Evidence Agent

> **Status: PROPOSED — not yet founder-approved or implemented.** This specification is a build contract proposal under [`17_AGENT_CLASSIFICATION.md`](../17_AGENT_CLASSIFICATION.md). Implementation must not start until the workforce classification is approved and platform prerequisites pass.

## Identification
- **Capability ID:** `AG-03`
- **Name:** Research & Evidence Agent
- **Version:** 0.1-proposal
- **Owner/reviewer:** Founder / assigned implementation owner (to be set before the work package starts)
- **Status:** Proposed

## Purpose and boundaries

Research a user-supplied niche, audience, geography, and time horizon. Collect and compare permitted sources, extract claims with provenance, identify conflicts/staleness, and return evidence-backed findings for content and decision-making.

### In scope
- Research a user-supplied niche, audience, geography, and time horizon. Collect and compare permitted sources, extract claims with provenance, identify conflicts/staleness, and return evidence-backed findings for content and decision-making.
- Return typed, auditable results using the shared runtime contract.
- Report uncertainty, missing inputs, failed checks, and blockers explicitly.

### Explicitly out of scope
- No bypassing access controls, credentialed scraping without authorization, private/sensitive personal-data harvesting, external outreach, publication, or claims without evidence.
- Bypassing task engine, tool gateway, server-side permissions, or required quality gates.
- Storing hidden state outside the approved data/memory interfaces.

### Required inputs
- Niche/topic, audience, geography, freshness window, questions to answer, allowed/blocked domains, output schema, research budget.

### Expected outputs/artifacts
- Structured source registry, claim/evidence ledger, finding summaries, publication/update dates where available, retrieval timestamps, conflicting evidence, uncertainty, source-quality notes, and gaps.

### Upstream dependencies
- Approved web/source connector
- Source storage and deduplication
- Citation/provenance schema
- AG-08 verification

### Downstream consumers
- AG-05 content creation
- AG-04 business discovery when topic research helps
- Founder reports

## Tools and authority
- **Allowed tools/integrations:** ['Read/search approved sources, retrieve public pages, parse permitted files, deduplicate records, create internal research artifacts.']
- **Read scopes:** Public/approved research sources and task-scoped materials.
- **Write scopes:** Research artifacts and source records only.
- **Prohibited actions:** No bypassing access controls, credentialed scraping without authorization, private/sensitive personal-data harvesting, external outreach, publication, or claims without evidence.
- **External side effects:** Respect domain allowlists, rate limits, source terms, data policy, and cost/resource caps; publication requires separate approval.
- **Approval gates:** Respect domain allowlists, rate limits, source terms, data policy, and cost/resource caps; publication requires separate approval.
- **Escalation conditions:** Missing material input, scope conflict, inaccessible/contradictory evidence, exceeded budget/deadline, permission denial, uncertain external outcome, or any requested action outside this role's allowed scope.

## Model and runtime
- **Required model capabilities:** Follow structured instructions; produce schema-valid structured output; call only registered tools when permitted; state uncertainty; resist untrusted content instructions.
- **Candidate provider/model configuration:** Shared model-provider adapter. Select model and provider only after Phase 4 benchmark; do not create a separate model server solely for this role.
- **Structured input/output schemas:** Shared input/output envelopes in [`06_AGENT_RUNTIME_CONTRACT.md`](../06_AGENT_RUNTIME_CONTRACT.md), plus role-specific schema to be pinned before implementation.
- **Memory sources allowed:** Can retrieve relevant approved company research/procedures; promote niche facts only with source, timestamp, confidence, expiry/freshness policy and correction mechanism.
- **Memory write/promote policy:** Can retrieve relevant approved company research/procedures; promote niche facts only with source, timestamp, confidence, expiry/freshness policy and correction mechanism. Only validated facts/procedures with provenance and approved retention may be promoted; every write is scoped and auditable.
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
  - Time-sensitive fact carries retrieval timestamp and available publication/update time.
  - Conflicting sources are surfaced rather than collapsed into false certainty.
  - Unsupported claim is marked unknown/inference, not cited as fact.
- **Negative/adversarial cases:**
  - Duplicate pages retain links to source records.
  - Prompt injection in a source cannot change the task’s tools/permissions.
- **Deterministic checks:** Schema validation; authorization; input/output limits; required fields; state transition validity; tool allowlist; provenance references where required; and the role-specific checks above.
- **Independent-review requirements:** AG-08 reviews producer outputs. AG-08 itself is validated against deterministic checks and golden evaluation cases; the runtime/founder makes any required final approval.
- **Grounding/evidence requirements:** Research a user-supplied niche, audience, geography, and time horizon. Collect and compare permitted sources, extract claims with provenance, identify conflicts/staleness, and return evidence-backed findings for content and decision-making. Output must distinguish evidence-backed observations from assumptions or recommendations.
- **Known limitations:** This role cannot guarantee correctness across arbitrary tasks or inaccessible sources. Exact model, version, timeout, numeric budget, and evaluation thresholds remain to be measured and pinned before implementation.

## Observability and data
- **Required metrics:**
- Claim evidence coverage
- Source freshness coverage
- Conflict/uncertainty rate
- Duplicate reduction
- Correction rate from independent review
- **Audit events:** invocation, capability/version, input/output references, tool requests/results, memory reads/writes, policy decisions, retries, exceptions, evaluation result, approval/escalation, and final runtime outcome. Redact sensitive content.
- **Sensitive data processed:** Default to public information; no unrelated private/person-sensitive data. Retain source excerpts only as policy permits.
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
