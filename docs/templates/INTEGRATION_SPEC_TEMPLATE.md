# External Integration Specification — Template

## Identification
- Integration ID/name:
- Business purpose:
- Provider and product:
- Environments:
- Technical owner:
- Status:

## Contract
- API/webhook endpoints and version:
- Authentication method:
- Secret reference (never paste a secret here):
- Permissions/scopes granted:
- Input/output schemas:
- Webhook signature validation:
- Rate/usage limits:

## Data handling
- Data sent to provider:
- Data received:
- Personal/sensitive data classification:
- Storage/retention policy:
- Data residency/processing terms:

## Side effects and controls
- Side effects:
- Idempotency/reconciliation strategy:
- Required approvals:
- Duplicate handling:
- Opt-out/suppression behavior:
- Audit events:
- Emergency disable procedure:

## Reliability and security
- Timeouts/retries/backoff:
- Failure categories:
- Unknown-outcome handling:
- Health check:
- Test environment/sandbox:
- Threats and mitigations:
- Rollback plan:

## Acceptance criteria
- [ ] Contract is reviewed.
- [ ] Permissions are least privilege.
- [ ] Secrets remain outside code/logs/prompts.
- [ ] Failure and duplicate cases are tested.
- [ ] Privacy/retention and legal/provider requirements are checked.
- [ ] Disable/rollback is tested.
- [ ] Production enablement is approved.
