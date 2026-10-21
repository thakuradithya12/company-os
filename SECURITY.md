# Security Policy

## Scope

Company OS will coordinate AI agents that can read information, create artifacts, call tools, and later interact with external people and systems. Security bugs that enable unauthorized access, secret disclosure, unintended external action, unsafe execution, or cross-customer data access are high priority.

## Reporting

Do not publish credentials, personal data, call recordings, or exploit details in public issues. Report a suspected vulnerability privately to the repository owner/operator using an explicitly configured private channel. A reporting address will be added before public release; do not invent or assume one exists today.

## Development requirements

- Do not commit real secrets or production/client data.
- Include reproduction steps and impact in security reports.
- Preserve evidence carefully and avoid destructive testing against live systems.
- Do not enable outbound calling, financial actions, public deployment, or arbitrary code execution before the relevant security gates pass.
- All security fixes require regression tests and re-review of related permission boundaries.

## Release policy

Production must not be released with unresolved critical security defects, exposed credentials, bypassable authorization, unsafe host-level code execution, untested external-action gating, or false claims about sandbox enforcement.
