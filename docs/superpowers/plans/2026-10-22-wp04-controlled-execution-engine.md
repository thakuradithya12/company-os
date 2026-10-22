# WP-04 Implementation Plan: Controlled Execution Engine for Company OS

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement a secure, bounded, and auditable execution engine that runs allowlisted tools for assigned specialist agents, performs real HTTP retrieval with anti-SSRF and DNS-rebinding defense, splits database transactions around network I/O, prevents concurrent duplicate execution, persists execution attempts, and enforces strict completion verification evidence.

**Architecture:**
- **Tool Domain Layer:** `ToolRegistry` with typed `ToolDefinition` contracts, risk tiers (`Tier 0` read-only internal to `Tier 3` high impact).
- **Minimal Real Tool:** `research.source_verifier` for agent `AG-03` (Research & Evidence Agent) performing real bounded HTTP GET retrievals (strict timeouts, 1MB size ceiling, text/json content types).
- **SSRF & DNS Security:** Dedicated `SSRFPenetrationGuard` validating schemes (`http`/`https` only), resolving DNS once, checking IPv4 and IPv6 against comprehensive prohibited ranges (loopback, private, link-local, carrier-grade NAT, IPv4-mapped IPv6), validating every redirect hop manually, and connecting directly to the validated IP with SNI/Host headers to eliminate DNS rebinding.
- **Two-Phase Transaction Boundaries:**
  - *Phase 1 (Claim Transaction):* Atomically claims execution on `READY` task, increments version, increments attempt count, persists `TaskExecutionRecord` in `status="running"`, transitions task to `RUNNING`, logs `task.execution_claimed` audit event, and commits.
  - *Phase 2 (Network Execution):* Executes the tool completely outside any database transaction (no open connections or table locks held during HTTP requests).
  - *Phase 3 (Outcome Transaction):* Opens a fresh transaction, verifies version/state concurrency, updates `TaskExecutionRecord` with results/checks/evidence, transitions task to `COMPLETED` (if verified) or `BLOCKED` (if failed/unauthorized), and logs audit events.
- **Concurrency & Crash Handling:** Atomic `with_for_update()` lock and version checks reject concurrent execution attempts with HTTP 409 Conflict. Interrupted executions remain recorded with start times and can be safely reconciled; non-idempotent operations are never automatically retried.
- **Completion Gate:** Integration with `transition_task` requiring `verification_evidence` with `passed=True`, non-empty `checks`, and a durable `evidence_ref`.
- **API Endpoint:** `POST /tasks/{task_id}/execute` and `GET /tasks/{task_id}/executions`.

**Tech Stack:** Python 3.13, FastAPI, SQLAlchemy 2.0, Alembic, PostgreSQL / SQLite, Pydantic v2, Python `urllib`/`http.client`/`ssl`/`socket`/`ipaddress`.

**Spec:** `docs/05_SECURITY_PRIVACY_AND_GOVERNANCE.md`, `docs/06_AGENT_RUNTIME_CONTRACT.md`, `docs/17_AGENT_CLASSIFICATION.md`, `docs/agent-specs/AG-03_RESEARCH_EVIDENCE.md`.

---

## Global Constraints

- **No arbitrary shell execution:** Never expose host shell, subprocess execution, or arbitrary command runners.
- **Strict tool allowlisting:** Agents can only invoke tools explicitly enumerated in `allowed_agent_ids`.
- **SSRF protection:** All outbound requests must resolve and validate destination IPs before connection. No private, loopback, or link-local IPs. No DNS rebinding.
- **Transaction decoupling:** Never hold a database transaction open while waiting for network I/O.
- **Evidence integrity:** A hash alone is never proof that a claim is true. Evidence must include verified URL, timestamp, content metadata, checks, and artifact reference.
- **Fail closed:** Any validation error, permission denial, or network failure leaves the task in `blocked` or `failed` with sanitized error codes.
- **Preserve baseline:** Existing health endpoints, task API endpoints, and migrations remain intact. Preserve `apps/web/next-env.d.ts` unstaged.

---

## Review Focus

1. **Adversarial SSRF & DNS Rebinding:** Attacking `research.source_verifier` with `127.0.0.1`, `localhost`, `169.254.169.254`, `10.0.0.1`, `[::1]`, `[::ffff:127.0.0.1]`, `file:///`, or redirects to internal IPs -> must fail closed before connection or redirect.
2. **Concurrent Duplicate Execution:** Two concurrent execution requests for the same task -> exactly one succeeds in claiming; the second is rejected with 409 Conflict.
3. **Transaction Isolation during Network Latency:** Simulating a slow network request -> confirm zero active database transactions or locks exist during the network phase.
4. **Completion Verification Gate:** Output with `passed=False` or missing `evidence_ref` -> task cannot reach `completed`; must transition to `blocked` with explicit error code.
5. **Crash & Interruption Safety:** Crash during Phase 2 -> execution attempt remains identifiable in database with `running` status and start timestamp, task remains `RUNNING`, never falsely marked `completed`.

---

## Migration Assessment

A new additive migration is required:
- **Migration ID:** `0004_task_executions`
- **Revises:** `0003_task_agent_routing`
- **Table created:** `task_executions`
  - `id`: UUID (Primary Key)
  - `task_id`: UUID (Foreign Key to `tasks.id`, ondelete="RESTRICT", indexed)
  - `agent_id`: String(32) (indexed)
  - `tool_id`: String(80) (indexed)
  - `status`: String(32) (`running`, `success`, `failed`, `permission_denied`, `validation_failed`, `approval_required`, `interrupted`)
  - `input_parameters`: JSON
  - `output_data`: JSON (nullable)
  - `evidence_ref`: String(128) (nullable)
  - `checks`: JSON
  - `error_code`: String(80) (nullable)
  - `error_message`: Text (nullable)
  - `started_at`: DateTime(timezone=True)
  - `completed_at`: DateTime(timezone=True) (nullable)
  - `duration_ms`: Integer (nullable)
  - `created_at`: DateTime(timezone=True), server_default=now()
- **Downgrade:** Drops index and `task_executions` table cleanly.
- **Impact on existing data:** Fully additive and non-breaking.

---

## Detailed Task Breakdown

### Task 1: SSRF & DNS-Rebinding Guard and Bounded HTTP Client

**Files:**
- Create: `apps/api/src/company_os/domain/network_security.py`
- Test: `apps/api/tests/test_network_security.py`

**Interfaces:**
- Produces: `SSRFPenetrationGuard`
  - `validate_url(url: str, allow_loopback: bool = False) -> tuple[str, str, int]` (scheme, host, port)
  - `resolve_and_validate_ip(host: str, port: int, allow_loopback: bool = False) -> ipaddress.IPv4Address | ipaddress.IPv6Address`
  - `is_prohibited_ip(ip: IPv4Address | IPv6Address, allow_loopback: bool = False) -> bool`
- Produces: `BoundedHttpClient`
  - Performs direct-to-IP HTTP/HTTPS GET requests with SNI and Host headers
  - Max response size ceiling (1 MB)
  - Connection timeout (5s), read timeout (5s)
  - Manual redirect validation (max 3 hops, each hop validated against SSRF guard)
  - Accepted content types: `text/html`, `text/plain`, `application/json`, `application/xml`

- [ ] **Step 1: Write failing unit tests for `SSRFPenetrationGuard` and `BoundedHttpClient`**
  - Test rejection of loopback `127.0.0.1`, `localhost`, `[::1]`, `[::ffff:127.0.0.1]`
  - Test rejection of AWS/cloud metadata `169.254.169.254`, `fe80::`
  - Test rejection of private subnets `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, `fc00::/7`
  - Test rejection of non-HTTP schemes (`file://`, `ftp://`, `gopher://`)
  - Test manual redirect hop validation (detecting redirect to private IP and aborting)
  - Test response size ceiling truncation/rejection (>1MB)
  - Test content-type validation

- [ ] **Step 2: Run test to verify it fails**
  Run: `uv run --locked --python 3.13.16 pytest apps/api/tests/test_network_security.py -v`
  Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Implement `SSRFPenetrationGuard` and `BoundedHttpClient` in `network_security.py`**
  - Implement IP range checks with `ipaddress`
  - Implement DNS resolution and direct-IP socket connection
  - Implement response stream limit and manual redirect loop

- [ ] **Step 4: Run tests to verify they pass**
  Run: `uv run --locked --python 3.13.16 pytest apps/api/tests/test_network_security.py -v`
  Expected: PASS

---

### Task 2: Tool Registry and Real Tool `research.source_verifier`

**Files:**
- Create: `apps/api/src/company_os/domain/tools.py`
- Modify: `apps/api/src/company_os/domain/__init__.py`
- Test: `apps/api/tests/test_tools.py`

**Interfaces:**
- Produces: `RiskTier`, `ToolDefinition`, `ToolRegistry`, `create_default_tool_registry()`
- Produces: `ExecutionStatus`, `ExecutionRequest`, `ExecutionResult`
- Produces: Real tool `research.source_verifier`:
  - Allowed agent: `AG-03`
  - Executes real bounded HTTP retrieval via `BoundedHttpClient`
  - Extracts title, snippet, byte count, headers, SHA-256 hash
  - Builds structured verification `checks` and durable `evidence_ref` (`evidence:research:sha256:<hash>`)

- [ ] **Step 1: Write failing unit tests in `apps/api/tests/test_tools.py`**
  - Test tool registry registration and lookup
  - Test agent allowlist verification (`AG-03` allowed, `AG-07` denied)
  - Test real HTTP retrieval on a test server producing valid checks and evidence
  - Test tool execution failure on network errors

- [ ] **Step 2: Run test to verify it fails**
  Run: `uv run --locked --python 3.13.16 pytest apps/api/tests/test_tools.py -v`
  Expected: FAIL

- [ ] **Step 3: Implement tool contracts and `research.source_verifier` in `company_os/domain/tools.py`**
  - Define `ToolDefinition` and `ToolRegistry`
  - Implement `SourceVerifierInput` schema
  - Implement `research.source_verifier` execution handler

- [ ] **Step 4: Run tests to verify they pass**
  Run: `uv run --locked --python 3.13.16 pytest apps/api/tests/test_tools.py -v`
  Expected: PASS

---

### Task 3: Database Model and Alembic Migration `0004_task_executions`

**Files:**
- Create: `apps/api/alembic/versions/0004_task_executions.py`
- Modify: `apps/api/src/company_os/db/models/task.py`
- Modify: `apps/api/src/company_os/db/models/__init__.py`
- Test: `apps/api/tests/test_task_executions_migration.py`

**Interfaces:**
- Produces: `TaskExecutionRecord` mapped model
- Relationship: `TaskRecord.executions`

- [ ] **Step 1: Write failing test in `apps/api/tests/test_task_executions_migration.py`**
  - Verify `TaskExecutionRecord` table creation, foreign key to `tasks.id`, fields, and indices
  - Verify clean upgrade and downgrade

- [ ] **Step 2: Run test to verify it fails**
  Run: `uv run --locked --python 3.13.16 pytest apps/api/tests/test_task_executions_migration.py -v`
  Expected: FAIL

- [ ] **Step 3: Add `TaskExecutionRecord` to `models/task.py` and write Alembic migration `0004_task_executions.py`**

- [ ] **Step 4: Run tests and check Alembic heads**
  Run: `uv run --locked --python 3.13.16 pytest apps/api/tests/test_task_executions_migration.py -v`
  Run: `uv run --locked --python 3.13.16 alembic heads`
  Expected: PASS, head is `0004_task_executions`

---

### Task 4: Controlled Execution Engine with Two-Phase Transactions

**Files:**
- Create: `apps/api/src/company_os/services/execution_engine.py`
- Modify: `apps/api/src/company_os/services/__init__.py`
- Test: `apps/api/tests/test_execution_engine.py`

**Interfaces:**
- Produces: `execute_task_tool(session_factory, task_id, tool_id, parameters, agent_id=None, request_id=None)`
- Features:
  - *Phase 1:* Short transaction claims execution on `READY` task, increments attempt count, creates `TaskExecutionRecord(status="running")`, transitions task to `RUNNING`, commits.
  - *Phase 2:* Executes tool outside any transaction.
  - *Phase 3:* Fresh transaction records outcome, transitions task to `COMPLETED` (via `transition_task` with verification evidence) or `BLOCKED` (on failure/error), commits.
  - Prevents concurrent duplicate execution with 409 Conflict.
  - Reconciles interrupted executions.

- [ ] **Step 1: Write failing tests in `apps/api/tests/test_execution_engine.py`**
  - Test end-to-end execution success: `ready` -> `running` -> `verifying` -> `completed`
  - Test unapproved agent/tool mismatch -> `PERMISSION_DENIED`, task `blocked`
  - Test SSRF attempt -> `VALIDATION_FAILED`, task `blocked`
  - Test tool execution failure -> `FAILED`, task `blocked`
  - Test concurrent execution conflict -> second request rejected with 409
  - Test zero transaction open during network request
  - Test crash / interrupted execution handling

- [ ] **Step 2: Run test to verify it fails**
  Run: `uv run --locked --python 3.13.16 pytest apps/api/tests/test_execution_engine.py -v`
  Expected: FAIL

- [ ] **Step 3: Implement `execute_task_tool` in `company_os/services/execution_engine.py`**

- [ ] **Step 4: Run tests to verify they pass**
  Run: `uv run --locked --python 3.13.16 pytest apps/api/tests/test_execution_engine.py -v`
  Expected: PASS

---

### Task 5: API Endpoints `POST /tasks/{task_id}/execute` & `GET /tasks/{task_id}/executions`

**Files:**
- Modify: `apps/api/src/company_os/api/schemas.py`
- Modify: `apps/api/src/company_os/api/tasks.py`
- Modify: `apps/api/tests/test_tasks_api.py`

**Interfaces:**
- Produces: `TaskExecuteRequest`, `TaskExecutionResponse`
- Produces: `POST /tasks/{task_id}/execute` (and `/api/v1/tasks/{task_id}/execute`)
- Produces: `GET /tasks/{task_id}/executions` (and `/api/v1/tasks/{task_id}/executions`)

- [ ] **Step 1: Write failing API integration tests in `test_tasks_api.py`**
  - Test execute endpoint on routed task -> 200 OK
  - Test unauthorized tool execution via API -> 403 / 400
  - Test concurrent execution via API -> 409 Conflict
  - Test missing task -> 404 Not Found
  - Test listing executions via `GET /tasks/{task_id}/executions`

- [ ] **Step 2: Run test to verify it fails**
  Run: `uv run --locked --python 3.13.16 pytest apps/api/tests/test_tasks_api.py -k "execute" -v`
  Expected: FAIL

- [ ] **Step 3: Implement schemas and API routes in `schemas.py` and `tasks.py`**

- [ ] **Step 4: Run tests to verify they pass**
  Run: `uv run --locked --python 3.13.16 pytest apps/api/tests/test_tasks_api.py -v`
  Expected: PASS

---

### Task 6: Documentation, Linting, & Baseline Verification

**Files:**
- Create: `docs/22_WP04_CONTROLLED_EXECUTION_ENGINE.md`
- Modify: `docs/08_API_CONTRACTS.md`

- [ ] **Step 1: Write WP-04 documentation in `docs/22_WP04_CONTROLLED_EXECUTION_ENGINE.md`**
- [ ] **Step 2: Update `docs/08_API_CONTRACTS.md`**
- [ ] **Step 3: Run full verification suite**
  - `uv run --locked --python 3.13.16 ruff check apps/api/src apps/api/tests`
  - `uv run --locked --python 3.13.16 pytest`
  - `uv run --locked --python 3.13.16 alembic heads`
  - `powershell -ExecutionPolicy Bypass -File scripts/check.ps1`
- [ ] **Step 4: Verify git status and unstaged `apps/web/next-env.d.ts`**

---

## Exact Acceptance Criteria

1. **Real Execution:**
   - `research.source_verifier` performs actual bounded HTTP GET retrieval using direct IP connection.
   - Enforces connection timeout (5s), read timeout (5s), and response size ceiling (1 MB).
   - Enforces accepted content types (`text/html`, `text/plain`, `application/json`, `application/xml`); unaccepted types fail closed.

2. **SSRF & DNS Security:**
   - Rejects loopback (`127.0.0.0/8`, `::1`), private (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, `fc00::/7`), link-local/cloud metadata (`169.254.0.0/16`, `fe80::/10`), IPv4-mapped IPv6 (`::ffff:127.0.0.1`), and non-HTTP schemes.
   - Connects directly to the pre-validated IP to eliminate DNS rebinding.
   - Disables automatic redirects; manual redirect hops are individually validated against the SSRF guard (max 3 hops).

3. **Transaction Boundaries:**
   - Database transactions are never held open during HTTP requests.
   - Claim transaction commits before network I/O; outcome transaction opens and commits after network I/O completes.

4. **Concurrency & Crash Safety:**
   - Atomic task-state and version checks reject concurrent execution attempts on the same task with HTTP 409 Conflict.
   - Execution attempts are assigned a durable UUID; interrupted executions remain recorded as `status="running"` with start timestamps, never falsely marked `completed`.
   - Non-idempotent operations are never automatically retried.

5. **Evidence Integrity:**
   - Stores durable evidence reference (`evidence:research:sha256:<hash>`), source URL, retrieval timestamp, HTTP status, content metadata, and discrete verification check results.
   - A hash alone is never accepted as verification proof.

6. **Completion Gate:**
   - Tasks only transition to `COMPLETED` when verification checks succeed (`passed=True`, non-empty `checks`, and valid `evidence_ref`).
   - Failed or interrupted work transitions to `BLOCKED` (or `FAILED`), never `COMPLETED`.

7. **Tool Allowlisting:**
   - Tool execution is permitted only if `task.assigned_agent_id` is in the tool's `allowed_agent_ids`. Unauthorized calls fail with `PERMISSION_DENIED` (`UNAUTHORIZED_TOOL`).

8. **Bounded Scope:**
   - No arbitrary shell commands, unrestricted tool invocation, or autonomous loops.
   - Full repository check (`scripts/check.ps1`) passes cleanly with 0 errors and 0 warnings.
