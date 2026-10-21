# 02 — System Architecture

## 1. Architecture objective

Separate user interaction, policy enforcement, durable orchestration, model inference, external tools, memory, and verification so each part can be observed and tested independently. The model proposes reasoning and tool actions; deterministic application code validates permissions, executes authorized actions, records the outcome, and updates task state.

## 2. Proposed logical components

### A. Web client
A Next.js and TypeScript application provides the founder dashboard, chat, task details, approvals, CRM/project views, and settings. The client is not authoritative for task status or permissions. All privileged controls are verified by the API.

### B. API and identity boundary
A FastAPI service exposes versioned APIs for authentication, requests, tasks, approvals, policy, integrations, memory, leads, deals, and projects. It validates schema, identity, authorization, rate limits, and idempotency before persisting a command.

### C. Orchestration service
A stateful workflow engine manages plans, dependencies, checkpoints, delegation, waits, approvals, retries, cancellation requests, and terminal outcomes. The orchestration layer cannot bypass policy by asking a model whether an action is allowed.

### D. Durable background workers
A worker system executes long-running work outside request/response processes. PostgreSQL is the system of record. Redis may act as a broker/cache, but it is not the only durable record of work. A reconciliation process detects tasks that were committed but not dispatched, stale leases, and interrupted runs.

### E. Model gateway
A provider adapter normalizes chat, tool-calling, embeddings, structured output, timeouts, and usage accounting. The first development path may use Ollama locally. Other providers remain optional and are added behind the adapter. Provider keys are server-side only.

### F. Tool gateway
All external actions pass through registered tool definitions that specify schema, scope, permission, timeout, idempotency behavior, data handling, and audit requirements. Agents never receive unrestricted host shell, direct database credentials, arbitrary network access, or unbounded filesystem access.

### G. Data layer
PostgreSQL stores canonical entities and execution records. `pgvector` may be used for semantic retrieval when required, avoiding a separate vector database in the first release. Object storage or a controlled local artifact store holds larger files and deliverables, with metadata and access checks in PostgreSQL.

### H. Quality/evaluation service
Deterministic tests, schema checks, source verification rules, project build/test results, and independent review gates determine whether a deliverable can progress. Model self-evaluation is supplementary evidence, not the only quality gate.

### I. Observability
Structured logs, metrics, traces, audit records, queue-health metrics, provider latency/usage, and task-level evidence are correlated by IDs. Telemetry views must come from actual backend records; demo data is separately labeled.

## 3. Proposed deployment topology

```text
Browser
  -> HTTPS reverse proxy / ingress
      -> Next.js web application
      -> FastAPI API
           -> PostgreSQL (system of record)
           -> durable work broker / worker pool
           -> workflow/orchestration runtime
           -> model gateway (local Ollama and/or approved provider)
           -> tool gateway
                -> approved research/data sources
                -> CRM / email / messaging / compliant telephony (later gates)
                -> isolated build/test workspaces (later gates)
      -> Observability and alerting
```

Do not expose PostgreSQL, Redis, Ollama, worker control ports, Docker socket, or internal service endpoints directly to the public internet.

## 4. Proposed baseline choices

- **Frontend:** Next.js App Router + TypeScript.
- **API:** Python + FastAPI.
- **Canonical database:** PostgreSQL.
- **Semantic retrieval:** PostgreSQL with `pgvector` only when embedding retrieval is needed.
- **Workflow orchestration:** LangGraph is the recommended candidate for stateful agent flows, checkpoints, and human approval points.
- **Model runtime:** Provider adapter; Ollama for local development/low-cost experimentation and approved remote APIs as optional alternatives.
- **Background work:** A dedicated worker and durable broker for long-running jobs; never rely on the API process remaining alive.
- **Live status:** WebSockets or server-sent events, backed by persisted task state.
- **Integrations:** Direct typed adapters first; n8n may be introduced where its operational behavior, licensing, and self-hosted requirements fit.

These are the recommended baseline, not pinned package versions. Version selection, compatibility and deployment-specific tradeoffs are part of repository bootstrap and must be recorded before implementation.

## 5. System-of-record rules

- PostgreSQL is authoritative for task state, permissions, approvals, leads, deals, policies, and artifact metadata.
- Broker messages are signals to execute work, not canonical task definitions.
- Model conversation history is not the database of record.
- Memory retrieval may inform decisions but cannot override explicit current policy or approved project requirements.
- External side effects must be associated with a persisted intent and resulting outcome.
- UI state is a projection; refresh/reconnect must reconcile against the backend.

## 6. Resilience and idempotency

Use unique command/job IDs and idempotency keys for actions that may be retried. Persist the intent before dispatching side effects. Where an external provider supports idempotency keys, use them. Where it does not, use an explicit pending/confirmed/unknown outcome and require reconciliation instead of blindly repeating an action.

Workers should use bounded leases or heartbeats, explicit timeouts, retry classifications, exponential backoff with jitter, dead-letter/quarantine handling, and a reconciliation job. Cancellation is cooperative by default; hard termination must be supported for isolated execution tasks when safe.

## 7. Isolation model

Generated code, downloaded files, web content, and customer attachments are untrusted. Execute them only in disposable, resource-limited workspaces without host credentials, with restricted filesystem and network access. The public API process and orchestration process must not run arbitrary agent-generated shell commands directly.

## 8. Failure boundaries

- If a model provider fails, affected tasks enter a visible retryable or blocked state.
- If the broker fails, task definitions remain in the database and reconciliation can redispatch eligible tasks.
- If the dashboard disconnects, execution continues only within persisted policy; the dashboard can resynchronize later.
- If verification fails, the task remains in verification/rework or failed state; it is not silently completed.
- If an external call's outcome is uncertain, mark the outcome unknown and reconcile before any retry that could duplicate contact.
- If a policy service or permission check is unavailable, fail closed for external side effects.

## 9. Architecture constraints

- One monorepo for the first release, with clear package boundaries.
- One canonical database initially.
- One execution contract used by every role.
- Do not create one web app, database, or model service per agent.
- The proposed role count and classification are documented in `17_AGENT_CLASSIFICATION.md`; founder approval is pending. The architecture remains role-count agnostic and uses one shared execution contract.
- No production external calls, public publication, money movement, contract acceptance, or live deployment before their release gates pass.
