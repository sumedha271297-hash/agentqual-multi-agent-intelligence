# Three-minute demo recording plan

1. 00:00–00:20 Explain the synthetic problem and architecture.
2. 00:20–00:50 Show the deterministic scoring code, labeled fixtures, and routing.
3. 00:50–01:20 Run `pytest -q` and `python -m scripts.evaluate`; explain the scope of these tests.
4. 01:20–01:50 Start `uvicorn app.api:app --reload`, open `/docs`, and call `/offline/run` for `c01` and `c02`.
5. 01:50–02:30 After installing LangGraph, call `/graph/run` for `c01` and `/graph/{thread_id}/approve` with `{"approved":true}`. `sent` stays false.
6. 02:30–03:00 Discuss gaps: real research API, LLM, independently labeled data, persistence, authentication, deployment.

Do not claim this recording exists until it is actually made.
