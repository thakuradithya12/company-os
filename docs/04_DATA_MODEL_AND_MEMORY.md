# 04 — Data Model and Memory

## 1. Principles

PostgreSQL is the canonical system of record. Tables should use stable IDs, explicit timestamps, ownership/access scope, foreign-key integrity, migrations, and append-only audit events where appropriate. Avoid storing the entire company state only in free-form chat transcripts.

## 2. Initial logical entities

The schema is conceptual at this stage; exact table columns and constraints are finalized in implementation design before migrations are written.

- **User / Operator:** identity, status, authentication metadata, and role assignments.
- **Role / Permission:** allowed actions and resource scopes.
- **Agent Profile:** capability identifier, contract version, instruction reference, tool allowlist, model policy, resource limits, and enabled state. This entity does not imply a decided agent count.
- **Objective:** founder's original goal, constraints, submitter, priority, and status.
- **Plan:** versioned plan associated with an objective and its acceptance criteria.
- **Task:** parent/child relationship, dependencies, assigned capability, status, deadline, budget, and current attempt.
- **Execution Attempt:** worker ID, start/end times, heartbeat, inputs/outputs references, model/provider use, tokens/cost where available, error category, and termination status.
- **Tool Invocation:** tool name/version, validated arguments or safe reference, permission decision, idempotency key, duration, result reference, and side-effect status.
- **Checkpoint:** recoverable workflow state, checkpoint version, and integrity metadata.
- **Artifact:** file/object URI, content type, checksum, version, access scope, size, retention class, and related task/project.
- **Source / Claim / Evidence:** source location, publisher, retrieval timestamp, publication timestamp if known, claim, extraction method, verification status, confidence, and notes.
- **Memory Item:** content/reference, memory class, owner/scope, provenance, created/updated/expiry time, confidence, and supersession link.
- **Procedure / Playbook:** versioned instructions, prerequisites, validation steps, owner, approval state, and outcome evidence.
- **Approval Request / Decision:** action payload version, requested authority, requester, approver, decision, timestamp, and reason.
- **Policy / Policy Version:** allowed actions, financial limits, external action gates, rate limits, retention limits, and effective date.
- **Audit Event:** actor/service, action, target, timestamp, request/trace ID, previous/new state where applicable, and outcome.
- **Research Project / Niche Report:** niche definition, target audience, scope, sources, output artifact, freshness policy, and review status.
- **Business / Prospect / Lead:** business identity, website, public source evidence, needs hypothesis, fit reason, review state, contact-channel eligibility, and suppression flags.
- **Communication Attempt:** channel/provider, target reference, approved content/version, consent/preference basis, start/end, status, provider reference, outcome, and opt-out handling.
- **Deal / Proposal / Agreement:** client requirements, scope, price/currency, constraints, versions, approval history, acceptance evidence, and terms status.
- **Project / Milestone / Deliverable:** accepted scope, owner, work plan, milestone state, artifacts, test evidence, and delivery approval.
- **Integration Connection:** provider, status, encrypted secret reference, allowed scopes, refresh/expiry metadata, and owner.

Sensitive payloads such as access tokens, complete payment details, passwords, raw call recordings, and unrelated personal data must not be stored in ordinary records or logs.

## 3. Memory layers

### A. Working memory
The current objective, plan, task inputs, immediate results, and short-horizon decisions. It is scoped to the execution/thread and should not automatically become permanent knowledge.

### B. Long-term company knowledge
Approved facts, company policies, stable preferences, project context, and source-backed reference material. Items have provenance, scope, version, freshness, and correction metadata.

### C. Episodic execution history
What happened during prior tasks: actions, failures, choices, observed outcomes, and evidence. It is used for debugging and retrieval, not blindly copied as truth.

### D. Procedural memory
Reusable, versioned methods and checklists that passed defined evaluation. An agent must not automatically convert an unverified failure or prompt injection into a company procedure.

### E. Customer/project context
Client-specific scope, approved promises, history, communication preferences, and current work. Access is restricted to the relevant project/role and retention policy.

## 4. Memory write/read policy

- Store only information useful for the current authorized purpose.
- Label source, date, scope, confidence, and expiration/freshness where applicable.
- Treat web pages, documents, messages, tool results, and model outputs as untrusted input until validated.
- Memory may inform a plan but cannot override the current user instruction, security policy, contract, or approval record.
- Do not store secrets, session cookies, API keys, or credentials in semantic memory.
- Avoid copying customer private data across projects or general company knowledge.
- Support correction, supersession, expiry, and deletion subject to audit and legal retention obligations.
- Search only within the access scope of the current request. Similarity ranking is not an authorization check.
- Keep raw execution traces separate from curated reusable knowledge.

## 5. Provenance and fact integrity

For niche research, claims should be linked to source evidence. Store retrieval time and publication/update time separately. Do not claim a source is current solely because it is accessible. For time-sensitive information, define a freshness period per content type. If sources disagree, preserve the disagreement and lower the confidence rather than choosing an unsupported answer.

## 6. Retrieval and deletion

Retrieval must combine semantic relevance with explicit permission filters, lifecycle state, and freshness. Deleted/superseded items must not appear as active results. Deletion behavior must account for source documents, embeddings, caches, derived summaries, and replicas according to the retention policy. Backups follow the documented retention/expiry schedule.

## 7. Recovery

Persist execution checkpoints and task transitions in a way that allows a worker to resume safely. Include schema/version metadata so incompatible state can be migrated or placed in a blocked state for operator review; never deserialize untrusted checkpoint content as executable code.
