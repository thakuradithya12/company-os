# 01 — Product Requirements

## 1. Product summary

Company OS is a web control plane for a founder-directed AI workforce. It combines a conversational interface with durable tasks, specialist capabilities, persistent memory, client and project records, external tools, verification, and operator controls.

## 2. Primary user stories

- As the founder, I can describe a company goal or niche once and see the plan, scope, status, and dependencies created from it.
- As the founder, I can see what each running agent is doing, which tools it used, what remains, and why a task is blocked.
- As the founder, I can stop, pause, retry, reprioritize, or cancel work and see confirmation of the actual backend state.
- As the founder, I can set global policy, task limits, permitted tools, approval requirements, and spending ceilings.
- As the founder, I can inspect the sources behind research claims and identify uncertainty or stale information.
- As the founder, I can maintain niche reports, opportunity records, leads, conversations, proposals, deals, projects, and deliverables in one place.
- As the founder, I can see a proposed external action before it is executed whenever policy requires approval.
- As the founder, I can receive a final result that explains what was completed, what failed, how it was verified, and what still needs attention.
- As a future external user, I can access only public resources or the account-specific data I am authorized to see.

## 3. Product modules

1. **Command interface:** Natural-language request intake, clarification when a material requirement is missing, task creation, and final reporting.
2. **Work orchestration:** Plans, tasks, dependencies, queues, task state, cancellation, retries, checkpoints, and recovery.
3. **Workforce registry:** A catalog of approved roles/capabilities, instructions, tools, access scopes, model settings, and status. The proposed initial classification is in `17_AGENT_CLASSIFICATION.md` and remains pending founder approval.
4. **Memory and knowledge:** Short-term execution state, long-term company knowledge, reusable procedures, customer context, decision history, and evidence provenance.
5. **Research and niche intelligence:** Source collection, normalization, deduplication, relevance ranking, verification, summary writing, and controlled distribution.
6. **Opportunity and CRM:** Public-business research, prospect qualification, website audit findings, lead history, communication preferences, and follow-up eligibility.
7. **Sales and deals:** Conversation preparation, approved outreach, needs capture, proposal drafts, policy-bounded negotiation, approvals, and signed/accepted terms recorded as evidence.
8. **Production and delivery:** Project requirements, task breakdown, code/content production, isolated workspaces, testing, previews, release approval, and delivery records.
9. **Quality and governance:** Independent verification, permission checks, safety checks, human approvals, audit history, policy configuration, and incident reporting.
10. **Operations:** Service health, queue depth, failures, model/provider health, backup state, logs, metrics, and restoration actions.

## 4. Functional requirements

IDs are stable references used by the traceability matrix.

### Request and orchestration
- **FR-001:** Accept a founder objective through the dashboard chat or structured task form.
- **FR-002:** Persist the original request and its attachments/references before execution begins.
- **FR-003:** Convert the request into an explicit plan, task list, dependencies, expected outputs, and acceptance criteria.
- **FR-004:** Ask for founder clarification or approval when a missing decision materially changes scope, cost, risk, or external impact.
- **FR-005:** Assign subtasks only to registered capabilities authorized for the task.
- **FR-006:** Track each task's owner/capability, state, timestamps, inputs, output references, attempts, errors, and verification outcome.
- **FR-007:** Support pause, resume, cancel, retry, reprioritize, and bounded replan operations.
- **FR-008:** Recover interrupted work from persisted state without falsely duplicating irreversible side effects.
- **FR-009:** Enforce deadlines, iteration limits, concurrency limits, and resource budgets.
- **FR-010:** Never mark a task completed solely because the model emitted a completion statement.

### Dashboard and control
- **FR-011:** Show current and recent work, task states, active capabilities, alerts, and blocker counts from live backend data.
- **FR-012:** Provide detailed task inspection, source/evidence links, execution history, and error diagnostics.
- **FR-013:** Make pause, cancel, retry, approve, reject, and edit-policy controls perform the corresponding authorized backend action.
- **FR-014:** Show pending approvals with the exact action, target, content/terms, risk, and evidence needed to decide.
- **FR-015:** Record the authenticated actor and result of every privileged control action.
- **FR-016:** Clearly distinguish mocked/demo data from live system data; production must not show mock results as real telemetry.

### Research and information services
- **FR-017:** Accept a niche, audience, geography, output format, freshness requirement, and delivery destination as research parameters.
- **FR-018:** Preserve source URL or source identifier, retrieval time, published/updated time when available, extracted claim, and confidence/verification state.
- **FR-019:** Deduplicate sources and findings while retaining a traceable link to originals.
- **FR-020:** Distinguish fact, inference, opinion, estimate, and unsupported claim.
- **FR-021:** Prepare audience-appropriate resources, reports, summaries, and recommendations under an explicit content brief.
- **FR-022:** Require review or policy approval before external publication where configured.

### Opportunity, CRM, and sales
- **FR-023:** Store a business opportunity with source, evidence, fit rationale, discovered issue, potential service, last-checked time, and review state.
- **FR-024:** Avoid collecting irrelevant personal information; prefer public business contact channels and record the lawful/policy basis for contact.
- **FR-025:** Maintain suppression/opt-out data and prevent disallowed follow-up.
- **FR-026:** Generate personalized outreach drafts grounded in verified business findings.
- **FR-027:** Store communication attempts, outcomes, commitments, and requested follow-up time with audit history.
- **FR-028:** Provide configurable limits for pricing, discounts, project scope, promises, and contract language.
- **FR-029:** Require approval when a proposed deal exceeds any configured authority boundary.
- **FR-030:** Do not treat a verbal summary as proof of a signed contract, payment, or accepted terms.
- **FR-031:** Keep automated outbound calling and messaging disabled until regulatory, provider, consent, preference, and suppression gates pass.

### Production and delivery
- **FR-032:** Convert accepted project terms into a versioned requirements brief and delivery checklist.
- **FR-033:** Keep untrusted inputs, generated code, and build/test execution in bounded workspaces with least privilege.
- **FR-034:** Record repository commit, artifact version, build/test output, and preview reference for generated software deliverables.
- **FR-035:** Separate internal preview from public production deployment.
- **FR-036:** Require founder or explicitly delegated approval before production deployment and final client delivery, where configured.

### Memory, identity, security, and operations
- **FR-037:** Store execution checkpoints separately from long-term knowledge and ensure both can be scoped and retrieved safely.
- **FR-038:** Preserve source/provenance, timestamps, access scope, confidence, and correction history for stored knowledge.
- **FR-039:** Enforce authentication, authorization, user/session limits, and least-privilege tool access.
- **FR-040:** Protect secrets from prompts, logs, outputs, memory, and Git.
- **FR-041:** Audit privileged actions, external side effects, approvals, failures, policy changes, and data access where appropriate.
- **FR-042:** Provide health endpoints, metrics, structured logs, alertable failures, backups, and restoration procedures.

## 5. Non-functional requirements

- **Reliability:** Persistent task records; idempotent handling of repeated requests; bounded retries; crash recovery; reconciliation of queue and database state.
- **Observability:** Correlated request, task, execution, tool, and approval identifiers; timestamps; structured error categories; no sensitive payload leakage.
- **Security:** Secure sessions; least privilege; secret management; input/output validation; isolated execution; rate limits; audit logs.
- **Performance:** Dashboard status changes should be near-real-time for the initial expected workload. Define concrete latency and throughput targets before deployment load tests.
- **Maintainability:** Modular components, typed interfaces, migrations, documented setup, repeatable checks, small changes, and stable requirement IDs.
- **Portability:** Local development must not assume cloud-only services. Deployment-specific details belong in environment configuration.
- **Cost control:** Configurable model calls, retries, context budgets, parallelism, crawling limits, and provider usage limits.
- **Accessibility and usability:** Keyboard-operable controls, readable status labels, clear empty/error states, and no misleading success messages.
- **Factuality:** Research outputs cite their sources; time-sensitive items show retrieval times; uncertain claims remain marked uncertain.
- **Recoverability:** A restore test—not merely a backup configuration—is required before production.

## 6. Explicitly not guaranteed

- Perfect accuracy on all tasks.
- Full autonomy across every possible online activity.
- Free, always-on public hosting or free telephony.
- Access to every third-party service without API keys, permissions, subscriptions, or terms approval.
- The ability to place commercial calls from a personal mobile number.

## 7. Release posture

Until requirements and architecture are approved and their tests are implemented, the product remains private and non-production. Public user accounts, automatic client outreach, real payment collection, binding contract acceptance, and public code deployment are disabled by default.
