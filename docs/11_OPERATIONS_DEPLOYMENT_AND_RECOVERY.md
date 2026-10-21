# 11 — Operations, Deployment, and Recovery

## 1. Environments

Maintain distinct configurations for:
- **Local development:** founder/engineering environment with fake external integrations by default.
- **Test/CI:** isolated database and worker, deterministic fixtures, no production credentials.
- **Staging:** production-like deployment using synthetic data and disabled outbound side effects.
- **Production:** real users and approved integrations only after all release gates pass.

Never point a local/staging CLI or app at production by accident. Environment identity must be visible in logs and, for operator-only pages, the dashboard.

## 2. Configuration

- Commit `.env.example` with placeholders and validation rules; never commit real `.env` files.
- Validate required environment variables at startup and fail clearly when critical values are missing.
- Use separate database, broker, model-provider, and integration credentials per environment.
- Document port mappings and bind internal services to private interfaces/networks.
- Pin compatible dependency versions and use lockfiles.
- Run database schema migrations as an explicit release step with backup/rollback planning.

## 3. Local developer setup

The repository must eventually provide one canonical quick-start path with prerequisites, exact commands, expected health response, test commands, and common failure remedies. Prefer a documented containerized development environment for PostgreSQL and required supporting services, while allowing local Ollama when desired. Do not hide required initialization steps inside undocumented scripts.

## 4. Health and observability

Expose separate checks for:
- **Liveness:** process is running.
- **Readiness:** application can serve its intended requests and required dependencies are available.
- **Dependency health:** database, broker, model provider, artifact store, and selected integration status.

Track queue depth, age of oldest queued task, active and stale leases, task completion/failure rate, retry count, worker heartbeat, model latency/error/usage, database saturation, disk space, backup recency, integration failure rates, and unknown external outcomes.

Logs must be structured and correlated using request/task/attempt/tool/trace IDs. Do not put secrets, access tokens, passwords, unnecessary personal data, or full sensitive customer content into logs.

## 5. Backups and restore

Define recovery-point and recovery-time objectives before public launch. Back up PostgreSQL, required artifact metadata and objects, key configuration (excluding raw secrets), and other persistent state. Encrypt backups and restrict access. Set retention schedules and deletion rules.

A backup is not proven until a restore test succeeds. Record the test date, environment, restored version, checks performed, and defects. Include schema migration compatibility and integrity checks.

## 6. Worker and queue recovery

- Maintain durable task records in PostgreSQL.
- Use leases/heartbeats so abandoned work is detected.
- Reconcile committed-but-undispatched jobs and stale running tasks.
- Use idempotency to avoid duplicate side effects.
- Send repeatedly failing jobs to a visible quarantine/dead-letter state with diagnostics.
- Bound retries and retry only transient failures.
- Provide a controlled requeue action that records operator identity and reason.

## 7. Release and rollback

1. Confirm current Git commit and clean working tree.
2. Run required checks and review the release-gate report.
3. Confirm migration order, backward compatibility, backup, and rollback path.
4. Deploy to staging and execute smoke/end-to-end/security checks relevant to the change.
5. Obtain required approval for production.
6. Deploy and watch health, queue, errors, and task outcomes.
7. Roll back or disable the feature if a gate fails; preserve audit evidence and reconcile external outcomes.

For schema changes, prefer compatible expand/migrate/contract steps. Do not roll back database changes blindly when data may have been written using the new schema.

## 8. Emergency controls

Authorized operators must be able to:
- stop new task dispatch;
- block external side effects;
- disable a specific integration/provider;
- request cancellation of active work;
- revoke a credential/connection;
- restrict logins or disable public entry points;
- inspect unresolved/unknown external outcomes.

The stop system must be independent of model cooperation and must record its state persistently. Define which workers can continue cleanup after stop and which actions are blocked.

## 9. Availability expectations

An always-available online service requires an always-on host and reliable network/service dependencies. A laptop-hosted local prototype is not continuous production hosting. Free hosting or API tiers may sleep, cap requests, restrict background workers, or change limits. Production availability must be based on measured infrastructure and an explicit operational budget, not a promise of free 24/7 operation.
