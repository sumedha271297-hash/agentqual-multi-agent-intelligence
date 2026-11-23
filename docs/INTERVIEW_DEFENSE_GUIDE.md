# AgentQual — Coinbase IC4-style Technical Defense Guide

**Use:** grounded practice for experienced engineering interviews. **Not** a representation of actual Coinbase interview questions or a claim of commercial/client production experience. Answers are conversational, targeted at approximately 20–40 seconds.

## 90-second project introduction

“I built AgentQual as an independent engineering demonstration of a stateful AI workflow. The baseline uses a local synthetic company lookup and deterministic ICP rules; optional model-backed stages can request an allowlisted tool, assess qualification with a structured response and draft outreach. LangGraph manages routing and a human-approval interrupt. I persisted checkpoints in PostgreSQL, added tenant-bound access checks, advisory locks and idempotent approval retry behavior, and deliberately did not implement outbound sending. I verified the code with 82 automated tests, an actual Compose restart/recovery exercise and a Chromium recording. The evaluation data is fictional; live-provider performance and public cloud operation are not verified.”

## Architecture and design

**1. Why LangGraph?**  
“Because the system is not simply a prompt call. It has explicit branches, a human interrupt, and resumption from durable state. LangGraph makes those transitions inspectable. I would not claim the deterministic baseline needs a multi-agent framework: a small state machine could do it. The benefit here is studying checkpointed workflows with optional model decisions.”

**2. Why not make every step an autonomous LLM agent?**  
“Research already resolves a known synthetic ID, and hard ICP constraints are deterministic. Making those calls autonomous adds cost and ambiguity. I kept model reasoning optional and limited tool execution to one allowlisted lookup. I would introduce more autonomy only after showing measurable gains against the deterministic baseline on truly reviewed examples.”

**3. Walk through an approved lead.**  
“The request is tenant-authenticated, research resolves the company record, qualification checks ICP criteria, and the outreach node produces a draft. LangGraph interrupts for a reviewer. On resume, the server checks thread ownership and serializes approval. The state becomes approved, but the sent flag remains false: approval means manual use, not automatic delivery.”

**4. What happens to rejected or ambiguous leads?**  
“Rule-based misses stop as rejected. When optional model reasoning returns REVIEW, the graph ends in needs_review with no draft and no approval interrupt. Provider exceptions are also mapped to a safe needs_review or failed route, rather than silently treating uncertain output as approved.”

## Reliability, state and security

**5. Why PostgreSQL checkpoints? What did you actually verify?**  
“The interrupt needs to survive process restarts. I used LangGraph’s PostgresSaver, then tested a pending approval through a real API container restart while PostgreSQL stayed running. The flow resumed afterward. That proves one restart/recovery scenario in ephemeral CI, not managed-cloud disaster recovery or five-nines availability.”

**6. How do two simultaneous approvals behave?**  
“Approvals for one thread are serialized with a PostgreSQL advisory lock in database mode. After acquiring it, the server reloads the checkpoint, validates tenant ownership and checks whether an interrupt remains. A matching idempotency UUID and decision can replay the durable response; conflicting approvals get 409. It doesn’t solve future exactly-once external messages.”

**7. How would you prevent a cross-tenant approval?**  
“The tenant is derived from the server-side API-key mapping, not a client-supplied tenant field. On checkpoint read or approval, require_owner checks the persisted tenant ID. Foreign or nonexistent thread IDs return 404. I verified this with actual HTTP probes against the Compose app.”

**8. What is your prompt-injection defense?**  
“I treat company descriptions as untrusted data, restrict model-requested tool names and arguments, and veto unsupported QUALIFY outputs using deterministic ICP constraints. Six mocked policy attacks passed. That only validates the application-level rules; it does not prove real models resist malicious data. A real-provider adversarial benchmark is the next gate.”

**9. What happens when the model provider goes down?**  
“The model-assisted paths fail closed; they don’t fabricate a successful result or switch secretly to a different decision. The workflow can return failure or needs_review and never sends a message. In production I’d add distributed retry budgets, alerting, circuit breakers and measured tail latency before scaling.”

## Measurement and judgment

**10. You reported an 87.5% F1: is that a credible model metric?**  
“No. That was deterministic matching over 40 fictional, explicitly authored scenario labels. The same companies appear in multiple policy splits, so it isn’t an independent company holdout. I use it to verify evaluation machinery and expose baseline disagreement, not to claim LLM accuracy or generalization.”

**11. What does 82 passing tests prove?**  
“That selected integration and policy behaviors are reproducible in the tested environment, including mock model edge cases and database recovery. It does not prove real-world model accuracy, end-to-end production correctness, or security against unseen attacks. The suite is evidence of engineering discipline, not a quality certificate.”

**12. Explain your load-test results.**  
“The smoke test sent 80 requests through an in-process FastAPI test client and recorded latency/throughput on one GitHub runner. That is useful as a regression signal only. I would not call it deployed throughput or make an SLO from it. Real capacity testing would require an instrumented private deployment, controlled traffic mix and steady-state load.”

**13. How did you decide what to log?**  
“I capture method, route template, status, per-request ID and elapsed time without token values, message bodies or raw UUID paths. The current metrics are process-local recent counters, so I’d replace them with distributed traces, structured redacted events, retention controls and alerting for an actual service.”

**14. What is the biggest weakness in the design?**  
“The optional model-based research step can be redundant when the ID and tool are already fixed. I would run an ablation against a deterministic pipeline: compare error reduction, human-review burden, cost and latency on independent reviewed scenarios. If the model doesn’t outperform the baseline, I’d remove it.”

**15. Could this serve actual Coinbase customers now?**  
“No. It is an independent portfolio demonstration with synthetic data, limited tenant bearer auth, no role model, rate limits, audited cloud infrastructure or factuality validation. A cloud release needs a threat model, managed secrets, identity integration, measured provider behavior and a formal release gate. I wouldn’t market this as production-ready.”

## Whiteboard challenges (practice without reading implementation)

**A. Add an outbox that guarantees no duplicate email dispatch after retries.**  
Discuss transactional insert with unique event ID, worker claim, idempotent delivery where supported, dead-letter handling, reconciliation. Explain why exactly-once is a system-level contract, not a lock.

**B. Add 100 parallel approvals across three API workers.**  
Discuss per-thread lock contention, DB connections, wait/timeout behavior, fair scheduling, correctness assertions and an idempotency key collision case. Define the test oracle before writing code.

**C. Demonstrate a forged company description.**  
Construct malicious instruction text as a field; show the model may misbehave, but tool-name and company-ID checks block unauthorized calls and a deterministic veto prevents one class of bad QUALIFY decision. Document residual risk.

**D. Design a live evaluation with a $5 budget.**  
Choose the cheapest suitable provider/model, capped cases/tokens, defined spend ceilings, 2 blind reviewers for factuality, a pre-registered scoring rubric, latency and token accounting, and an explicit stop condition. Run only with user-authorized available credits.

**E. Migrate to private cloud staging.**  
Outline TLS ingress, private DB, secrets manager, IAM, token rotation, audit logs, egress controls, scaling, health and rollback procedures. Distinguish staged tests from public operation.

## Defensive follow-up checklist

- Explain each API path and state field without looking at the README.
- Demonstrate why APPROVED never means SENT; identify exactly where adding sending would change the threat model.
- Distinguish test fixtures, model mocks, actual container execution and real provider responses.
- Describe one failure encountered while implementing CI and how the specific root cause was found.
- Name a capability intentionally **not** implemented, and justify the trade-off.
- Be transparent: this is **your independent portfolio work**, not evidence of prior customer deployment.

## Resume/portfolio-safe line

“Independent AgentQual demonstration — implemented stateful FastAPI/LangGraph qualification and checkpointed human approval with tenant-bound authorization, PostgreSQL restart recovery, concurrent-approval controls and bounded model-tool policies; verified via 82 tests and a real container/browser demonstration.”

**Before interview:** rehearse with a local run, understand every claimed design choice, and keep links to the exact passing GitHub Actions runs.
