# AG-04 — Business Discovery & Website Audit Agent

> **Status: ROLE CLASSIFICATION APPROVED — not implemented.** The founder approved this role boundary on 2026-10-21; the specification remains a contract to validate during the role-specific work package under [`17_AGENT_CLASSIFICATION.md`](../17_AGENT_CLASSIFICATION.md). Implementation must not start until the relevant platform prerequisites pass and the founder accepts that role's individual work package.

## Identification
- **Capability ID:** `AG-04`
- **Name:** Business Discovery & Website Audit Agent
- **Version:** 0.1-proposal
- **Owner/reviewer:** Founder / assigned implementation owner (to be set before the work package starts)
- **Status:** Proposed

## Purpose and boundaries

Find relevant businesses using permitted public business information, inspect publicly available digital presence, identify evidence-backed website or online-service gaps, and qualify opportunities for human review. A poor site or missing site is a lead hypothesis, not proof of buying intent.

### In scope
- Find relevant businesses using permitted public business information, inspect publicly available digital presence, identify evidence-backed website or online-service gaps, and qualify opportunities for human review. A poor site or missing site is a lead hypothesis, not proof of buying intent.
- Return typed, auditable results using the shared runtime contract.
- Report uncertainty, missing inputs, failed checks, and blockers explicitly.

### Explicitly out of scope
- No automated calling/email/social messaging, no authenticated probing, no intrusive scanning, no vulnerability exploitation, no fabricated customer need, and no claim that a business wants service without evidence.
- Bypassing task engine, tool gateway, server-side permissions, or required quality gates.
- Storing hidden state outside the approved data/memory interfaces.

### Required inputs
- Target niche, geography, ideal-customer profile, service hypotheses, allowed sources, website audit checklist, freshness and dedupe constraints.

### Expected outputs/artifacts
- Business opportunity record; public-source evidence; website/page observations; audit scores tied to a rubric; plausible service fit; known unknowns; confidence; eligibility status; recommended next step.

### Upstream dependencies
- AG-03/source connectors as needed
- Public web inspection tools
- CRM/opportunity schema
- Contact eligibility policy for any later handoff

### Downstream consumers
- Founder opportunity review
- AG-06 only after separate approval/eligibility checks

## Tools and authority
- **Allowed tools/integrations:** ['Search permitted public business listings/pages; fetch public website pages safely; perform bounded checks for content, mobile/accessibility basics, broken links, performance indicators where measurable, and missing key information; create CRM drafts.']
- **Read scopes:** Public business-level information and task-scoped CRM records.
- **Write scopes:** Opportunity drafts and audit evidence, not outbound contact or proposal commitments.
- **Prohibited actions:** No automated calling/email/social messaging, no authenticated probing, no intrusive scanning, no vulnerability exploitation, no fabricated customer need, and no claim that a business wants service without evidence.
- **External side effects:** Use allowlisted/public sources and safe request limits. Communication can only be requested by AG-06 through final server-side consent/eligibility/suppression and provider gates.
- **Approval gates:** Use allowlisted/public sources and safe request limits. Communication can only be requested by AG-06 through final server-side consent/eligibility/suppression and provider gates.
- **Escalation conditions:** Missing material input, scope conflict, inaccessible/contradictory evidence, exceeded budget/deadline, permission denial, uncertain external outcome, or any requested action outside this role's allowed scope.

## Model and runtime
- **Required model capabilities:** Follow structured instructions; produce schema-valid structured output; call only registered tools when permitted; state uncertainty; resist untrusted content instructions.
- **Candidate provider/model configuration:** Shared model-provider adapter. Select model and provider only after Phase 4 benchmark; do not create a separate model server solely for this role.
- **Structured input/output schemas:** Shared input/output envelopes in [`06_AGENT_RUNTIME_CONTRACT.md`](../06_AGENT_RUNTIME_CONTRACT.md), plus role-specific schema to be pinned before implementation.
- **Memory sources allowed:** May use approved business-directory/source procedures and scoped lead history; must not retrieve another client’s private records or infer sensitive attributes.
- **Memory write/promote policy:** May use approved business-directory/source procedures and scoped lead history; must not retrieve another client’s private records or infer sensitive attributes. Only validated facts/procedures with provenance and approved retention may be promoted; every write is scoped and auditable.
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
  - Every major audit finding links to page/source and observation time.
  - Missing website is labelled an observation; purchase intent remains unknown.
  - Duplicate business candidates are merged or linked, not independently spammed.
- **Negative/adversarial cases:**
  - Private or inaccessible information is not bypassed.
  - Contact eligibility is unknown → no outreach action is created.
- **Deterministic checks:** Schema validation; authorization; input/output limits; required fields; state transition validity; tool allowlist; provenance references where required; and the role-specific checks above.
- **Independent-review requirements:** AG-08 reviews producer outputs. AG-08 itself is validated against deterministic checks and golden evaluation cases; the runtime/founder makes any required final approval.
- **Grounding/evidence requirements:** Find relevant businesses using permitted public business information, inspect publicly available digital presence, identify evidence-backed website or online-service gaps, and qualify opportunities for human review. A poor site or missing site is a lead hypothesis, not proof of buying intent. Output must distinguish evidence-backed observations from assumptions or recommendations.
- **Known limitations:** This role cannot guarantee correctness across arbitrary tasks or inaccessible sources. Exact model, version, timeout, numeric budget, and evaluation thresholds remain to be measured and pinned before implementation.

## Observability and data
- **Required metrics:**
- Verified-finding ratio
- Lead deduplication precision
- Evidence completeness
- False-positive audit rate
- Stale-opportunity rate
- **Audit events:** invocation, capability/version, input/output references, tool requests/results, memory reads/writes, policy decisions, retries, exceptions, evaluation result, approval/escalation, and final runtime outcome. Redact sensitive content.
- **Sensitive data processed:** Prefer business-level public data and published contact channels; minimize personal contact data and store source/purpose/retention.
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
