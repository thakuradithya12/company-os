# 09 — External Integrations

## 1. Integration principles

Third-party integrations are adapters behind explicit contracts. Each integration has a registered owner, purpose, scope, secret reference, data classification, rate and usage limits, retry behavior, side-effect classification, health check, and disable switch.

No integration should be enabled in production simply because its API key exists. The founder must be able to disable it without deleting task history.

## 2. Model providers

The model gateway should support a local provider (Ollama is the initial candidate) and optional hosted providers behind one application-level interface. A provider adapter must define:
- model ID and version/configuration;
- supported chat, tool calling, streaming, JSON-schema output, and embeddings features;
- context/output limits;
- timeout and retry policy;
- usage/cost accounting when available;
- data sent to provider and retention policy;
- fallback rules that do not silently change required quality or data residency.

If a model lacks reliable tool-calling or structured output for a role, the capability must not be enabled until a validated alternative is tested. Model names and configuration belong in environment/deployment configuration, not scattered hardcoded strings.

## 3. Web research and crawling

Use allowed public sources, documented APIs, RSS/feeds, and sites whose terms permit the intended access. Respect robots directives and rate limits where applicable, avoid login bypass, paywall evasion, CAPTCHA bypass, and collection of private information. Track source and retrieval times. Validate outbound URLs and prevent requests to internal/private network addresses to mitigate SSRF.

The research adapter should return structured source records rather than untrusted page text alone. It must identify fetch errors, stale pages, source conflicts, and incomplete extraction.

## 4. Website audit and development

Audit tools can inspect publicly reachable pages for availability, responsiveness, basic accessibility, metadata, performance indicators, broken links, and other clearly evidenced issues. Distinguish automated findings from subjective recommendations. Avoid intrusive scans, authentication bypass, vulnerability exploitation, or high-volume crawling without explicit authorization.

Generated sites should run in isolated development workspaces. Track source control commit, dependencies, build output, test output, preview address, and release approval. Deployment credentials must be mediated by the deployment integration and never provided directly to the model.

## 5. CRM and client communications

Communication integrations must support draft-before-send, provider-confirmed outcomes, duplicate prevention, suppression/opt-out enforcement, contact history, delivery state where available, and audit records. Store only necessary contact data. Outreach personalization must be based on verified business facts, not fabricated claims about the prospect.

## 6. Voice calling

Voice calling is a future gated integration. Select a provider that can lawfully support the intended outbound commercial calling mode and required registration, identity, consent/preferences, number series, suppression, recording/disclosure, retention, and audit requirements. Verify current Indian telecom regulations and the provider's written terms before implementation. Do not use a normal personal mobile number as a workaround for commercial telemarketing restrictions.

Required adapter behaviors include call eligibility check, approved script/version, human-like disclosure rules where legally/policy required, call start/finish status, provider call ID, failure/unknown outcome state, do-not-contact propagation, recording/transcript access control, and emergency stop. The system must not call when eligibility is unknown.

## 7. Email, messaging, and publishing

Before enabling sends, configure an authorized sending domain/provider, sender identity, bounce and complaint handling, rate limits, opt-out mechanisms where applicable, template review, and provider webhooks. Draft generation is separate from the send action. Publishing content to a public website or social platform uses the same approval pattern as outbound messages.

## 8. Payments, proposals, and signatures

The first release may prepare estimates and proposals but must not make purchases, transfer funds, or bind the company to a contract automatically. If payment/signature integrations are added later, use verified webhook signatures, clear transaction IDs, immutable status history, authorized limit checks, and founder approval for any action outside explicitly delegated bounds.

## 9. Integration lifecycle

`not_configured -> configured -> connection_verified -> policy_reviewed -> enabled_for_test -> enabled_for_production -> disabled/revoked`.

Every transition records the operator, environment, scope, test result, and date. Production enablement requires successful integration tests, permission review, rate/usage limit configuration, failure behavior, and disable/rollback procedure.
