# AG-06 — Client Acquisition & Deal Agent

> **Status: PROPOSED — not yet founder-approved or implemented.** This specification is a build contract proposal under [`17_AGENT_CLASSIFICATION.md`](../17_AGENT_CLASSIFICATION.md). Implementation must not start until the workforce classification is approved and platform prerequisites pass.

## Identification
- **Capability ID:** `AG-06`
- **Name:** Client Acquisition & Deal Agent
- **Version:** 0.1-proposal
- **Owner/reviewer:** Founder / assigned implementation owner (to be set before the work package starts)
- **Status:** Proposed

## Purpose and boundaries

Prepare prospect outreach, manage authorized customer conversations, capture requirements, draft proposals, track follow-ups, and negotiate only inside founder-approved scope/pricing/commitment boundaries. Voice is an adapter/channel, not a separate authority bypass.

### In scope
- Prepare prospect outreach, manage authorized customer conversations, capture requirements, draft proposals, track follow-ups, and negotiate only inside founder-approved scope/pricing/commitment boundaries. Voice is an adapter/channel, not a separate authority bypass.
- Return typed, auditable results using the shared runtime contract.
- Report uncertainty, missing inputs, failed checks, and blockers explicitly.

### Explicitly out of scope
- No personal-SIM automated telemarketing; no contact when suppressed/ineligible; no false identity, fake urgency or fabricated claims; no invented prices; no binding contract acceptance, signature, purchase, payment, or out-of-limit promise without explicit founder authority.
- Bypassing task engine, tool gateway, server-side permissions, or required quality gates.
- Storing hidden state outside the approved data/memory interfaces.

### Required inputs
- Qualified opportunity, source-backed reason for contact, contact eligibility evidence, prior interactions, approved service catalogue/pricing, proposal template, negotiation limits, channel policy.

### Expected outputs/artifacts
- Personalized draft/script; conversation summary with evidence; requirements brief; objection/questions list; proposal versions; follow-up task; deal stage; escalation for any policy boundary or ambiguity.

### Upstream dependencies
- AG-04 qualified opportunity
- CRM and proposal records
- Server-side policy/suppression
- Approved email/messaging/telephony adapter
- Approved pricing/authority settings
- Founder approvals

### Downstream consumers
- Founder deal approval
- AG-07 delivery plan after an accepted/verified agreement
- AG-08 proposal consistency review where configured

## Tools and authority
- **Allowed tools/integrations:** ['Initially draft-only. After separate communication gate: invoke only approved provider send/call tools, query eligibility, record outcomes, save conversation notes, and draft proposal versions. Tool gateway owns actual execution and audit.']
- **Read scopes:** Qualified lead evidence, scoped communication history, approved service catalogue/pricing limits, suppression/eligibility decision, proposal versions.
- **Write scopes:** Drafts, conversation summaries, requirements, follow-up records, proposal drafts and deal-stage requests.
- **Prohibited actions:** No personal-SIM automated telemarketing; no contact when suppressed/ineligible; no false identity, fake urgency or fabricated claims; no invented prices; no binding contract acceptance, signature, purchase, payment, or out-of-limit promise without explicit founder authority.
- **External side effects:** Live outbound calling/messaging disabled by default. Before enabling, confirm current law, provider requirements, consent/preferences/registration, disclosures, opt-out handling and provider outcome reconciliation. Every binding term and any out-of-limit negotiation requires founder approval in initial release.
- **Approval gates:** Live outbound calling/messaging disabled by default. Before enabling, confirm current law, provider requirements, consent/preferences/registration, disclosures, opt-out handling and provider outcome reconciliation. Every binding term and any out-of-limit negotiation requires founder approval in initial release.
- **Escalation conditions:** Missing material input, scope conflict, inaccessible/contradictory evidence, exceeded budget/deadline, permission denial, uncertain external outcome, or any requested action outside this role's allowed scope.

## Model and runtime
- **Required model capabilities:** Follow structured instructions; produce schema-valid structured output; call only registered tools when permitted; state uncertainty; resist untrusted content instructions.
- **Candidate provider/model configuration:** Shared model-provider adapter. Select model and provider only after Phase 4 benchmark; do not create a separate model server solely for this role.
- **Structured input/output schemas:** Shared input/output envelopes in [`06_AGENT_RUNTIME_CONTRACT.md`](../06_AGENT_RUNTIME_CONTRACT.md), plus role-specific schema to be pinned before implementation.
- **Memory sources allowed:** Retrieve only account/client-scoped history and approved scripts/policies. Never reuse one prospect’s confidential details with another. Call recording/transcription requires provider and legal policy review.
- **Memory write/promote policy:** Retrieve only account/client-scoped history and approved scripts/policies. Never reuse one prospect’s confidential details with another. Call recording/transcription requires provider and legal policy review. Only validated facts/procedures with provenance and approved retention may be promoted; every write is scoped and auditable.
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
  - Opted-out or ineligible prospect blocked at final server-side boundary even if agent asks to call.
  - Provider timeout with unknown send/call outcome leads to reconciliation, not blind retry.
  - Proposal price/discount/scope outside authorized bounds is blocked/escalated.
- **Negative/adversarial cases:**
  - Prospect requests no more contact → suppression is persisted and immediately enforced.
  - An informal “sounds good” is not recorded as proof of signed/accepted contract.
  - Conversation claims are distinguished from verified customer commitments.
- **Deterministic checks:** Schema validation; authorization; input/output limits; required fields; state transition validity; tool allowlist; provenance references where required; and the role-specific checks above.
- **Independent-review requirements:** AG-08 reviews producer outputs. AG-08 itself is validated against deterministic checks and golden evaluation cases; the runtime/founder makes any required final approval.
- **Grounding/evidence requirements:** Prepare prospect outreach, manage authorized customer conversations, capture requirements, draft proposals, track follow-ups, and negotiate only inside founder-approved scope/pricing/commitment boundaries. Voice is an adapter/channel, not a separate authority bypass. Output must distinguish evidence-backed observations from assumptions or recommendations.
- **Known limitations:** This role cannot guarantee correctness across arbitrary tasks or inaccessible sources. Exact model, version, timeout, numeric budget, and evaluation thresholds remain to be measured and pinned before implementation.

## Observability and data
- **Required metrics:**
- Eligible-contact rate
- Suppression block correctness
- Qualified conversation rate where measurable
- Proposal-policy pass rate
- Unknown-outcome reconciliation rate
- Complaints/opt-outs
- **Audit events:** invocation, capability/version, input/output references, tool requests/results, memory reads/writes, policy decisions, retries, exceptions, evaluation result, approval/escalation, and final runtime outcome. Redact sensitive content.
- **Sensitive data processed:** May process contact details and conversation transcripts. Minimize collection, restrict access, redact secrets, and apply reviewed retention/deletion rules.
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
