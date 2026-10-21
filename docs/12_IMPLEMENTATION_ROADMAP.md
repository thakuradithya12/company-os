# 12 — Implementation Roadmap and Work Discipline

## 1. Required sequencing

Work must proceed in the order below. The agent classification phase is not to be skipped or preempted. Each phase has a written start condition, deliverables, tests, and exit decision.

### Phase 0 — Project documentation (accepted)
Deliverables: project charter, requirements, architecture, workflow contracts, data/memory model, security policy, dashboard and API requirements, integration plan, acceptance tests, operations plan, roadmap, decision log, and traceability matrix.

Exit gate: passed. Documentation is committed and pushed; founder accepted the baseline before workforce classification.

### Phase 1 — Agent inventory and classification (accepted)
The founder approved the eight-role classification in `docs/17_AGENT_CLASSIFICATION.md` on 2026-10-21. Individual role contracts are recorded in `docs/agent-specs/`. This closes classification; it does not mean any agent is implemented or enabled. Do not add or implement agent-specific behavior until the shared platform/runtime phases pass.

Deliverables: approved role inventory, capability matrix, dependency map, role contracts, and sequential build order.

Exit gate: satisfied for the initial workforce. Any role split or merge requires a documented change proposal and founder approval.

### Phase 2 — Repository bootstrap and engineering foundation (current)
Create the application monorepo structure, dependency/lock files, CI, environment validation, migration baseline, health checks, lint/type checks, and repeatable local setup. Keep the user-facing web page and API limited to the foundation status and health/readiness surfaces. Do not implement agent execution, agent prompts, business workflows, authentication, CRM, telephony, or production integrations.

Exit gate: clean locked dependency sync, backend lint/tests, frontend type check and production build, PostgreSQL migration, health endpoint behaviors, Compose configuration, and GitHub Actions checks all pass. Any check not run is still open; no agent feature is accepted in this phase.

### Phase 3 — Core platform before specialist agents
Implement authentication, authorization, canonical task schema/state machine, audit events, durable worker dispatch, retries, cancellation, checkpoints, and live task updates.

Exit gate: core reliability acceptance scenarios pass, including restart recovery and cancellation.

### Phase 4 — Agent runtime foundation
Implement the generic runtime contract, provider adapter, registered tools, validated input/output, memory interfaces, limits, and verification pipeline.

Exit gate: one approved test capability can execute a fixture task through the generic pipeline with evidence, and failure behavior is correct.

### Phase 5+ — Role-by-role workforce implementation
Implement one approved agent role at a time in the founder-approved order. For every role: confirm spec, implement minimal capability, create unit/integration/evaluation tests, run negative tests, fix blocking defects, produce evidence, commit a checkpoint, and obtain acceptance before proceeding.

**Hard rule:** If any deliverable or required test for the current role is pending, or any blocking bug remains, do not start the next role. No parallel agent development that makes ownership and integration ambiguous unless the founder explicitly changes this rule.

### Later phases — Dashboard, research, CRM/sales, delivery, and deployment
These product modules are integrated only in the sequence and scopes recorded after the core platform is stable. Voice calling, automatic external outreach, public publication, production deployment, payment, contract acceptance, and untrusted code execution each require their specific security/legal/operational gates.

## 2. Work-package template

Every work package must specify:
- unique ID and objective;
- parent phase and prerequisites;
- included/excluded scope;
- permitted files/modules and ownership;
- requirements IDs addressed;
- proposed approach and interface contract;
- tests and exact acceptance criteria;
- known risks and rollback approach;
- required evidence;
- blocking defects and dependencies;
- exit decision owner.

## 3. Definition of done

A package is done only when:
- specified files/deliverables exist in the expected locations;
- implementation matches its approved contract;
- required tests were executed and passed;
- negative/failure cases relevant to the feature were tested;
- documentation is updated;
- no unresolved blocking bug remains;
- known non-blocking limitations are documented;
- the Git checkpoint is committed and pushed to the designated repository;
- the founder explicitly accepts the package when the phase requires it.

## 4. Bug handling protocol

1. Stop moving forward on the affected work package.
2. Record reproduction steps, expected behavior, actual behavior, logs, and impact.
3. Classify severity and identify the root cause rather than masking the symptom.
4. Add a regression test before or with the fix.
5. Implement the smallest correct fix.
6. Rerun the regression test and relevant broader suite.
7. Recheck downstream contracts and security impact.
8. Commit the fix, attach evidence, and update the issue/decision log.
9. Proceed only when the exit gate is satisfied.

## 5. Git discipline

- Use a single clean monorepo for the initial implementation.
- Make small, descriptive commits that correspond to a work package or defect fix.
- Never overwrite unrelated user work or force-push without an explicit request and reviewed recovery plan.
- Do not commit secrets or production/customer data.
- Require CI/required tests before merging a pull request when CI is configured.
- Preserve checkpoint tags or release references for accepted phase boundaries.
- Documentation changes are also reviewed and traced like code changes.

## 6. Change control

A change to requirements, safety policy, architecture, agent classification, approval levels, or release sequence requires a written change proposal with rationale, impact, affected docs/tests, and founder approval. Update the decision log and traceability matrix before implementation.
