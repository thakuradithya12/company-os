# 00 — Project Charter

## 1. Purpose

Create a founder-controlled, web-accessible operating system for a digital company whose routine work is carried out by coordinated AI agents under explicit instructions, permissions, and quality gates.

The product must let the founder issue an objective in natural language and then observe and control how the system plans, delegates, executes, verifies, and delivers the resulting work.

## 2. Vision

A small, extensible digital company that can be directed by one person and use an AI workforce to perform multiple kinds of online work. The company may research niches and distribute useful information, identify businesses that may benefit from better websites or digital services, qualify opportunities, manage client conversations, produce digital deliverables, and deliver work with the founder's oversight.

## 3. Outcomes

- A single control center for the founder.
- One orchestrated task system shared by all future agents.
- Explicit task state, progress, logs, evidence, and recoverable execution.
- Memory that is persistent, attributable to sources, scoped by permissions, and correctable.
- A repeatable process for research, verification, production, review, approval, and delivery.
- Controlled integrations for online research, communications, calling, software development, publishing, and project delivery.
- A strict one-work-package-at-a-time development process where a blocking defect prevents progression.

## 4. Principles

1. **Founder authority:** The founder defines company goals, policy, budgets, allowed capabilities, and approval requirements.
2. **Evidence before completion:** State changes and completion claims must be supported by actual system records or verification results.
3. **Explicit autonomy:** Every capability has a permission boundary. Model-generated text is not itself authorization.
4. **Durability:** Long-running work must survive normal process restarts and report the state of interrupted operations.
5. **Smallest viable scope:** Implement only what the current phase needs; keep future capabilities designed but disabled until their gates pass.
6. **Replaceable models:** Business logic and company memory must not be trapped inside one model vendor or model's context window.
7. **Privacy by design:** Collect and retain only information necessary for an authorized purpose.
8. **Honest uncertainty:** The system must report unknowns, assumptions, failed checks, and incomplete work.
9. **Human accountability:** Legal, financial, customer-impacting, or irreversible actions require policy-based approval.
10. **No false guarantees:** “Flawless” is a quality target, not a claim. Reliability is demonstrated through tests, monitoring, and recovery.

## 5. Stakeholders and users

### Initial owner/operator
The founder is the primary user and final authority. At first, the control center is private and accessible only to authorized operators.

### Future external users and clients
People may later use public-facing niche information services, submit tasks or enquiries, receive digital deliverables, or interact with sales and service workflows. Public access must not be enabled until access separation, data privacy, abuse controls, and operational support are ready.

### Internal AI workforce
Agents are system components, not trusted principals. Each must act through a registered identity, a bounded capability set, and the shared execution interface.

## 6. Scope boundaries

### In scope
- Founder control dashboard and main company chat.
- Task planning, delegation, state transitions, dependencies, retries, timeouts, cancellation, and recovery.
- Agent contracts, role-specific skills, memory, and source provenance.
- Niche research and information preparation.
- Business opportunity discovery and website quality assessment using permissible public information.
- Client relationship and deal records.
- Drafting proposals and managing approvals.
- Later integration of compliant external communication, including voice calling through an authorized provider.
- Website and digital deliverable production, testing, preview, and controlled delivery.
- Auditability, observability, security, and deployment operations.

### Out of scope for documentation stage
- Selecting the exact number of agents.
- Final classification of agent roles or deciding which agents are separate versus capabilities of a shared runtime.
- Production code, UI implementation, telephony setup, public deployment, or automatic outbound campaigns.
- Claiming legal compliance without reviewing the applicable current rules and provider terms.
- Fully autonomous execution of all possible work without human oversight.

## 7. Definition of project success

The company is not successful merely because its dashboard renders. The core success condition is a fully traceable loop:

1. Founder submits a bounded objective.
2. System records it and creates a plan.
3. Work is delegated through registered capabilities.
4. Each task records inputs, outputs, tool actions, and state transitions.
5. Results are checked against prewritten acceptance criteria.
6. Failures are visible and recoverable; unresolved issues remain open.
7. The founder can inspect, pause, cancel, approve, or reject work.
8. A final deliverable is presented with supporting evidence and limitations.

## 8. Governance

The founder approves scope and decision changes. The implementation operator must not silently redefine product behavior, expand permissions, add an agent role outside the agreed classification phase, or skip a release gate. Decisions and exceptions must be written to the decision log.
