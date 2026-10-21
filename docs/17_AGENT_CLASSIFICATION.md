# 17 — Approved Agent Workforce Classification

> **Status: APPROVED CLASSIFICATION — founder approved on 2026-10-21.** The eight logical roles and their top-level responsibility boundaries are approved. This approval does not mean any role is implemented or enabled. Agent implementation remains blocked until the shared engineering foundation and each role-specific release gate pass.

## 1. Decision summary

**Approved initial workforce: 8 logical agent roles, implemented on one shared runtime.** The roles are not eight separate applications, databases, or always-running model servers. They are registered role configurations with distinct responsibilities, I/O contracts, permissions, memory scopes, and evaluations. The execution platform may create bounded task-specific instances as needed.

This is a practical starting structure for the scope currently documented: founder command chat, planning and delegation, niche research, business opportunity discovery, content/resource production, client acquisition and deal support, digital deliverable production, and independent verification.

The count is deliberately smaller than an org chart of 17–20 job titles. Many apparent employees are better implemented as deterministic platform services, integrations, or reusable skills. Extra permanent roles should be introduced only when testing shows a distinct responsibility boundary that cannot be handled safely as a skill under an existing role.

## 2. Classification principles

1. **One accountable responsibility per role.** Each role has a clear purpose, owned outputs, and boundaries.
2. **Agent versus service.** Use an AI role where interpretation, synthesis, or context-sensitive reasoning is needed. Use deterministic code for permissions, task state, budgets, approvals, retries, billing records, and audit events.
3. **Skill before new agent.** Add a reusable skill/tool package to an existing role unless the new capability needs a distinct lifecycle, security scope, memory policy, evaluation suite, and accountable output.
4. **Shared runtime.** All roles use the same registered execution contract and tool gateway. Separate prompts/configurations do not imply separate infrastructure.
5. **Independent verification.** Producers cannot self-certify their own acceptance result. The quality reviewer is a separate role; deterministic tests remain mandatory too.
6. **Side effects default-deny.** Actual external calls/messages, public publication, contractual commitments, money movement, and production deployment remain behind server-side policy and required approvals.
7. **Finite execution.** Every run requires explicit limits for time, steps, model calls, output size, tools, and cost where measurable. Missing limits never mean unlimited authority.
8. **Evidence and uncertainty.** Research claims and completed actions need traceable evidence. Unknown outcomes remain unknown until reconciled.
9. **Sequential implementation.** After the founder approves this proposal, implement one role at a time in the approved order. A blocking defect or unmet acceptance criterion stops advancement.

## 3. Approved workforce inventory

| ID | Approved role | Primary responsibility | Separate role because | Default external authority |
|---|---|---|---|---|
| AG-01 | Founder Command & Intake Agent | Conversational interface to clarify the founder's intent and form a structured objective | Needs a stable conversational contract but must not have execution authority | None; reads status and creates a draft/approved work request through the API |
| AG-02 | Planning & Orchestration Agent | Propose a plan, task breakdown, dependencies, and capability assignments | Planning is cross-company and must remain separate from any one producer | None directly; deterministic orchestration validates and executes the approved plan |
| AG-03 | Research & Evidence Agent | Research a niche, collect sources, compare claims, and return evidence-backed findings | Research has source provenance, freshness, and citation-quality requirements | Read-only approved sources by default |
| AG-04 | Business Discovery & Website Audit Agent | Find relevant businesses and document evidence-backed digital presence or website opportunities | Prospect qualification is different from general topic research and must not initiate contact | Read-only permitted public business information; no contact actions |
| AG-05 | Content & Information Product Agent | Turn reviewed research into audience-specific reports, guides, resource pages, and content drafts | Owns transformation and editorial quality, not independent fact creation or publication authority | Internal draft creation only; publishing through a gated integration |
| AG-06 | Client Acquisition & Deal Agent | Prepare and conduct approved prospect/client conversations, capture needs, draft proposals, and negotiate within limits | Customer interaction and commercial commitments require a distinct communication and authority boundary | Draft-only until communication gates pass; no binding agreement or spending authority by default |
| AG-07 | Digital Solution Builder Agent | Produce software and digital deliverables such as websites and bounded automations | Needs a controlled code/artifact workspace and build/test toolchain | Internal isolated workspace only; no direct production deploy or unbounded host access |
| AG-08 | Independent Quality & Acceptance Agent | Review outputs against criteria, evidence, tests, and scope; return pass/rework/block | Must not share the producer's acceptance authority; review is a separate control | Read-only access to task brief, evidence, artifacts, and test results; cannot approve its own findings |

### Count interpretation

Eight is the proposed **logical role count**, not a target for eight concurrent LLM processes. One model may serve multiple roles through different runtime configurations when evaluation supports it. Concurrent execution is determined by dependencies, available hardware/provider limits, and policy—not by the role count.

## 4. What is deliberately not a separate agent

These functions are required, but should initially be deterministic platform services or skills rather than permanent AI workers:

| Function | Initial implementation form | Reason |
|---|---|---|
| Task queue, scheduler, retry, timeout, cancellation, checkpoint and recovery | Durable execution service | Must provide predictable state transitions and recovery; a model cannot be the source of truth |
| Authorization, approval gates, budgets and emergency stop | Policy/permissions service | Security decisions must be enforced by code outside model-generated text |
| Company memory and retrieval | Database-backed memory/knowledge service | Storage, scoping, provenance, retention and deletion require deterministic rules |
| Dashboard, monitoring, alerts and audit | Web UI plus telemetry/audit services | Must display persisted facts rather than rely on an agent's narrative |
| CRM records, opt-out suppression and contact eligibility | Database and server-side policy | Outreach eligibility must be checked at the final action boundary |
| Email, browser research, telephony and publication | Typed integration adapters | Providers execute actions; role agents only request authorized operations |
| Project handover and post-delivery checklist | Workflow plus templates; later may gain a support skill | Most steps are state transitions, notifications, and evidence collection |
| Finance, HR, SEO, design, cybersecurity, legal research, social media and other niche expertise | On-demand skills/capability packs, initially | These are domains or service types, not automatically separate always-on agents. Higher-risk domains require extra qualification and review. |
| Website deployment and client delivery | Gated workflow/tool integration | Deployment requires approval, access controls, test evidence and rollback—not another chat persona |

A future role may be split out only with a written change proposal explaining why a new accountability/security/evaluation boundary is necessary and how cost and complexity are justified.

## 5. Capability coverage matrix

| Business workflow | Primary role(s) | Required non-agent support | Gated action |
|---|---|---|---|
| Founder describes a goal or niche | AG-01, then AG-02 | Request schema, task API, persistent task state | Approval for material scope/cost/risk changes |
| Niche intelligence report | AG-03 → AG-05 → AG-08 | Approved research connectors, source store, tests, publishing preview | External publication |
| Business prospect discovery | AG-03 as needed → AG-04 | Public-source allowlist, deduplication, CRM and eligibility rules | Contact is not initiated by discovery |
| Website opportunity assessment | AG-04 → AG-08 | Safe HTTP inspection, audit rubric, source evidence | No production changes to prospect's site |
| Outreach and client discussion | AG-06 | CRM, approved messaging/telephony provider, suppression and policy service | Each channel must pass regulatory/provider gates; initial calls/messages remain disabled |
| Proposal and deal tracking | AG-06 → AG-08 where useful | Versioned proposal store, pricing/authority policy, approval records | Binding terms/contract acceptance require founder approval in the initial release |
| Website/software delivery | AG-02 → AG-07 → AG-08 | Isolated workspace, repository/artifact store, deterministic build/test pipeline | Production deployment and final handover according to configured approval policy |
| Dashboard and control | AG-01 for explanatory chat; no role owns truth | API, RBAC, telemetry, event/audit store | Every control is server-authorized and auditable |

## 6. Data flow and handoffs

```text
Founder
  -> AG-01 Command & Intake (clarify / structure objective)
  -> AG-02 Planning & Orchestration (propose task graph)
  -> deterministic policy + task engine validates/persists/dispatches
  -> selected producer role (AG-03 / AG-04 / AG-05 / AG-06 / AG-07)
  -> AG-08 Independent Quality & Acceptance
       -> pass: continue to configured approval/delivery workflow
       -> rework: return to the responsible producer with evidence
       -> blocked: request founder decision or required access
  -> deterministic delivery/approval workflow
  -> founder sees outcome, evidence, remaining limitations, and audit trail
```

This is a logical flow, not a commitment to run every step for every task. The planner selects only the capabilities needed by an objective. The deterministic task engine owns the authoritative state machine, dependency resolution and cancellation.

## 7. Approved role dependency and build order

**Prerequisite before any role:** repository bootstrap, CI, authentication/authorization, PostgreSQL schema, task state machine, audit events, durable worker, recovery/cancellation, model adapter, tool gateway, memory interfaces, and generic verification pipeline must pass their roadmap gates. These platform work packages are not additional agents.

After the platform is stable, the proposed sequential order is:

1. **AG-02 Planning & Orchestration Agent** — needed to route work among registered capabilities; deterministic orchestration service remains authoritative.
2. **AG-01 Founder Command & Intake Agent** — makes the founder-facing chat produce structured requests and explain status safely.
3. **AG-08 Independent Quality & Acceptance Agent** — gives later producer roles a consistent review protocol; deterministic checks already run from the outset.
4. **AG-03 Research & Evidence Agent** — establishes grounded source collection and niche reporting input.
5. **AG-04 Business Discovery & Website Audit Agent** — depends on research/source and CRM records; must not contact prospects.
6. **AG-05 Content & Information Product Agent** — transforms verified research into reviewed material.
7. **AG-07 Digital Solution Builder Agent** — builds website/digital deliverables in an isolated workspace.
8. **AG-06 Client Acquisition & Deal Agent** — last because external communication, telephony, pricing, terms, opt-outs, and provider/compliance gates are higher risk; it is initially draft-only and live outreach remains disabled until those gates are explicitly passed.

This order is proposed for founder approval. Dependencies may be adjusted only through a documented change, not silently during implementation.

## 8. Standard contract for all roles

Every role conforms to `docs/06_AGENT_RUNTIME_CONTRACT.md` and the template in `docs/templates/AGENT_ROLE_SPEC_TEMPLATE.md`. Each role must have:

- versioned input/output schemas and typed statuses;
- explicit tools, data scopes, read/write authority, prohibitions, and escalation conditions;
- bounded runtime and resource budgets set before implementation;
- clear allowed memory sources and memory write/promote behavior;
- positive, negative, adversarial, regression and failure evaluations;
- deterministic checks plus independent review where needed;
- metrics, audit events, data handling and retention policy;
- a role-specific completion gate and reproducible evidence.

A role result of `success` does not imply acceptance. The execution system may mark an objective complete only after required acceptance checks, approvals, and deliverables are recorded.

## 9. Acceptance tests for the classification itself

- **AC-CL-01:** Every in-scope responsibility is assigned to one accountable role or an explicitly named deterministic service.
- **AC-CL-02:** No role has permission to bypass the policy service, task state machine, approval gates, or audit pipeline.
- **AC-CL-03:** Every proposed role has a specification file with inputs, outputs, dependencies, allowed/prohibited actions, memory, limits, tests, metrics and escalation.
- **AC-CL-04:** Outreach/discovery separation is enforced: AG-04 discovers and qualifies; only AG-06 can request communication through the gated adapter.
- **AC-CL-05:** Production artifacts require AG-08 review plus deterministic tests; production deployment remains separately authorized.
- **AC-CL-06:** Roles share a runtime/contract; there is no separate app/database/model server required solely because a role exists.
- **AC-CL-07:** The founder explicitly approves or requests changes to the role count, boundaries, permissions and build order.

## 10. Risks and tradeoffs

- **Risk — roles overlap:** Control with explicit input/output ownership and handoff schemas; review duplication before implementation.
- **Risk — one general builder becomes too broad:** Start with website/software deliverables and define new skill packs with narrow evaluations. Do not claim every possible digital task is supported by default.
- **Risk — independent review is not genuinely independent:** Separate role instructions, context and tool permissions; prefer deterministic tests or a different evaluation path where feasible, and record same-model limitations.
- **Risk — sales autonomy harms real people or business reputation:** Disable live outreach by default; enforce eligibility/opt-outs server-side; keep binding terms, exceptional discounts and contracts under founder approval.
- **Risk — local resource limits:** Use bounded concurrency and queued work; measure latency/resource use before increasing concurrency. Do not spin up one model server per role.
- **Risk — memories contaminate customers/projects:** Scope retrieval by tenant/task, record provenance, and block unrelated client data from the current context.

## 11. Approval record

- [ ] Founder accepts the proposed initial count of 8 logical roles.
- [ ] Founder accepts the responsibility boundaries and deterministic-service split.
- [ ] Founder accepts or revises the proposed build order.
- [ ] Founder accepts the default-deny and draft-only communication posture.
- [ ] Each role specification is approved for use as the build contract.

**Until these boxes are reviewed and acceptance is explicitly recorded, this inventory is a proposal, not implementation authorization.**
