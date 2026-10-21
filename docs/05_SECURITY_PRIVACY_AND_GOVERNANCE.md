# 05 — Security, Privacy, and Governance

## 1. Security objective

Prevent the workforce from exceeding its authority, exposing company/client data, running unsafe code on the host, or causing unreviewed external side effects. Security applies to prompts, memory, model output, integrations, generated code, and dashboard controls.

## 2. Threat model

Threats include:
- prompt injection in web pages, emails, documents, code repositories, or tool results;
- fabricated or malformed model output accepted by an API or workflow;
- a compromised/over-permissioned integration token;
- cross-user/client memory retrieval;
- unsafe generated code or shell execution;
- secret leakage into prompts, logs, artifacts, or Git;
- duplicate messages/calls caused by retries or uncertain provider outcomes;
- a misleading dashboard that displays mock or stale status as real;
- an agent attempting unapproved pricing, contract, publishing, spending, or deployment actions;
- denial of service, runaway loops, unbounded web crawling, or provider-cost spikes;
- malicious or manipulative instructions supplied by prospective clients or external sources.

Use the current OWASP GenAI / LLM security guidance as a living input to threat reviews. Relevant topics include prompt injection, improper output handling, sensitive-data disclosure, supply-chain issues, excessive agency, overreliance, and unbounded consumption.

## 3. Identity and authorization

- Require authentication for all private control-center routes and API endpoints.
- Apply server-side authorization to every protected operation; hiding a button is not authorization.
- Use least-privilege roles and resource scopes.
- Require MFA for production founder/operator access where supported.
- Use secure, HttpOnly, appropriately SameSite cookies or a documented equivalent secure session strategy; protect state-changing requests against CSRF.
- Expire sessions and support revocation.
- Rate-limit login, sensitive endpoints, user-provided task creation, and expensive operations.
- Restrict service-to-service credentials and rotate them when exposure is suspected.
- Treat agent identities as service principals with limited scopes, not as administrators.

## 4. Tool permission model

Every tool declares:
- tool ID and version;
- input/output schema;
- allowed roles/capabilities;
- required user/operator permission;
- resource and data scope;
- whether it can produce an external side effect;
- idempotency/reconciliation rules;
- timeout and resource limits;
- logging/redaction requirements;
- approval requirement and risk class.

The runtime must enforce this registry outside the model. A model's claim that an action is safe or approved has no authorization effect. Tools must reject unknown fields where practical and validate argument values before execution.

## 5. Risk tiers and approval gates

- **Tier 0 — Read-only internal:** retrieval, analysis of authorized internal materials, task planning.
- **Tier 1 — Reversible internal writes:** draft artifacts, task notes, non-public project changes in a controlled workspace.
- **Tier 2 — External communication/publication:** outbound email, business messaging, voice calls, public content publication, prospect follow-up.
- **Tier 3 — Financial/legal/production impact:** quote acceptance, contract signature, payment, purchasing, domain/DNS changes, production deployment, destructive actions, broad customer data changes.

The specific action catalog must assign exact tiers during implementation. Default-deny all external side effects until the integration and approval gates are signed off. Tier 2 and Tier 3 actions require explicit configured policy and should require approval unless the founder has granted narrowly bounded delegation. Tier 3 actions should remain founder-approved in the initial release.

## 6. Prompt injection and untrusted data

- Mark external content and tool output as untrusted data, never as system policy.
- Do not allow text inside a retrieved page or file to change permissions, tool allowlists, system instructions, or approval rules.
- Keep system/developer instructions, user objectives, source excerpts, and tool results structurally separated where supported.
- Validate output schemas and independently validate proposed tool arguments.
- Sanitize/render user content safely; do not execute arbitrary HTML, JavaScript, shell snippets, or generated code in the control plane.
- Require source-aware retrieval and allowlisted network access for production research jobs.
- Test adversarial inputs as part of the release gate.

## 7. Generated code isolation

Generated code and third-party artifacts must run in disposable isolated environments. Require non-root execution, resource ceilings (CPU, memory, process count, disk), bounded runtime, restricted network, controlled filesystem mounts, no host Docker socket, no cloud credentials, no production secrets, and forced cleanup after exit/failure. Never enable arbitrary participant/customer code execution until the isolation implementation has evidence-backed tests and a separate release gate.

## 8. Secret management

- Do not commit secrets, `.env` files, provider keys, phone numbers used as credentials, session tokens, or passwords.
- Commit only `.env.example` with placeholders.
- Keep secrets in environment configuration or an approved secret manager; use separate credentials per environment.
- Redact secrets from logs and model prompts.
- Maintain a credential rotation and incident response procedure.
- Ensure agents cannot read deployment secrets unless the specific integration requires access, and then expose only a narrow tool operation rather than the secret itself.

## 9. Privacy and retention

- Collect only data necessary for an explicit task and lawful purpose.
- Prefer company-level and public business information; do not harvest private or sensitive personal data.
- Record the source and purpose for contact details and contact eligibility.
- Provide suppression/opt-out enforcement for outreach.
- Set retention periods for messages, transcripts, task traces, source extracts, artifacts, and audit records.
- Restrict call transcripts/recordings and customer messages to authorized staff and tasks.
- Do not use customer data for unrelated cross-client learning without a reviewed basis and appropriate controls.
- Support deletion/correction procedures without corrupting the integrity of required audit records.

## 10. Voice calling and commercial communications in India

**Outbound calling must remain disabled by default.** TRAI's official UCC page states that unsolicited commercial communication can include voice calls and discusses consent, recipient preferences, registered senders, and the risks of using ordinary ten-digit numbers for commercial communication. TRAI also publishes guidance for senders and telemarketers. Before enabling calls or messages, verify the latest applicable regulations, amendments, sender/telemarketer registration, numbering-series requirements, consent/preference obligations, time restrictions, identification/disclosure, opt-out handling, provider obligations, and recordkeeping with an authorized telecom provider and qualified adviser.

Official reference starting points:
- <https://www.trai.gov.in/what-spam-or-ucc>
- <https://trai.gov.in/advice-telemarketers>
- <https://trai.gov.in/advice-to-senders>
- <https://trai.gov.in/release-publication/regulations/amendments-page/7617>

These pages are not a substitute for a current legal check. TRAI's regulations index lists a Third Amendment dated 18 September 2026; the actual amendment text and implementation status must be reviewed before enabling the feature. Regulations and provider requirements can change. Do not connect a personal ten-digit SIM to an automated commercial calling campaign. The product must store eligibility checks, provider IDs, required disclosures, opt-outs, and call outcomes before calls can be enabled.

## 11. Auditability

Audit events should cover login/security changes, role/permission changes, tool calls with side effects, approvals and rejections, policy changes, data exports/deletions, external communications, deal changes, production deployments, and emergency-stop actions. Use append-only records with access control and retention. Do not log more personal content than necessary.

## 12. Incident handling

1. Stop or restrict the affected integration/worker.
2. Preserve necessary audit evidence without copying exposed secrets into new locations.
3. Revoke/rotate affected credentials.
4. Determine affected tasks, data, customers, and external side effects.
5. Notify the founder/operator and follow applicable reporting obligations.
6. Fix the root cause and add a regression test.
7. Re-enable only after the release gate passes.

## 13. Security acceptance criteria

Production is blocked by any unresolved critical/high finding, missing authorization checks, exposed secret, unbounded execution path, untested emergency stop, inability to suppress outreach, public access to internal services, or claims of isolation without test evidence.
