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

## Phase 0 documentation acceptance

- [ ] Project vision, goals, scope boundaries, and non-goals are documented.
- [ ] Functional and non-functional requirements are uniquely identified.
- [ ] Proposed architecture and component boundaries are documented.
- [ ] Task state machine, retries, cancellation, recovery, and completion rules are documented.
- [ ] Conceptual data model and memory policy are documented.
- [ ] Security, privacy, permissions, tool execution, and approval gates are documented.
- [ ] Agent runtime contract exists without fixing agent count/roles.
- [ ] Dashboard, API, integration, testing, and operational requirements are documented.
- [ ] Sequential build/break-fix workflow is documented.
- [ ] Open decisions and risk constraints are recorded.
- [ ] Cross-document links and internal consistency have been checked.
- [ ] Documentation is committed and pushed to the designated GitHub repository.
- [ ] Founder accepts the baseline before Phase 1.

## Related operating references

- [Company operating model](15_COMPANY_OPERATING_MODEL.md)
- [Glossary](16_GLOSSARY.md)
