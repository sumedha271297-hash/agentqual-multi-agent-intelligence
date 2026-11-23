# AgentQual — Engineering Design Review (challenge-first)

**Scope:** A code-grounded review of commit `3aae87c1`, not a security certification or statement that Coinbase uses these requirements. Severity denotes engineering priority before a public release.

## Executive assessment

The system is a **stronger-than-toy integration demonstration** with explicit workflow routing, real PostgreSQL checkpoint restart evidence, bounded tool execution, tenant isolation and a real UI walkthrough. It is **not ready for public production traffic**. The best interview narrative is how risks were bounded and which defenses are intentionally missing.

| Priority | Weakness / credible interviewer challenge | Code-grounded observation | Recommended resolution and proof |
|---|---|---|---|
| P0 | Public exposure and abuse control | `app/security.py` maps static bearer tokens to tenants. No user identity, roles or rate limiter; local UI is disabled in production. | OIDC user+tenant identity, scoped roles, rotation, strict request size/concurrency/time budgets, abuse tests and externally reviewed threat model. |
| P0 | Factuality of model drafts | `app/llm.py` enforces Pydantic **shape**, but does not independently verify assertions against evidence. | Field-level grounded-claim validator, citations to source facts, high-risk assertion abstention, human-reviewed unsupported-claim benchmark. |
| P0 | External side effects are not exactly-once | `app/graph.py` never sends messages; `app/approval_lock.py` guards approval only. | If sending is ever added, transactional outbox, delivery idempotency, retries and reconciliation; do not reuse approval locking as sending guarantee. |
| P1 | API shape and authorization boundaries | `/companies` returns all fictional companies to any authenticated tenant; `/metrics` returns process-wide counts. Thread ownership is checked on read/approve. | Define tenant-scoped data domains and permission tests; separate admin metrics; deny global collection access where tenants have private records. |
| P1 | Observability is process-local | `app/observability.py` counts routes and samples recent latencies in memory. No distributed traces, incident alerts, audit retention, or model costs. | Correlated workflow spans, anonymized structured events, sampled model tokens/costs, error budgets and alarms; validate with incident drill. |
| P1 | Agent architecture may be unnecessary | Model-directed research permits one allowlisted lookup; deterministic baseline already knows the company ID. | A/B compare deterministic vs optional model-assisted qualification on independently labeled ambiguous cases; keep ML only if quality gain justifies cost/risk. |
| P1 | Reliability is not load tested | In-process smoke test gives runner-only latency; ephemeral Compose verifies request paths and API restart. | Multi-instance private staging, scaled Postgres connections, steady/concurrent load, backpressure and chaos tests with recorded infra config. |
| P1 | Multi-worker and lock protocol | Postgres session advisory locks use a separate DB connection; all writers must follow the same protocol, with 2s acquisition deadline. | Concurrent multi-process PostgreSQL test, lock timeouts, network interruption, connection pool bounds; consider transactional state machine constraints. |
| P1 | Model-output prompt injection | `app/reasoning.py` says descriptions are data, but instructions alone are not a strong isolation boundary. Guardrail vetoes some unjustified positives. | Real-provider adversarial corpus, escaped/isolated tool evidence, evaluate malicious descriptions, monitor abstention and unsupported claims. |
| P2 | Strict reviewer schema / input validation | `app/core.py:validate_draft` checks basic types and `requires_approval`; `app/llm.py` has tighter Pydantic lengths only for OpenAI. | Harmonize schemas across offline/OpenAI/Gemini, reject unknown/untrusted fields, test downstream rendering and safety invariants. |
| P2 | Documentation freshness | README's original 'no live video' and 'unverified staging' statements became outdated after the successful CI run. | Maintain evidence-index with commit/run links, automate release summary, avoid incompatible claims in different docs. |

## Hard technical trade-off questions

### Why LangGraph instead of a simple function?
The interrupt/resume and conditional routing requirements make stateful orchestration attractive; on the default deterministic path a plain state machine could still be simpler. We should benchmark complexity/operational cost and retain LangGraph only if human-review persistence justifies it.

### Does idempotency mean exactly-once?
No. Approval replay is keyed to a UUID and persisted checkpoint state for **this particular operation**, after a lock. It does not guarantee exactly-once network delivery, nor atomic completion across future external systems.

### Is the model the decision maker?
Only when explicitly enabled and paid for; its QUALIFY result is vetoed by deterministic ICP mismatch and REVIEW ends without draft. A model can still reject a valid deterministic candidate; evaluate the cost of false negatives.

### Did staging prove cloud readiness?
No. Compose ran with production-mode configuration in GitHub Actions and actual TCP HTTP assertions; TLS termination, managed secrets, multi-zone failover, a public endpoint, sustained workloads and external auditing were not demonstrated.

### How would you evaluate risk systematically?
Create a threat model (assets: tenant keys, drafts, checkpoint history; threats: unauthorized cross-tenant data, prompt injection, replay, resource exhaustion), assign ownership and abuse budgets, then turn each threat into negative CI tests and staging attack probes.

## 30/60/90 day design evolution (hypothetical roadmap, not executed history)

- **0–30:** threat model + tenant data boundaries + user/role access; independent offline evaluation dataset; schema parity across providers; safer model factuality controls.
- **31–60:** private cloud staging with TLS/managed secrets and external observability, concurrent multi-worker test and dependency/container scanning.
- **61–90:** controlled live provider benchmark, comparative baseline study, staged load/chaos tests, readiness review. Add customer data or sending only with consent and clear business need.

## Review verdict

**Portfolio-readiness:** strong if explained transparently and demonstrated live.  
**Security/production-readiness:** not established.  
**Evidence completeness:** offline workflow and staging recovery yes; real model inference and externally validated results no.  
**Priority issue to defend:** whether the added model/agent orchestration improves the deterministic problem sufficiently to justify complexity.
