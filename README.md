# AgentQual — LangGraph Lead Intelligence Workflow

**Independent candidate portfolio demonstration | not a historical client deliverable**

A Python/FastAPI application demonstrating explicit graph orchestration, stateful routing, a local company lookup tool, transparent ICP qualification, grounded outreach drafting, and resumable human review. **The current system uses deterministic logic and synthetic data, not LLM calls.** Its LangGraph nodes are specialized workflow stages, not autonomous LLM agents.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
pytest -q
python -m scripts.evaluate
uvicorn app.api:app --reload
```

Open http://127.0.0.1:8000/docs for API documentation.

## Offline baseline

```bash
curl -X POST http://127.0.0.1:8000/offline/run -H 'Content-Type: application/json' -d '{"company_id":"c01","icp":{"industries":["SaaS","Fintech"],"min_employees":20,"max_employees":300,"regions":["US"]}}'
```

## Graph + approval

POST the same JSON to `/graph/run`. A qualified company pauses at the review interrupt. Then POST `{"approved":true}` to `/graph/THREAD_ID/approve`. No messages are sent: human approval only releases a draft for manual use.

## Evaluation

`python -m scripts.evaluate` creates `reports/evaluation.json`. The ten synthetic examples have intentionally rule-aligned labels. Perfect accuracy is **not** evidence of model generalization. No LLM quality or external provider success metrics are claimed.

## Docker

```bash
docker build -t agentqual .
docker run --rm -p 8000:8000 agentqual
```

Cloud deployment has not been performed. Checkpoints are in-memory and API endpoints are unauthenticated; never expose them publicly without security controls.

## Contents

- `app/core.py`: rule-based qualification baseline and grounded recommendation generation
- `app/tools.py`: bounded local lookup tool with retries and validation
- `app/graph.py`: LangGraph StateGraph, conditional routing, interrupt
- `app/api.py`: FastAPI run/resume endpoints
- `data/`: synthetic company fixtures and labels
- `scripts/evaluate.py`: reproducible baseline metrics
- `tests/`: deterministic, edge, tool, API tests
- `docs/`: architecture, demo plan, readiness assessment
- `.github/workflows/ci.yml`: unit tests and evaluation in CI

## Remaining engineering gates

1. Verify LangGraph run/pause/resume in GitHub CI with real integration tests.
2. Add permissioned research API and an optional LLM adapter with structured outputs.
3. Create a truly independently labeled evaluation dataset.
4. Use persistent Postgres checkpoints and add authentication and instrumentation.
5. Stage, load-test, deploy and record a reproducible demonstration video.

**Integrity note:** This is candidate project work, not client-delivered software or an operated production service. Do not describe its deterministic graph stages as autonomous LLM agents.
