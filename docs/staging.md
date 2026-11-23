# Staging deployment plan (NOT a deployed service)

Goal: run the service behind a TLS-terminating ingress with managed secrets,
private PostgreSQL, per-tenant auth and no outbound sending. This repository
does not contain cloud credentials or a public service URL.

## Preflight and local smoke

- Docker Compose binds the API and PostgreSQL to 127.0.0.1 by default.
- Use a long random tenant key (minimum 24 characters) in
  AGENTQUAL_TENANT_TOKENS, never in the repository.
- APP_ENV=production requires DATABASE_URL and tenant tokens.
- Use `docker compose config` and `docker compose up --build` locally.
- Run `python -m scripts.demo` to produce a real local graph/approval trace.
- Verify health 200; unauthorized /companies 401; foreign thread 404.
- Verify approval replay returns replayed=true and conflicting decision 409.
- Exercise PostgreSQL restart and restore from backup; stage is incomplete
  until externally observable metrics and logs are wired up.

## Remaining release blockers

No cloud deployment credentials are available. Rate limiting, proper
identity federation, role-based access, outbound filtering, backup/restore
evidence, distributed tracing, load-test evidence, and security scanning
are still required before any internet-facing staging deployment.

Do not expose the current service to the public internet.
