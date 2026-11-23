# Coinbase IC4 candidate — engineering evidence and interview guide

This is an **independent personal engineering demonstration**, not historical freelance client delivery. Reviewers should verify source and CI before judging claims. No service is deployed publicly.

## Evidence map

| Claim you may make after CI passes | Where to inspect | Boundary |
|---|---|---|
| Implemented explicit stateful workflow routing | `app/graph.py` | Workflow nodes, not independently autonomous LLM agents |
| Tested interrupt and human resume | `tests/test_graph_integration.py`, `tests/test_api_graph.py` | No auto-send or reviewer UI |
| Tested durable recovery after DB reconnection | `tests/test_postgres_integration.py` | Does not prove cloud reliability |
| Added tenant-bound thread lookup and approval controls | `app/security.py`, `tests/test_security.py` | Shared tenant keys; no identity provider or concurrency locking |
| Implemented optional structured OpenAI/Gemini output | `app/llm.py`, `app/gemini.py` | Mock tests are not live-provider metrics |
| Added deliberately gated live evaluation | `scripts/evaluate_live.py`, GitHub Actions | No real API metrics until an approved run is executed |
| Reproducible offline baseline and review disagreement | `scripts/evaluate.py`, `scripts/evaluate_rubric.py` | Ten synthetic records; cannot infer real-world accuracy |
| Fail-closed research/LLM paths | `tests/test_resilience.py` | Synthetic failure injection, not uptime/SLO evidence |

## Interview narrative (no invented experience)

**Why use LangGraph?** The application needs explicit conditional transitions, resumable human approval, and checkpoint state. A single sequential prompt pipeline would obscure these constraints.

**What happens on tool failure?** Bounded retry for transient lookup errors, explicit terminal failure after exhaustion, and no outreach draft or external send.

**How is a reviewer protected?** Tenant identity is derived from a configured server-side API key, persisted with the graph state, and checked before inspecting/resuming a thread. Unknown and cross-tenant IDs both return 404.

**How did you evaluate?** Two synthetic rubric datasets; a deterministic baseline is perfect by construction, while an invented contextual reviewer exclusion produces a false positive. This demonstrates evaluation machinery, not model generalization.

**What would you improve for production?** Per-user identity and authorization, idempotent concurrent approvals, secret rotation, rate limits, independent blind labels, factual grounding tests, traces/cost tracking, and a staged cloud release with load testing.

## Suitable resume bullet (after verifying latest CI)
- Built an independent LangGraph + FastAPI demonstration with typed workflow state, conditional qualification routing, PostgreSQL-backed approval recovery, tenant-aware API checks, mocked provider tests and reproducible synthetic evaluation.

Do **not** present it as client-deployed, production-operated, autonomous multi-agent intelligence, or real-model performance evidence.
