# Company OS

- **Project type:** Founder-controlled, AI-operated online company platform
- **Documentation status:** Draft baseline — prepared before implementation
- **Current stage:** Phase 1 workforce-classification proposal; no application implementation
- **Agent count / role classification:** Proposed as 8 logical roles in `docs/17_AGENT_CLASSIFICATION.md`; founder approval is pending

## Vision

Company OS is intended to let its founder direct an online company through one control center while a coordinated AI workforce performs authorized digital work. The system should accept a goal or niche, research it, identify useful information and business opportunities, prepare and deliver digital outputs, manage prospective-customer conversations through compliant channels, and coordinate project delivery under the founder's policies.

The product is not just a chatbot or a static website. It includes an orchestration runtime, durable task execution, memory and evidence stores, external integrations, quality gates, a control dashboard, and operational safeguards.

## Documentation rules

1. These documents define requirements and proposed architecture. They do not authorize implementation beyond the current phase.
2. The exact number and classification of agent roles are proposed in `docs/17_AGENT_CLASSIFICATION.md`; the proposal is not approved until the founder explicitly accepts or revises it.
3. Work is sequential: do not advance to the next agent or work package while the current one has open blocking bugs, missing acceptance evidence, or unresolved required deliverables.
4. A feature is not complete because a model says it is complete. Completion requires observable evidence and passing acceptance criteria.
5. No system can guarantee perfect performance on every task. The engineering objective is measurable reliability, bounded execution, visible uncertainty, safe recovery, and independent verification.
6. Commercial outreach, calls, external publication, spending, contract acceptance, and production deployment are gated by permission and applicable law.

## Start here

Read in order:

1. [Project charter](docs/00_PROJECT_CHARTER.md)
2. [Product requirements](docs/01_PRODUCT_REQUIREMENTS.md)
3. [Architecture](docs/02_SYSTEM_ARCHITECTURE.md)
4. [Workflows and state machines](docs/03_WORKFLOWS_AND_STATE_MACHINES.md)
5. [Data model and memory](docs/04_DATA_MODEL_AND_MEMORY.md)
6. [Security, privacy, and governance](docs/05_SECURITY_PRIVACY_AND_GOVERNANCE.md)
7. [Agent runtime contract](docs/06_AGENT_RUNTIME_CONTRACT.md)
8. [Control-center UX](docs/07_CONTROL_CENTER_UX.md)
9. [API contract](docs/08_API_CONTRACTS.md)
10. [External integrations](docs/09_EXTERNAL_INTEGRATIONS.md)
11. [Testing and acceptance](docs/10_TESTING_AND_ACCEPTANCE.md)
12. [Operations and recovery](docs/11_OPERATIONS_DEPLOYMENT_AND_RECOVERY.md)
13. [Implementation roadmap](docs/12_IMPLEMENTATION_ROADMAP.md)
14. [Decision log and open questions](docs/13_DECISIONS_AND_OPEN_QUESTIONS.md)
15. [Requirements traceability](docs/14_TRACEABILITY_MATRIX.md)
16. [Company operating model](docs/15_COMPANY_OPERATING_MODEL.md)
17. [Glossary](docs/16_GLOSSARY.md)
18. [Agent workforce classification proposal](docs/17_AGENT_CLASSIFICATION.md)

Proposed role specifications (not approved/implemented): [`docs/agent-specs/`](docs/agent-specs/).

Reusable blank templates for future agent/capability and integration specifications are in [`docs/templates/`](docs/templates/). They do not override the proposed role specifications.

## Proposed baseline technology

The initial architecture recommendation is a TypeScript web frontend, Python API, PostgreSQL as the source of truth, an explicit durable worker mechanism, and a stateful agent-orchestration library. Local model execution should be supported through an adapter; hosted models can be optional later. Specific versions must be selected and locked during repository bootstrap after compatibility checks.

Technology names are implementation candidates, not a reason to change requirements to suit a framework. See the decision log before changing a baseline choice.

## Status and repository policy

This repository remains documentation-only. The proposed classification is documented but not yet founder-approved. Do not implement any role or enable external execution until the founder approves the classification and the repository roadmap prerequisites pass. Record meaningful changes in the decision log. Keep secrets, client personal data, call recordings, credentials, and real prospect lists out of Git.

## Official technical and governance references

- Next.js App Router: <https://nextjs.org/docs/app>
- Next.js deployment options: <https://nextjs.org/docs/app/getting-started/deploying>
- FastAPI background tasks and when to use a worker queue: <https://fastapi.tiangolo.com/tutorial/background-tasks/>
- LangGraph persistence: <https://langchain-ai.github.io/langgraph/concepts/durable_execution/>
- Ollama API, tool calling, and structured output: <https://github.com/ollama/ollama/blob/main/docs/api.md>
- OWASP GenAI / LLM application risks: <https://genai.owasp.org/llm-top-10/>
- TRAI UCC guidance: <https://www.trai.gov.in/what-spam-or-ucc>
- TRAI advice to telemarketers: <https://trai.gov.in/advice-telemarketers>
- TRAI advice to senders: <https://trai.gov.in/advice-to-senders>

Regulatory references are a starting point, not a legal opinion. Re-check official rules and the selected telecom provider's requirements immediately before enabling commercial calling or messaging.
