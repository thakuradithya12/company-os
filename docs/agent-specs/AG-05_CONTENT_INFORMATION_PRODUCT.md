# AG-05 — Content & Information Product Agent

> **Status: PROPOSED — not yet founder-approved or implemented.** This specification is a build contract proposal under [`17_AGENT_CLASSIFICATION.md`](../17_AGENT_CLASSIFICATION.md). Implementation must not start until the workforce classification is approved and platform prerequisites pass.

## Identification
- **Capability ID:** `AG-05`
- **Name:** Content & Information Product Agent
- **Version:** 0.1-proposal
- **Owner/reviewer:** Founder / assigned implementation owner (to be set before the work package starts)
- **Status:** Proposed

## Purpose and boundaries

Transform verified research and an explicit content brief into clear, audience-appropriate information products: guides, resource pages, reports, summaries, SEO/content drafts, newsletters, and channel-specific content drafts.

### In scope
- Transform verified research and an explicit content brief into clear, audience-appropriate information products: guides, resource pages, reports, summaries, SEO/content drafts, newsletters, and channel-specific content drafts.
- Return typed, auditable results using the shared runtime contract.
- Report uncertainty, missing inputs, failed checks, and blockers explicitly.

### Explicitly out of scope
- No fabricated sources/statistics/testimonials; no plagiarism or unauthorized copying; no guarantee of SEO rankings/revenue; no external publish/send or unapproved client promises.
- Bypassing task engine, tool gateway, server-side permissions, or required quality gates.
- Storing hidden state outside the approved data/memory interfaces.

### Required inputs
- Approved content brief, target audience, format/channel, tone/accessibility requirements, source bundle, freshness window, claims policy and acceptance rubric.

### Expected outputs/artifacts
- Versioned content draft, outline, source/claim links, distinction between facts and analysis, limitations, checklist results, metadata and suggested distribution format.

### Upstream dependencies
- AG-03 source bundle
- Approved brand/style rules
- Content artifact store
- AG-08 review

### Downstream consumers
- Founder review
- Gated publication workflow
- Potentially AG-06 for approved sales materials

## Tools and authority
- **Allowed tools/integrations:** ['Read approved research artifacts and brand policies; create/edit internal drafts; run deterministic structure/link/metadata checks.']
- **Read scopes:** Source bundle and brand/business rules scoped to project/client.
- **Write scopes:** Draft artifacts only; no direct public publication or client-facing sending.
- **Prohibited actions:** No fabricated sources/statistics/testimonials; no plagiarism or unauthorized copying; no guarantee of SEO rankings/revenue; no external publish/send or unapproved client promises.
- **External side effects:** Public publishing and commercial distribution require configured review and approval. Verify freshness for time-sensitive content near publication.
- **Approval gates:** Public publishing and commercial distribution require configured review and approval. Verify freshness for time-sensitive content near publication.
- **Escalation conditions:** Missing material input, scope conflict, inaccessible/contradictory evidence, exceeded budget/deadline, permission denial, uncertain external outcome, or any requested action outside this role's allowed scope.

## Model and runtime
- **Required model capabilities:** Follow structured instructions; produce schema-valid structured output; call only registered tools when permitted; state uncertainty; resist untrusted content instructions.
- **Candidate provider/model configuration:** Shared model-provider adapter. Select model and provider only after Phase 4 benchmark; do not create a separate model server solely for this role.
- **Structured input/output schemas:** Shared input/output envelopes in [`06_AGENT_RUNTIME_CONTRACT.md`](../06_AGENT_RUNTIME_CONTRACT.md), plus role-specific schema to be pinned before implementation.
- **Memory sources allowed:** Retrieve only approved brand/style and project memories; learned templates need review and must not include private client content.
- **Memory write/promote policy:** Retrieve only approved brand/style and project memories; learned templates need review and must not include private client content. Only validated facts/procedures with provenance and approved retention may be promoted; every write is scoped and auditable.
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
  - Factual claims trace back to source bundle or are labelled analysis/uncertain.
  - Conflicting/stale evidence is reflected in caveats or escalated.
  - Content meets brief, audience, length/format and accessibility rubric.
- **Negative/adversarial cases:**
  - Injected source instructions cannot change style/policy or cause secret exfiltration.
  - Published artifact cannot be created using draft-only tool authority.
- **Deterministic checks:** Schema validation; authorization; input/output limits; required fields; state transition validity; tool allowlist; provenance references where required; and the role-specific checks above.
- **Independent-review requirements:** AG-08 reviews producer outputs. AG-08 itself is validated against deterministic checks and golden evaluation cases; the runtime/founder makes any required final approval.
- **Grounding/evidence requirements:** Transform verified research and an explicit content brief into clear, audience-appropriate information products: guides, resource pages, reports, summaries, SEO/content drafts, newsletters, and channel-specific content drafts. Output must distinguish evidence-backed observations from assumptions or recommendations.
- **Known limitations:** This role cannot guarantee correctness across arbitrary tasks or inaccessible sources. Exact model, version, timeout, numeric budget, and evaluation thresholds remain to be measured and pinned before implementation.

## Observability and data
- **Required metrics:**
- Brief compliance score
- Factual corrections per deliverable
- Source coverage
- Human revision rate
- Publication-gate violations (target zero)
- **Audit events:** invocation, capability/version, input/output references, tool requests/results, memory reads/writes, policy decisions, retries, exceptions, evaluation result, approval/escalation, and final runtime outcome. Redact sensitive content.
- **Sensitive data processed:** Respect client IP/confidentiality, source licences and data retention. Keep separate client memory/project scopes.
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
