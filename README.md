# AgentQual — Stateful Lead Qualification with LangGraph

**Independent engineering portfolio demonstration. Not historical client software or a deployed production system.**

AgentQual is an intentionally bounded AI workflow showing how to build and test auditable qualification decisions, tool execution, checkpointed human approval, and optional provider-backed drafting.

## Start here — verified candidate package

- **[Recruiter-facing case study + current architecture diagram](docs/PORTFOLIO_CASE_STUDY.md)**
- **[Challenge-first engineering architecture review](docs/ARCHITECTURE_REVIEW.md)**
- **[Interview defense guide and whiteboard exercises](docs/INTERVIEW_DEFENSE_GUIDE.md)**

Latest confirmed baseline (commit `3aae87c1`): **82 tests passed** in [Python CI](https://github.com/sumedha271297-hash/agentqual-multi-agent-intelligence/actions/runs/45243287837), and [Docker Compose staging plus genuine Chromium browser recording](https://github.com/sumedha271297-hash/agentqual-multi-agent-intelligence/actions/runs/45243288064) passed. Recordings are workflow artifacts. This is **synthetic-data independent portfolio work**, not customer delivery, verified real LLM performance, or a public deployment.

## Final candidate validation gates (2026-11-24)

**Latest verified outcome:** 88 passing tests and a [successful production-mode localhost TLS/rate-limit/PostgreSQL backup-and-restore rehearsal](https://github.com/sumedha271297-hash/agentqual-multi-agent-intelligence/actions/runs/45248497792). [Evidence status and explicit gaps](docs/FINAL_EVIDENCE_STATUS.md).

- [Blinded independent-review packet and adjudication protocol](docs/INDEPENDENT_REVIEW_PROTOCOL.md). Code checks format and distinct reviewers; **no actual outside reviewer labels have been supplied or claimed**.
- [Production-style localhost TLS, ingress rate limit and real Postgres backup/restore drills](docs/PRODUCTION_REHEARSAL.md). CI uses disposable secrets and a self-signed localhost certificate, not an actual private cloud.
- [Unscored, hands-on technical interview assessment](docs/TECHNICAL_ASSESSMENT.md) with `python -m scripts.practice_defense`; the candidate must personally submit answers before anyone can claim the practice was completed.
- Real Gemini model evaluation succeeded: [3 of 3 synthetic drafts had valid schema](https://github.com/sumedha271297-hash/agentqual-multi-agent-intelligence/actions/runs/45260671524), with two HTTP 503 recoveries. No independently reviewed factual accuracy is claimed. [Current canonical evidence ledger](docs/FINAL_EVIDENCE_STATUS.md).

## Final verified snapshot (2026-11-24)

- **102 automated tests passed**: [Python CI](https://github.com/sumedha271297-hash/agentqual-multi-agent-intelligence/actions/runs/45261571202).
- **Latest real staging/browser workflow passed**: [verification](https://github.com/sumedha271297-hash/agentqual-multi-agent-intelligence/actions/runs/45261571293).
- **Gemini 3.5 Flash-Lite real provider evaluation: 3/3 schema-valid drafts** on fictional company inputs, including recovery from two HTTP 503 provider errors: [run](https://github.com/sumedha271297-hash/agentqual-multi-agent-intelligence/actions/runs/45260671524).
- **Synthetic-only factuality and prompt-injection triage** with human review packet: [methodology](docs/FACTUALITY_EVALUATION.md). Do not describe heuristic flags as factuality accuracy.
- **Remaining external evidence**: independent human labels, actual cloud hosting and genuine real-world customer outcomes are not established.

## What is implemented

- **LangGraph**: research → ICP qualification → conditional routing → outreach draft → human approval interrupt.
- **Local research tool**: synthetic company lookup with bounded retry, typed record validation, and fail-closed routing.
- **Three execution modes**: deterministic offline baseline (no key required); optional OpenAI and Gemini structured draft generation with the corresponding API key, `llm_enabled: true`, and `llm_provider` set to `openai` or `gemini`.
- **Persistent state**: `PostgresSaver` with `DATABASE_URL`; in-memory saver for local development only.
- **REST API**: FastAPI run, inspect checkpoint, and approve/reject; no outbound email capability.
- **Tests**: unit, API, mocked LLM, LangGraph interrupt/resume, and PostgreSQL saver reopening.
- **Evaluations**: a deliberately rule-aligned synthetic baseline and a synthetic review-rubric disagreement dataset. Neither reflects production quality.

These graph stages are **not autonomous LLM agents**: only the outreach stage optionally calls an LLM, and all input data are synthetic.

## Advanced reliability and agentic research (experimental)

- `app/approval_lock.py`: serializes human approval by thread using PostgreSQL session advisory locks (in-memory stripes in local-only mode). Correctness relies on all writers using the same protocol.
- `Idempotency-Key: <uuid>` on POST `/graph/{thread_id}/approve` supports safe replay of the **same decision** after a successful checkpoint commit; conflicting keys/decisions return 409.
- Optional `"agentic_research": true` on POST `/graph/run` enables model-directed tool selection using an OpenAI model and `OPENAI_API_KEY`. The only executable tool is `company_lookup`; calls are validated and bound to the authorized company ID. This costs API credits and is **off by default**.
- The qualification stage remains rule-based. These are bounded, role-specific workflow stages, **not** a fully autonomous multi-agent team.
- Tests cover concurrent retry safety, conflicting approvals, invalid tool calls, and cross-record tool access. CI runs without provider charges.

Architecture decisions: [approval locking](docs/adr/0001-approval-serialization.md) and [bounded model tool calls](docs/adr/0002-bounded-model-tool-calls.md).

## Verified 2026-11-23 engineering milestone

GitHub CI (commit `4ac10aa12ff5d03dfb666656ab3fc5ea90426aa2`) passed **75 automated tests** and executed two reproducible evidence programs:

- `python -m scripts.evaluate_v2` measures a **frozen 40-case fictional matrix** with explicit simulated reviewer labels and reports splits and errors. 87.5% overall F1 is a synthetic, rules-based test result, NOT LLM accuracy or independent real-world performance.
- `python -m scripts.demo` invokes the actual offline LangGraph graph with two fictional profiles. It verifies approval pause/resume and safe rejection. The corresponding report is available as an artifact in the [successful GitHub Actions run](https://github.com/sumedha271297-hash/agentqual-multi-agent-intelligence/actions/runs/45236305886).

Optional `agentic_qualification: true` enables schema-constrained model reasoning with QUALIFY, REJECT and REVIEW outcomes. A deterministic ICP policy vetoes unsupported QUALIFY judgments. This feature is tested with mocked model output, not live inference. It requires `OPENAI_API_KEY` when used for real calls.

A localhost-only rehearsal configuration is provided at [deploy/staging.compose.yml](deploy/staging.compose.yml). It **was verified in GitHub Actions with actual Compose containers and PostgreSQL restart recovery**; it remains **not a cloud deployment** and is not safe for internet exposure without additional controls.

See [evaluation methodology v2](docs/evaluation_v2.md), [demo instructions](docs/demo.md), [staging plan](docs/staging.md), and [ADR 0003](docs/adr/0003-constrained-qualification-reasoning.md).

## Local reviewer demo, adversarial checks and load smoke

The local browser interface at **http://127.0.0.1:8000/demo** works with
`uvicorn app.api:app --host 127.0.0.1 --port 8000`. It executes the
actual FastAPI + LangGraph request paths on fictional data. Click Run,
Inspect, and Approve/Reject. It does not store keys in browser storage,
is not available in `APP_ENV=production`, and is restricted to loopback
clients. Never expose the development application to the public internet.

`python -m scripts.security_matrix` runs six mocked adversarial policy
exercises. `python -m scripts.performance_smoke` measures 80 concurrent
in-process HTTP requests (8 workers) and records p50/p95 latency,
observed throughput, and failures. They are automated in CI with
per-run reports. **Neither is a real-model jailbreak benchmark or a
staging/production capacity test.**

See [security and performance methodology](docs/security_performance.md).
A genuine local Chromium browser screen recording is available in the [verified Actions artifact](https://github.com/sumedha271297-hash/agentqual-multi-agent-intelligence/actions/runs/45243288064). Independently validated live-provider factuality assessment is still outstanding.

## Running locally

```bash
python -m venv .venv
source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
python -m pytest -q
python -m scripts.evaluate
python -m scripts.evaluate_rubric
uvicorn app.api:app --reload
```

The API docs are at http://127.0.0.1:8000/docs. Example request to `POST /graph/run`:

```json
{
  "company_id": "c01",
  "icp": {
    "industries": ["SaaS", "Fintech"],
    "min_employees": 20,
    "max_employees": 300,
    "regions": ["US"]
  },
  "llm_enabled": false
}
```

Qualified leads pause for review and return a `thread_id`. Then send `{"approved":true}` or `{"approved":false}` to `POST /graph/{thread_id}/approve`. The graph will never automatically send messages.

For a local PostgreSQL-backed API:

```bash
cp .env.example .env
docker compose --env-file .env up --build
```

**Do not expose this demo publicly.** Basic API-key tenant isolation is present, but it lacks other production controls. PostgreSQL persistence is a demonstrated architecture and must be verified by CI before claiming a successful tested integration.

## Evaluation

`python -m scripts.evaluate` is a basic self-consistency check over ten synthetic records with rules-aligned outcomes; do **not** present its perfect score as a measured model achievement.

`python -m scripts.evaluate_rubric` compares the same rule decisions against a synthetic analyst-style rubric with one deliberate contextual disagreement. Expected metrics are 0.75 precision, 1.00 recall, and approximately 0.857 F1, strictly on this illustrative toy dataset. The contextual label is not a real analyst annotation.

See [evaluation methodology](docs/evaluation_methodology.md) and [operations and limitations](docs/operations.md).

## Candidate portfolio evidence

- [Architecture and trust boundaries](docs/architecture.md)
- [Review-rubric evaluation methodology](docs/evaluation_methodology.md)
- [Operational and deployment limits](docs/operations.md)
- [GitHub Actions workflow](.github/workflows/ci.yml)
- [Demo recording outline](docs/demo_script.md)

The realistic next steps are permissioned research API integration, measured LLM factuality, independently annotated holdout data, per-user authorization, distributed observability, and secure cloud deployment. A real local browser recording and ephemeral staging verification are already documented; no public deployment or live-model metrics are claimed.

## Gemini setup

[Gemini provider setup](docs/gemini_setup.md) explains optional free-tier access, API key handling, and the explicitly gated live evaluation script. No live provider calls run in CI.
