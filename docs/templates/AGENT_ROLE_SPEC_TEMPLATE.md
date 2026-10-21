# Agent / Capability Specification — Template

> Fill this in during the approved workforce inventory/classification phase. This template does not constitute a decision that a role is needed.

## Identification
- Capability ID:
- Name:
- Version:
- Proposed owner/reviewer:
- Status: proposed / approved / implemented / retired

## Purpose and boundaries
- Business objective served:
- In-scope responsibilities:
- Explicitly out-of-scope responsibilities:
- Required inputs:
- Expected outputs/artifacts:
- Upstream dependencies:
- Downstream consumers:

## Tools and authority
- Allowed tools/integrations:
- Read scopes:
- Write scopes:
- Prohibited actions:
- External side effects:
- Approval gates:
- Escalation conditions:

## Model and runtime
- Required model capabilities:
- Candidate provider/model configuration:
- Structured input/output schemas:
- Memory sources allowed:
- Memory write/promote policy:
- Timeout and maximum steps:
- Cost/token/resource limits:
- Retry and fallback rules:

## Quality
- Acceptance criteria:
- Positive evaluation cases:
- Negative/adversarial cases:
- Deterministic checks:
- Independent-review requirements:
- Grounding/evidence requirements:
- Known limitations:

## Observability and data
- Required metrics:
- Audit events:
- Sensitive data processed:
- Retention requirements:
- Access restrictions:

## Readiness gate
- [ ] Role is non-duplicative and needed.
- [ ] Inputs/outputs and contracts are defined.
- [ ] Permissions and prohibited actions are explicit.
- [ ] Success/failure/escalation behavior is testable.
- [ ] Evaluation cases are reviewed.
- [ ] Dependencies and integration contracts are approved.
- [ ] Founder approves role classification and build order.
