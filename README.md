# AgentQual — Stateful Lead Qualification with LangGraph

**Independent engineering portfolio demonstration. Not historical client software or a deployed production system.**

AgentQual is an intentionally bounded AI workflow showing how to build and test auditable qualification decisions, tool execution, checkpointed human approval, and optional provider-backed drafting.

## What is implemented

- **LangGraph**: research → ICP qualification → conditional routing → outreach draft → human approval interrupt.
- **Local research tool**: synthetic company lookup with bounded retry, typed record validation, and fail-closed routing.
- **Three execution modes**: deterministic offline baseline (no key required); optional OpenAI and Gemini structured draft generation with the corresponding API key, `llm_enabled: true`, and `llm_provider` set to `openai` or `gemini`.
- **Persistent state**: `PostgresSaver` with `DATABASE_URL`; in-memory saver for local development only.
- **REST API**: FastAPI run, inspect checkpoint, and approve/reject; no outbound email capability.
- **Tests**: unit, API, mocked LLM, LangGraph interrupt/resume, and PostgreSQL saver reopening.
- **Evaluations**: a deliberately rule-aligned synthetic baseline and a synthetic review-rubric disagreement dataset. Neither reflects production quality.

These graph stages are **not autonomous LLM agents**: only the outreach stage optionally calls an LLM, and all input data are synthetic.

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

The realistic next steps are permissioned research API integration, measured LLM factuality, independently annotated holdout data, authentication and authorization, distributed observability, cloud deployment, and a recorded demonstration. No such results are claimed here.

## Gemini setup

[Gemini provider setup](docs/gemini_setup.md) explains optional free-tier access, API key handling, and the explicitly gated live evaluation script. No live provider calls run in CI.
