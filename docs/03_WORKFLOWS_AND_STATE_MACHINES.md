# 03 — Workflows and State Machines

## 1. Objective lifecycle

1. Receive the founder's objective and persist the original input.
2. Normalize the request into expected outcome, scope, constraints, deadlines, budget/usage limits, external effects, and success criteria.
3. Identify missing decisions. Ask the founder only when missing information is material to correctness, cost, risk, or an irreversible choice.
4. Create a versioned plan with tasks, dependency edges, required capabilities, output schemas, and acceptance criteria.
5. Validate that every planned capability and tool is registered and authorized.
6. Execute ready tasks with bounded parallelism. Persist each attempt and checkpoint.
7. Collect output artifacts and evidence.
8. Run deterministic checks and independent review where required.
9. If checks fail, create a bounded rework cycle or mark the task blocked/failed with the reason. Do not loop indefinitely.
10. Request founder approval for configured actions and wait on a persisted approval record.
11. Deliver the final result, with completed scope, sources, tests, unresolved limitations, and follow-up items.
12. Store approved reusable knowledge separately from the task transcript.

## 2. Task state model

Canonical task states:

- `queued`: accepted and waiting for execution capacity.
- `planning`: creating or validating a plan.
- `ready`: dependencies satisfied and eligible to run.
- `running`: a worker holds a valid execution lease and is performing the task.
- `awaiting_approval`: a decision by an authorized human is required.
- `verifying`: output is being checked against acceptance criteria.
- `rework`: a failed check allows a bounded corrective attempt.
- `blocked`: the task cannot safely proceed due to a dependency, missing information, permission, provider issue, or policy gate.
- `completed`: required acceptance checks passed and the output is persisted.
- `failed`: terminal error after applicable retries or a non-retryable failure.
- `cancel_requested`: cancellation was requested but cleanup/outcome reconciliation is underway.
- `cancelled`: cancellation/cleanup completed and any external side effect was reconciled as needed.
- `unknown_outcome`: an external effect may have occurred but confirmation is unavailable; do not automatically repeat it.

All state transitions are validated by application code. Each transition records actor, timestamp, reason, prior state, new state, and related execution attempt.

## 3. Allowed transition principles

- A new task may move to `queued`, then `planning` or `ready`.
- A task can become `running` only when dependencies, permissions, capacity, and budgets have been checked.
- `running` can enter `awaiting_approval`, `verifying`, `blocked`, `rework`, `failed`, or `cancel_requested`.
- `verifying` can enter `completed`, `rework`, `blocked`, or `failed`.
- `completed`, `failed`, and `cancelled` are terminal unless an explicit new task/reopen operation is recorded. Do not silently mutate a terminal history.
- `unknown_outcome` requires a reconciliation decision before reattempting the external side effect.
- Any terminal task state must include a reason and final evidence reference where applicable.

## 4. Agent execution contract

Every execution receives a bounded envelope:

- task ID and attempt ID;
- role/capability identifier and contract version;
- objective, authorized scope, and forbidden actions;
- inputs and trusted/untrusted provenance labels;
- tool allowlist and data-access scope;
- budget, timeout, step/iteration ceiling, and output-size ceiling;
- expected output schema and acceptance criteria;
- checkpoint/trace identifiers.

The executor returns a structured result: status, summary, output/artifact references, sources/evidence, checks run, unresolved uncertainties, error classification, and recommended next step. The runtime validates the result schema before accepting it.

## 5. Retry policy

- Retry only transient errors (for example, rate limit, temporary network failure, or recoverable provider timeout) within a configured attempt and time budget.
- Do not automatically retry permission failures, invalid inputs, policy denial, or deterministic acceptance failures without a planned correction.
- Use exponential backoff and provider `Retry-After` information where available.
- Record every attempt and its error; do not overwrite failure history.
- A retry must not duplicate a side effect. Use idempotency or reconciliation first.

## 6. Human approval workflow

An approval request must contain:
- exact proposed action and target;
- content, price, scope, agreement terms, or deployment diff being approved;
- the agent's rationale and source evidence;
- risk and reversibility classification;
- expiration time and impact of not responding;
- permitted approve/reject/edit/cancel operations.

Approval is bound to the specific version of the proposed action. If content or terms change, the approval becomes stale and must be renewed. Approval decisions are immutable audit events.

## 7. Cancel and emergency-stop behavior

Canceling a task prevents it from starting new child tasks and asks workers to stop safely. Active subprocesses should receive a termination signal and then be forcibly terminated after a configured grace period inside their isolated workspace. The runtime must clean up temporary resources and reconcile side effects.

The global stop switch must stop dispatch and prevent new external side effects. It should not erase records. Cleanup/reconciliation operations remain available to authorized operators. The UI must show if a worker or external action has not yet confirmed termination.

## 8. Completion definition

A task is complete only when:
- required output exists and is readable;
- declared acceptance checks passed;
- required independent verification is present;
- evidence and provenance are attached;
- no blocking issue remains;
- required approval is recorded;
- task state and artifacts are persisted.

A partial or unverified output must be labelled partial/unverified, not complete.
