# 14 — Requirements Traceability Matrix

This matrix links core requirements to the documentation and future validation. Exact test module paths are assigned during implementation planning and are not invented at this stage.

| Requirement group | IDs | Specification | Planned verification |
|---|---|---|---|
| Objective intake and orchestration | FR-001–FR-010 | `01_PRODUCT_REQUIREMENTS.md`, `03_WORKFLOWS_AND_STATE_MACHINES.md` | Objective persistence, planning fixture, state-machine and recovery tests |
| Dashboard visibility and controls | FR-011–FR-016 | `07_CONTROL_CENTER_UX.md`, `08_API_CONTRACTS.md` | UI/API end-to-end control tests; stale-data/reconnect tests |
| Research and niche intelligence | FR-017–FR-022 | `01_PRODUCT_REQUIREMENTS.md`, `04_DATA_MODEL_AND_MEMORY.md`, `09_EXTERNAL_INTEGRATIONS.md` | Provenance, freshness, deduplication, source-conflict and publication-gate tests |
| Business discovery and CRM | FR-023–FR-027 | `01_PRODUCT_REQUIREMENTS.md`, `04_DATA_MODEL_AND_MEMORY.md`, `09_EXTERNAL_INTEGRATIONS.md` | Prospect evidence, eligibility, duplicate suppression, communication history tests |
| Deals and authority limits | FR-028–FR-031 | `05_SECURITY_PRIVACY_AND_GOVERNANCE.md`, `09_EXTERNAL_INTEGRATIONS.md` | Boundary/approval version tests; calling disabled until its release gate passes |
| Production and delivery | FR-032–FR-036 | `01_PRODUCT_REQUIREMENTS.md`, `02_SYSTEM_ARCHITECTURE.md`, `09_EXTERNAL_INTEGRATIONS.md` | Isolated build, test, preview, artifact provenance and deployment approval tests |
| Memory and knowledge | FR-037–FR-038 | `04_DATA_MODEL_AND_MEMORY.md`, `06_AGENT_RUNTIME_CONTRACT.md` | Scope isolation, provenance, expiry/correction and retrieval tests |
| Security and audit | FR-039–FR-041 | `05_SECURITY_PRIVACY_AND_GOVERNANCE.md` | AuthZ, secret-leak, prompt injection, SSRF, tool permission, audit tests |
| Operations and recovery | FR-042 | `11_OPERATIONS_DEPLOYMENT_AND_RECOVERY.md` | Health, restart recovery, restore drill, alerts, emergency-stop tests |


## Workforce classification traceability (Phase 1)

| Classification concern | Specification | Planned verification / acceptance |
|---|---|---|
| Role count, boundaries, skill-vs-agent decisions | `17_AGENT_CLASSIFICATION.md`, `agent-specs/` | AC-CL-01, AC-CL-06, founder review record |
| Role input/output/dependency and memory contracts | Each `docs/agent-specs/AG-*.md`, `06_AGENT_RUNTIME_CONTRACT.md` | Role schema contract tests and memory-scope tests before each role is enabled |
| External authority separation | `17_AGENT_CLASSIFICATION.md`, `05_SECURITY_PRIVACY_AND_GOVERNANCE.md` | AC-CL-02, AC-CL-04; negative tool-permission and opt-out tests |
| Producer/verifier separation | AG-08 specification; `10_TESTING_AND_ACCEPTANCE.md` | AC-CL-05; failed criterion cannot pass through model narrative alone |
| Sequential role implementation | `12_IMPLEMENTATION_ROADMAP.md` | One role-specific release gate and Git checkpoint at a time |

Phase 1 classification is accepted: the founder approved the eight-role inventory on 2026-10-21. The roles remain unimplemented; platform/runtime gates and per-role acceptance tests still apply.

## Phase 1 classification acceptance

- [x] Eight logical role boundaries approved by the founder on 2026-10-21.
- [x] Per-role specifications are present and use the shared runtime contract.
- [x] Deterministic platform services are not misclassified as independent agents.
- [x] External authority and sequential build gates are explicit.

## Phase 2 bootstrap acceptance

| Check ID | Required evidence | Current state |
|---|---|---|
| BOOT-001 | Root monorepo structure and Python/frontend dependency manifests exist | Implemented locally; locks still pending |
| BOOT-002 | `uv.lock` is generated and `uv lock --check` passes | Pending developer package-registry access |
| BOOT-003 | `apps/web/package-lock.json` is generated and `npm ci` passes on Node 24 | Pending developer package-registry access and Node 24 verification |
| BOOT-004 | Environment validation does not print secrets | Implemented; covered by configuration behavior and review |
| BOOT-005 | API liveness works without a database; readiness returns 503 without a configured DB | Backend tests passed locally |
| BOOT-006 | API readiness succeeds when a test database answers `SELECT 1` | Backend tests passed locally with SQLite test connection |
| BOOT-007 | PostgreSQL Alembic baseline executes in CI/local Docker environment | Pending PostgreSQL service execution |
| BOOT-008 | Ruff, Pytest, TypeScript check, and Next production build pass | Pytest passed locally; remaining locked checks pending |
| BOOT-009 | Compose configuration parses and full stack starts | YAML syntax parsed; Docker unavailable in authoring environment, full compose run pending |
| BOOT-010 | GitHub Actions workflow runs the locked verification sequence | Workflow authored; CI run pending push |
| BOOT-011 | No agent behavior or business-facing side-effect functionality is added during Phase 2 | In scope review: foundation only |

Phase 2 is not accepted until all required checks above are completed and their evidence is attached to the Git checkpoint. A pending check is not a pass.

## Phase 0 documentation acceptance

- [x] Project vision, goals, scope boundaries, and non-goals are documented.
- [x] Functional and non-functional requirements are uniquely identified.
- [x] Proposed architecture and component boundaries are documented.
- [x] Task state machine, retries, cancellation, recovery, and completion rules are documented.
- [x] Conceptual data model and memory policy are documented.
- [x] Security, privacy, permissions, tool execution, and approval gates are documented.
- [x] Agent runtime contract exists without fixing agent count/roles.
- [x] Dashboard, API, integration, testing, and operational requirements are documented.
- [x] Sequential build/break-fix workflow is documented.
- [x] Open decisions and risk constraints are recorded.
- [x] Cross-document links and internal consistency have been checked.
- [x] Documentation is committed and pushed to the designated GitHub repository.
- [x] Founder accepts the baseline before Phase 1.

## Related operating references

- [Company operating model](15_COMPANY_OPERATING_MODEL.md)
- [Glossary](16_GLOSSARY.md)
