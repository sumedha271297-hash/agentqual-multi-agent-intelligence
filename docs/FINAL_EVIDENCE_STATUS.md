# AgentQual — final verified evidence ledger (2026-11-24)

**Independent engineering portfolio demonstration, not a commercial deployment.**
This ledger distinguishes implemented code, passed tests, observed real-provider
results, and work that requires external parties or infrastructure.

## Verified completed work

| Gate | Verified outcome | Source |
|---|---|---|
| Automated Python suite | **102 passed** after synthetic factuality, prompt-injection and safe-retry additions | [CI 45261571202](https://github.com/sumedha271297-hash/agentqual-multi-agent-intelligence/actions/runs/45261571202) |
| Deployment-style rehearsal | Docker Compose staging, TLS on localhost, rate limiting, tenant denial, checkpoint recovery and backup/restore | [Staging 45261571293](https://github.com/sumedha271297-hash/agentqual-multi-agent-intelligence/actions/runs/45261571293) |
| UI proof | Real Chromium browser walkthrough interacting with app, with videos/screenshots as GitHub workflow artifacts | [Staging/browser evidence](https://github.com/sumedha271297-hash/agentqual-multi-agent-intelligence/actions/runs/45261571293) |
| Real Gemini connectivity | **1/1** synthetic company generated schema-valid structured draft using `gemini-3.5-flash-lite`; 1.73 s observed | [Live 1-case 45258253164](https://github.com/sumedha271297-hash/agentqual-multi-agent-intelligence/actions/runs/45258253164) |
| Real Gemini provider reliability | **3/3** synthetic company drafts schema-valid, median 4.42 s including retry delays; two initially 503 and recovered on second attempt | [Live 3-case 45260671524](https://github.com/sumedha271297-hash/agentqual-multi-agent-intelligence/actions/runs/45260671524) |
| Factuality/injection audit harness | Synthetic-only provider exercise + heuristic claim flags + separate human review packet; **mocked tests passed**, not human-validated factuality | [Methodology](FACTUALITY_EVALUATION.md), [CI](https://github.com/sumedha271297-hash/agentqual-multi-agent-intelligence/actions/runs/45261571202) |
| Blinded independent-review method | Produces unlabelled synthetic review packet and validates reviewer files; no independent reviewers have supplied decisions | [Protocol](INDEPENDENT_REVIEW_PROTOCOL.md) |
| Interview practice | Written and local self-practice assessment exists; no independent interviewer score or proof of candidate performance | [Assessment](TECHNICAL_ASSESSMENT.md) |

## Pending or not claimable

1. **Independent human factuality and qualification labels**: genuine reviewers
   have not provided ratings. Automated heuristics and synthetic rules are not
   independent ground truth.
2. **Live factuality red-team outcomes**: one authorized **four-case** evaluation
   was started in [run 45261904545](https://github.com/sumedha271297-hash/agentqual-multi-agent-intelligence/actions/runs/45261904545).
   Its final run report must be inspected before claiming any results. The
   one-time trigger was removed and the workflow is **manual-only again**.
3. **Real private-cloud service**: CI's temporary localhost deployment is not
   a hosted service with managed infrastructure, public DNS or production SLA.
4. **Interview performance**: user-owned interview readiness and external
   interview grading cannot be independently asserted from simulated practice.
5. **Commercial outcomes**: no actual client delivery, revenue improvement,
   production precision, or outbound sales messaging.

## Correct candidate-facing statement

> I built AgentQual as an independent FastAPI/LangGraph portfolio project,
> implementing deterministic and optional model-assisted qualification,
> structured Gemini drafting, PostgreSQL-backed human approval and checkpoint
> recovery, tenant-aware controls, retry boundaries and traceable testing.
> I verified 102 automated Python tests, a real browser and Compose staging
> walkthrough, and a successful three-company live Gemini smoke evaluation
> with 3/3 schema-valid drafts (two recovered from temporary HTTP 503 errors).
> The data is synthetic; this does not establish independent factual accuracy,
> a production cloud deployment, or real customer outcomes.

**Never claim** an externally reviewed accuracy score, production cloud
readiness, real outreach, or paid professional tenure on the basis of this work.
