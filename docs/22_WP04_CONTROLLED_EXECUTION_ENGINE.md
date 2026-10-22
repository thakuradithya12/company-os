# 22 — WP-04: Controlled Execution Engine

## 1. Executive Summary & Objective

Work Package 04 implements the **Controlled Execution Engine** for Company OS. It transitions the system from passive task definition and routing to bounded, deterministic execution.

Rather than giving models or agents unconstrained shell access or arbitrary networking, execution is guarded by:
1. **Tier 0 Read-Only Bounded Execution**: Only explicitly registered, risk-tiered tools may be executed. The first implemented tool is `research.source_verifier`.
2. **Hardened SSRF Defenses & DNS Anti-Rebinding**: Direct-to-IP outbound HTTP client that resolves DNS once, rejects all private, loopback, link-local, carrier-grade NAT, and cloud metadata IPs, connects directly to the validated IP, and inspects redirect targets manually.
3. **Strict Two-Phase Transaction Boundaries**: Database transactions are never held open during network operations. Phase 1 claims the execution in Tx 1, Phase 2 executes the tool outside any database transaction, and Phase 3 persists outcomes and enforces the completion gate in Tx 2.
4. **Completion Verification Gate**: Tasks cannot transition to `COMPLETED` merely because an agent ran. Completion requires verified, non-empty checks and a durable SHA-256 evidence reference.
5. **Durable Attempt Tracking & Concurrency Locks**: Execution attempts are persisted in `task_executions`. Concurrent execution requests for the same task are rejected with 409 Conflict. Interrupted or crashed executions are tracked explicitly without unsafe auto-retries.

---

## 2. Risk Tiers and Tool Allowlisting

Every executable tool in Company OS is classified under an explicit risk tier:

| Risk Tier | Identifier | Policy | Implemented Tools |
| :--- | :--- | :--- | :--- |
| **Tier 0** | `tier_0_read_only` | Read-only operations, zero side-effects, bounded resource limits. Allowed automatically for authorized specialist. | `research.source_verifier` |
| **Tier 1** | `tier_1_reversible` | Low-impact actions that are idempotent or reversible. | None (Reserved for future WPs) |
| **Tier 2** | `tier_2_high_impact` | Irreversible actions, external communications, financial impact. Strictly requires human approval. | None (Reserved for future WPs) |

### Tool-to-Agent Authorization Matrix
Tools can only be invoked by designated agent specialists:
- `research.source_verifier` is strictly authorized for `AG-03` (Research Specialist).
- Any attempt by other agents (e.g. `AG-07` Builder) to invoke `research.source_verifier` is rejected with `403 Forbidden` (`UnauthorizedToolError`).

---

## 3. Network Security & SSRF Penetration Guard

The `research.source_verifier` tool utilizes `SSRFPenetrationGuard` and `BoundedHttpClient` (`apps/api/src/company_os/domain/network_security.py`):

1. **Prohibited Subnets**:
   - IPv4: `127.0.0.0/8` (loopback), `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16` (RFC1918 private), `169.254.0.0/16` (link-local / AWS/GCP cloud metadata `169.254.169.254`), `100.64.0.0/10` (carrier-grade NAT), `0.0.0.0/8` (unspecified).
   - IPv6: `::1` (loopback), `fe80::/10` (link-local), `fc00::/7` (unique local address), and IPv4-mapped IPv6 `::ffff:0:0/96` (recursively inspected).
2. **DNS Rebinding Prevention**:
   - Hostnames are resolved using `socket.getaddrinfo`. If *any* returned IP is in a prohibited range, the request fails closed immediately.
   - Outbound HTTP connection connects directly to the validated IP address (`http.client.HTTPConnection(ip_str, port)`). The `Host: <hostname>` header is passed explicitly. No secondary DNS resolution occurs at socket connect time.
3. **Manual Redirect Inspection**:
   - HTTP redirects (`301`, `302`, `303`, `307`, `308`) are intercepted. Up to 3 redirects are followed, but each redirect URL is independently resolved and passed through `SSRFPenetrationGuard` before connecting.
4. **Content & Resource Bounds**:
   - Timeout: Maximum 5.0 seconds per request.
   - Response Size Ceiling: Maximum 1,048,576 bytes (1 MB) streamed in chunks. Exceeding this raises `ResponseSizeExceededError`.
   - Content-Type Whitelist: Only `text/html`, `text/plain`, `application/json`, `application/xml`, and `text/xml` are accepted. Binary or media payloads raise `InvalidContentTypeError`.

---

## 4. Two-Phase Database Transaction Architecture

Holding database transactions or row locks during external HTTP requests risks connection starvation, thread pool exhaustion, and deadlock. Company OS enforces a 3-phase split:

```
[Client / API Request]
         │
         ▼
 ┌─────────────────────────────────────────────────────────┐
 │ Phase 1: Transaction 1 (DB Claim & Lock)               │
 │ • SELECT ... FOR UPDATE on TaskRecord                   │
 │ • Reject if task is terminal (409) or running (409)     │
 │ • Check ToolRegistry authorization & schema validation │
 │ • Transition task status: QUEUED/READY -> RUNNING      │
 │ • Insert TaskExecutionRecord (status: RUNNING)         │
 │ • Insert TaskAuditEventRecord (execution.started)       │
 │ • COMMIT Transaction 1                                  │
 └─────────────────────────────────────────────────────────┘
         │
         ▼ (DB connection closed and returned to pool)
 ┌─────────────────────────────────────────────────────────┐
 │ Phase 2: Tool Execution (NO DB Transaction)             │
 │ • Invoke tool.handler(validated_params)                 │
 │ • Real HTTP retrieval via BoundedHttpClient             │
 │ • Calculate SHA-256 digest of content                   │
 │ • Execute verification checks                           │
 │ • Trap any NetworkSecurityError or HTTP exception       │
 └─────────────────────────────────────────────────────────┘
         │
         ▼
 ┌─────────────────────────────────────────────────────────┐
 │ Phase 3: Transaction 2 (Outcome & Completion Gate)      │
 │ • Open fresh DB session                                 │
 │ • SELECT ... FOR UPDATE on TaskRecord & ExecutionRecord │
 │ • Update TaskExecutionRecord (output, checks, evidence) │
 │ • Completion Verification Gate:                         │
 │     IF (all checks passed == True AND evidence_ref):    │
 │       Task status -> COMPLETED                          │
 │       Insert audit event (task.completed)               │
 │     ELSE:                                               │
 │       Task status -> BLOCKED (or FAILED if max retries) │
 │       Insert audit event (task.blocked / task.failed)   │
 │ • COMMIT Transaction 2                                  │
 └─────────────────────────────────────────────────────────┘
         │
         ▼
 [Return ExecutionResult]
```

---

## 5. Persistence & Migration

- Migration: `apps/api/alembic/versions/0004_task_executions.py`
- Table: `task_executions`
  - `id`: UUID (Primary Key)
  - `task_id`: UUID (Foreign Key to `tasks.id`, `RESTRICT`)
  - `agent_id`: VARCHAR(32)
  - `tool_id`: VARCHAR(80)
  - `risk_tier`: VARCHAR(32) (`tier_0_read_only`, `tier_1_reversible`, `tier_2_high_impact`)
  - `status`: VARCHAR(32) (`running`, `completed`, `failed`, `blocked`, `interrupted`)
  - `input_parameters`: JSON
  - `output_payload`: JSON
  - `error_message`: TEXT (Nullable)
  - `evidence_reference`: VARCHAR(256) (Nullable, format: `evidence:research:sha256:<hash>`)
  - `verification_checks`: JSON (List of structured check objects)
  - `duration_ms`: INTEGER
  - `created_at`: TIMESTAMPTZ
  - `updated_at`: TIMESTAMPTZ

---

## 6. API Endpoints

### 1. `POST /tasks/{task_id}/execute`
Triggers execution of an approved tool for the task.
- **Request Body**:
  ```json
  {
    "tool_id": "research.source_verifier",
    "parameters": {
      "url": "https://example.com/sec/filing",
      "expected_snippet": "Annual Report 2026"
    },
    "agent_id": "AG-03",
    "caller": "system",
    "request_id": "req-123"
  }
  ```
- **Responses**:
  - `200 OK`: Tool execution finished. Returns `TaskExecutionResponse`.
  - `403 Forbidden`: Agent not authorized for tool (`UnauthorizedToolError`).
  - `404 Not Found`: Task not found or Tool not registered.
  - `409 Conflict`: Task already completed/terminal or active execution is already running.
  - `422 Unprocessable Entity`: Input parameters fail schema validation.

### 2. `GET /tasks/{task_id}/executions`
Retrieves chronological execution history for the specified task.
- **Responses**:
  - `200 OK`: Returns array of `TaskExecutionResponse` objects.
  - `404 Not Found`: Task not found.

---

## 7. Crash Recovery & Non-Idempotent Protection

- Crashed or killed workers leave tasks in `RUNNING`.
- `mark_interrupted_executions(session, task_id)` transitions stranded execution attempts to `INTERRUPTED`.
- Operations are **not** automatically retried blindly. Any retry requires explicit caller action, preserving forensic state and preventing duplicate non-idempotent operations.
