# AG-07 — Digital Solution Builder Agent

> **Status: PROPOSED — not yet founder-approved or implemented.** This specification is a build contract proposal under [`17_AGENT_CLASSIFICATION.md`](../17_AGENT_CLASSIFICATION.md). Implementation must not start until the workforce classification is approved and platform prerequisites pass.

## Identification
- **Capability ID:** `AG-07`
- **Name:** Digital Solution Builder Agent
- **Version:** 0.1-proposal
- **Owner/reviewer:** Founder / assigned implementation owner (to be set before the work package starts)
- **Status:** Proposed

## Purpose and boundaries

Produce scoped websites, web changes, scripts, and bounded online automations from an approved requirements brief. Start with website/software deliverables; add other digital-production skills only when separately scoped and tested.

### In scope
- Produce scoped websites, web changes, scripts, and bounded online automations from an approved requirements brief. Start with website/software deliverables; add other digital-production skills only when separately scoped and tested.
- Return typed, auditable results using the shared runtime contract.
- Report uncertainty, missing inputs, failed checks, and blockers explicitly.

### Explicitly out of scope
- No arbitrary host shell execution, Docker socket access, secret extraction, unauthorized external network, production credential use, destructive repo history changes, or scope expansion without approval.
- Bypassing task engine, tool gateway, server-side permissions, or required quality gates.
- Storing hidden state outside the approved data/memory interfaces.

### Required inputs
- Versioned project brief, approved scope, repo/workspace reference, design/system constraints, acceptance checklist, dependencies, environment restrictions, resource limits.

### Expected outputs/artifacts
- Version-controlled source/artifact references, commit or artifact hash, build/test output, preview instructions/URL where available, known limitations, dependency manifest, handover checklist.

### Upstream dependencies
- Approved deal/project brief or founder-provided internal task
- Isolated build/test workspace
- Repository/artifact access broker
- AG-08 and deterministic CI/build checks

### Downstream consumers
- AG-08 review
- Founder deployment/delivery approval
- Handover workflow

## Tools and authority
- **Allowed tools/integrations:** ['Read/write only assigned workspace/repository; run allowlisted build/test/typecheck/lint commands in disposable isolated workers; create preview artifacts; report exact test evidence.']
- **Read scopes:** Only assigned project/repository and task requirements. No unrelated client repository or production secrets.
- **Write scopes:** Assigned branch/workspace and build artifacts. No direct production deploy, DNS, billing, or unrestricted host access by default.
- **Prohibited actions:** No arbitrary host shell execution, Docker socket access, secret extraction, unauthorized external network, production credential use, destructive repo history changes, or scope expansion without approval.
- **External side effects:** Code execution isolated with non-root, CPU/memory/process/disk/time limits, controlled mounts, restricted network and forced cleanup. Public deployment remains a separately gated operation.
- **Approval gates:** Code execution isolated with non-root, CPU/memory/process/disk/time limits, controlled mounts, restricted network and forced cleanup. Public deployment remains a separately gated operation.
- **Escalation conditions:** Missing material input, scope conflict, inaccessible/contradictory evidence, exceeded budget/deadline, permission denial, uncertain external outcome, or any requested action outside this role's allowed scope.

## Model and runtime
- **Required model capabilities:** Follow structured instructions; produce schema-valid structured output; call only registered tools when permitted; state uncertainty; resist untrusted content instructions.
- **Candidate provider/model configuration:** Shared model-provider adapter. Select model and provider only after Phase 4 benchmark; do not create a separate model server solely for this role.
- **Structured input/output schemas:** Shared input/output envelopes in [`06_AGENT_RUNTIME_CONTRACT.md`](../06_AGENT_RUNTIME_CONTRACT.md), plus role-specific schema to be pinned before implementation.
- **Memory sources allowed:** Read approved project style and reusable non-confidential patterns; do not cross-contaminate client code, secrets, or private architecture.
- **Memory write/promote policy:** Read approved project style and reusable non-confidential patterns; do not cross-contaminate client code, secrets, or private architecture. Only validated facts/procedures with provenance and approved retention may be promoted; every write is scoped and auditable.
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
  - A small approved site builds and passes specified tests in clean workspace.
  - Injected malicious instructions in README/source files cannot change runtime policy or expose secrets.
  - Build failure is reported accurately and linked to logs; not marked completed.
- **Negative/adversarial cases:**
  - Artifact commit/hash matches preview/build tested.
  - Cancellation cleans temporary resources within configured bound.
  - No production deployment tool available to default role.
- **Deterministic checks:** Schema validation; authorization; input/output limits; required fields; state transition validity; tool allowlist; provenance references where required; and the role-specific checks above.
- **Independent-review requirements:** AG-08 reviews producer outputs. AG-08 itself is validated against deterministic checks and golden evaluation cases; the runtime/founder makes any required final approval.
- **Grounding/evidence requirements:** Produce scoped websites, web changes, scripts, and bounded online automations from an approved requirements brief. Start with website/software deliverables; add other digital-production skills only when separately scoped and tested. Output must distinguish evidence-backed observations from assumptions or recommendations.
- **Known limitations:** This role cannot guarantee correctness across arbitrary tasks or inaccessible sources. Exact model, version, timeout, numeric budget, and evaluation thresholds remain to be measured and pinned before implementation.

## Observability and data
- **Required metrics:**
- Clean build pass rate
- Acceptance test pass rate
- Escaped defect/rework rate
- Build duration/resource use
- Artifact provenance completeness
- **Audit events:** invocation, capability/version, input/output references, tool requests/results, memory reads/writes, policy decisions, retries, exceptions, evaluation result, approval/escalation, and final runtime outcome. Redact sensitive content.
- **Sensitive data processed:** Source code and customer requirements may be confidential. Isolate project workspace and avoid sending secrets to model context.
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
