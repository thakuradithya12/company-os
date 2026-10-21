# 07 — Control-Center UX Specification

## 1. UX objective

Give the founder one calm, readable, operational view of the company. The interface must prioritize real status and high-value controls over decorative AI imagery, fake activity, or excessive dashboard cards.

## 2. Navigation domains

The final navigation layout can be refined during UI design, but the following product domains must be reachable:

1. **Overview:** current work, alerts, approvals, service health, and recent completed deliverables.
2. **Company Chat:** submit objectives, inspect the generated plan, clarify scope, and view the final report.
3. **Work Queue:** tasks, status, dependencies, owner/capability, attempts, priority, deadlines, and filters.
4. **Workforce:** registered role/capability definitions, enabled state, limits, and recent performance. The list is populated only after the agent classification phase.
5. **Research & Knowledge:** niches, research projects, sources, evidence, reports, publishing status, and memory review.
6. **Opportunities / CRM:** business records, website audits, qualification, contact eligibility, communication timeline, and suppression status.
7. **Deals:** requirements, proposals, price/discount limits, approval state, agreements, and recorded outcome.
8. **Projects:** project brief, milestones, deliverables, test results, previews, and delivery approvals.
9. **Approvals:** exact actions waiting for founder decision, with approve/reject/edit or cancel where supported.
10. **Memory & Procedures:** scoped memory items, provenance, version history, correction, expiry, and curated procedures.
11. **Audit & Diagnostics:** searchable events, task traces, error details, provider/queue health, and incident references.
12. **Settings:** integrations, model/provider policy, global resource limits, roles, security, retention, and environment information.

## 3. Overview page

Required live metrics should include:
- queued/running/blocked/awaiting-approval/completed/failed task counts;
- active worker and provider health;
- approvals requiring attention;
- recent failures with direct links to traces;
- current usage/cost where available;
- last successful backup and most recent restore-test status;
- external communication integration state and safety gate state.

Do not display “online” or “healthy” merely because the page loaded. Show the underlying check and last-updated time. If data is stale or unavailable, label it stale/unavailable.

## 4. Task detail page

Required content:
- objective and requester;
- plan and dependency graph;
- acceptance criteria and status for each check;
- current state, attempt, worker/capability version, start time, elapsed time, deadline, and resource limit;
- timeline of state changes;
- input and output artifacts;
- sources/evidence and verification details;
- tool calls with risk labels, permission decision, safe argument summary, and result;
- failure diagnostics and retry/cancel controls;
- pending approvals and their exact scope.

Secrets and unnecessary personal data must be redacted. Raw prompts/transcripts should be access-controlled.

## 5. Company chat behavior

- Clarify only material ambiguities; do not repeatedly ask for details already provided.
- Before costly or externally visible work, show an understandable plan and ask for approval when policy requires it.
- Clearly distinguish a proposal, a task accepted for execution, an in-progress task, and a verified result.
- Offer progress based on persisted events, not fabricated natural-language updates.
- Show source links, artifacts, test results, caveats, and follow-up decisions in the final report.

## 6. Interaction controls

Every command/control must have:
- a clear label and effect;
- disabled state when preconditions do not hold;
- confirmation for destructive or high-impact actions;
- server-side permission enforcement;
- visible success/failure based on backend response;
- audit record for privileged operation;
- accessible keyboard/focus behavior.

The Stop Company control must state whether it stops new dispatch only, requests worker cancellation, blocks external side effects, or includes all three. The implementation must match the label.

## 7. Visual direction

- Professional, restrained visual language; clear typography and spacing.
- Strong hierarchy for tasks and alerts; no excessive gradients, generic AI motifs, or unnecessary animated backgrounds.
- Use tables and detail views where operators need precision.
- Keep status colors and labels consistent, accessible, and not color-only.
- Provide responsive layouts without hiding critical controls on small screens.
- Prefer honest empty states over invented example activity in production.

## 8. Accessibility and usability checks

Keyboard navigation, focus visibility, screen-reader labels for icon buttons, contrast, form error messages, responsive scaling, table overflow behavior, loading/error/empty states, and confirmation for irreversible actions must be tested.

## 9. Live update and stale-data behavior

Live events are delivered over WebSocket/SSE, but they are notifications, not canonical state. On reconnect the client fetches the persisted state. Each view displays a last-updated timestamp and signals stale/disconnected state. Out-of-order events must not regress a task's state.
