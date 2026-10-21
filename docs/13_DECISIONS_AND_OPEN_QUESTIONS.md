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
**Status:** Accepted; the documentation baseline was published before workforce classification.

### D-003 — Agent classification is separate
- **Decision:** Do not fix the final number or exact role split during documentation. Perform a dedicated workforce inventory/classification phase after the documents are accepted.
- **Reason:** The founder explicitly requires classification to occur after documentation.
**Status:** Sequencing rule fulfilled. The eight-role classification was approved by the founder on 2026-10-21; implementation remains gated.

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


### D-011 — Initial workforce classification (founder approved 2026-10-21)
- **Proposal:** Start with eight logical roles: Founder Command & Intake; Planning & Orchestration; Research & Evidence; Business Discovery & Website Audit; Content & Information Product; Client Acquisition & Deal; Digital Solution Builder; Independent Quality & Acceptance.
- **Why eight:** These cover the distinct initial business workflows while keeping scheduling, policy enforcement, memory, CRM storage, telephony, monitoring, publishing, and delivery checklists as deterministic services/integrations rather than extra AI roles. Niche expertise should begin as reviewed skill packs where possible.
- **Tradeoff:** A role count above eight may be justified later by evidence of distinct permission, lifecycle, data scope, or evaluation requirements. A smaller count may be chosen if the founder wants to merge boundaries after review.
- **Safety constraints:** All roles use one runtime contract; external side effects are default-deny; calling/deal authority stays gated; AG-08 does not replace deterministic tests; implementation remains one role at a time after platform prerequisites pass.
- **Reference:** `docs/17_AGENT_CLASSIFICATION.md` and `docs/agent-specs/`.
- **Status:** Approved classification baseline. Individual role implementation remains gated by platform readiness and its own accepted work package.


### D-012 — Phase 2 engineering foundation scope
- **Decision:** Establish the monorepo, lockfile generation, configuration validation, minimal health/readiness API, migration scaffold, minimal web shell, CI, and repeatable PowerShell setup before any agent implementation.
- **Reason:** The founder requires sequential work, an auditable baseline, and no agent development before platform prerequisites are verified.
- **Constraints:** Domain migrations remain intentionally empty in this phase; the web shell must not display fabricated live agent metrics; production side effects remain disabled.
- **Status:** Approved scope for Phase 2.

### D-013 — Runtime baseline versions
- **Decision:** Target Python 3.13.16, Node.js 24 LTS, Next.js 16.4.2, and React/React DOM 19.3.1 for the bootstrap baseline. Pin uv 0.13.4 or newer as the bootstrap tool; 0.13.4 includes an update to bundled root certificates released on 2026-10-20. Python dependencies use a checked-in `uv.lock`; frontend dependencies use a checked-in `apps/web/package-lock.json` generated with Node 24/npm.
- **Reason:** Target a supported Python minor and active Node LTS while using stable framework releases rather than canary packages. Transitive versions are resolved once and then locked by the package managers.
- **Status:** Proposed implementation baseline; Phase 2 remains blocked until lockfiles are generated and all checks pass on a networked developer machine/CI.

## 2. Open questions to resolve at their designated phase

### During repository bootstrap (Phase 2)
- Generate and commit platform-specific transitive dependency lockfiles on a networked developer machine or trusted CI runner.
- Verify Python/Node/Docker tool versions and the canonical Windows PowerShell quick-start.
- Verify clean dependency sync, frontend production build, backend tests/lint, migration execution against PostgreSQL, and health endpoints.
- Decide whether Compose is a required local path or an optional convenience after testing it on the founder workstation.

### During agent implementation (after platform/runtime gates)
- Which approved roles can share a runtime/model, and which require separate inference or execution environments based on evaluation?
- What exact schema, memory scope, tool allowlist, and autonomy limits need further precision in each role contract before its work package begins?
- What is the measured concurrency budget for the target hardware/provider?

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
