# Production-readiness assessment (candidate project)

## Verified locally
- Deterministic qualification baseline, API contract tests, and bounded local lookup tool tests.
- Tool adapter retries transient failures with exponential backoff and rejects invalid response shapes.
- No outbound messaging; approvals only release a draft for manual use.

## Not verified / not production ready
- LangGraph runtime could not be installed in the original offline environment; graph execution and interrupt/resume need integration tests in CI.
- In-memory checkpoints are not durable and are unsafe for multi-worker deployment.
- No authentication, rate limits, external provider integrations, actual LLM inference, or distributed tracing.
- No independent real-world evaluation dataset or external deployment.

## Release gates
1. Run CI with pinned dependencies and integration tests of interrupt/resume.
2. Replace memory checkpointing with persistent checkpoint storage, and test restart recovery.
3. Add authenticated endpoints, rate limiting, request IDs, audit logging, and secrets management.
4. Add optional LLM provider behind a typed interface; evaluate factual grounding and cost.
5. Load-test concurrency, document SLOs, deploy to staging, and record a live demo.

**Integrity:** Do not claim this system is production deployed or that the deterministic stages are autonomous LLM agents.
