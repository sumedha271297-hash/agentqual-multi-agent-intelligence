# Security controls and limitations

## Implemented
- Server resolves tenant identity from API key; client does not supply a tenant selector.
- Tenant identity is persisted in the LangGraph checkpoint.
- GET /graph/{id} and POST /graph/{id}/approve verify owner before disclosing state or resuming.
- Unknown and foreign thread IDs both return 404.
- Production startup fails unless tenant tokens and DATABASE_URL exist.
- API-key comparisons use secrets.compare_digest.
- /metrics and /companies require authentication once tokens are configured.
- Logs include request ID, route template, response status and duration; they exclude token and raw company profile.
- No automatic messaging capability exists.

## Configuration
`AGENTQUAL_TENANT_TOKENS` is a secret JSON object e.g. `{"demo":"<24+-character random secret>"}`.
Set `APP_ENV=production`, `DATABASE_URL`, and the secret map via a secrets manager.
In development with no tokens the local demo remains unauthenticated and MUST listen on localhost only.

## Not production-ready
- No rate limiting, TLS termination, identity provider, scoped roles, token rotation, or comprehensive audit trail.
- No atomic compare-and-swap for simultaneous approval requests; two requests may race.
- API key is a shared tenant credential rather than per-user authorization.
- Process-local metrics are not distributed observability.
- No public cloud deployment performed.
