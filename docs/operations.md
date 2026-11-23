# Operations and safety notes

## Local deployment with PostgreSQL
```bash
cp .env.example .env
docker compose --env-file .env up --build
```
The API listens on localhost:8000; PostgreSQL only listens on localhost:5432. This is a LOCAL demonstration and is unauthenticated; do not publish these ports.

`DATABASE_URL` enables PostgresSaver; `OPENAI_API_KEY` enables model-backed draft generation *only if request.llm_enabled=true*. No API key is required for deterministic baseline.

## Failure modes
- Provider failures never silently revert into an approved outreach message.
- No external message dispatch exists.
- POST /graph/{uuid}/approve returns 409 when approval is not pending.
- If PostgreSQL is unavailable on startup, startup fails rather than silently falling back to ephemeral memory.
- The graph checkpoint persists across API restarts, but authorization per thread and concurrency locking are not implemented.
- The model output is schema-constrained but grounding still needs adversarial and human quality tests.

## Production blockers
Authentication, tenant isolation, authorization per thread, rate limiting, encrypted secrets, detailed traces, durable idempotency, audit log retention and independent dataset evaluation are not implemented. Do not internet-deploy.
