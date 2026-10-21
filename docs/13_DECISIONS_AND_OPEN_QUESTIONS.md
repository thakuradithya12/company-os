# 13 — Decision Log and Open Questions

This file separates the current baseline from items intentionally deferred. Do not treat a proposed choice as a completed implementation or assume a deferred decision has been made.

## 1. Recorded baseline decisions

### D-001 — Product shape
- **Decision:** Build one founder-controlled web control center backed by a shared orchestration/runtime and data system.
- **Reason:** The founder needs visibility and control across all business workflows, not a set of isolated chatbots.
**Status:** Baseline accepted as the project direction.

### D-002 — Documentation before implementation
- **Decision:** Complete and version-control the project documents before building application features.
- **Reason:** Reduces scope drift and makes acceptance criteria explicit.
**Status:** Current phase.

### D-003 — Agent classification is separate
- **Decision:** Do not fix the final number or exact role split during documentation. Perform a dedicated workforce inventory/classification phase after the documents are accepted.
- **Reason:** The founder explicitly requires classification to occur after documentation.
**Status:** Deferred to Phase 1.

### D-004 — Sequential work acceptance
- **Decision:** Do not move to the next agent/work package when the current one has pending required deliverables, failing acceptance tests, or unresolved blocking defects.
- **Reason:** Enforces the requested one-by-one development discipline.
**Status:** Baseline accepted.

### D-005 — Canonical data store
- **Decision:** PostgreSQL is the recommended canonical system of record; model context, Redis messages, and browser state are not authoritative.
- **Reason:** Durable relational records, transactions, audit history, and clear recovery behavior.
**Status:** Proposed baseline; verify operational fit during bootstrap.

### D-006 — Frontend/backend separation
- **Decision:** Next.js + TypeScript for the control UI; FastAPI for Python API/runtime integration.
- **Reason:** Clear boundary between UI and Python-oriented agent execution.
**Status:** Proposed baseline; dependency versions to be pinned during bootstrap.

### D-007 — Stateful orchestration candidate
- **Decision:** Use LangGraph as the first candidate for stateful workflows/checkpoints/human approval flows, subject to a narrow architecture verification before adoption.
- **Reason:** Long-running workflows require persisted state and controlled resumption.
**Status:** Proposed baseline; adoption must be tested against requirements.

### D-008 — Local model support
- **Decision:** Keep model inference behind a provider adapter and support local development through Ollama if model/tooling evaluation passes. Hosted providers remain optional.
- **Reason:** Reduce early API cost and avoid vendor lock-in.
**Status:** Proposed baseline.

### D-009 — Side effects default-deny
- **Decision:** Outbound calls/messages, publication, spending, binding contracts, production deployments, and destructive operations are disabled unless configured policy and required approvals permit them.
- **Reason:** Prevent unintended external impact and preserve founder control.
**Status:** Baseline accepted.

### D-010 — No perfect-output claim
- **Decision:** Require evidence, independent checks, recovery, and visible uncertainty; do not claim flawless behavior.
- **Reason:** Reliability must be measurable and honest.
**Status:** Baseline accepted.

## 2. Open questions to resolve at their designated phase

### Before repository bootstrap
- Confirm the GitHub repository owner/name and desired visibility.
- Pin compatible package versions and agree on package manager/lockfile.
- Choose concrete worker/broker configuration and deployment profile based on repeatable local tests.
- Define local developer operating system support and the canonical quick-start path.

### During agent classification
- What distinct roles are truly needed, and what should be a skill/tool versus a separate agent?
- Which roles can share a runtime/model, and which require different models or execution environments?
- Which capabilities can run in parallel and which must be sequential?
- What is the exact owner, input/output schema, memory scope, tool allowlist, and test suite for each role?
- What is the authorized autonomy and escalation path for each role?

### Before client communication is enabled
- Which CRM and communication providers are approved?
- What registrations, consent/preference checks, suppression rules, disclosures, retention, and telecom provider configuration apply to the intended campaign?
- What is the approved price/discount/negotiation authority?
- Which actions require explicit human approval or signature?

### Before public launch
- What user/account model, data retention schedule, privacy notice, terms, incident contact, and support process are required?
- Which hosting, domain, database backup, and recovery targets are affordable and measured?
- Which capacity, concurrency, latency, cost, and uptime targets will be used as service objectives?
- Which security review and independent checks are required for release?

## 3. Change proposal format

A proposed decision change must include: ID, current decision, proposed change, rationale, alternatives considered, user impact, architecture/data/security/test impact, migration or rollback plan, and founder approval. Update this record after a decision; do not erase meaningful prior history.
