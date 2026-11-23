# Production-style rehearsal: measured scope and remaining infrastructure

## What GitHub CI tests

A local, ephemeral Docker Compose network runs real PostgreSQL,
production-configured FastAPI and nginx as a TLS-terminating ingress.
The runner generates a **one-day self-signed certificate** for localhost,
then verifies the certificate chain by supplying its local certificate
as a trust root (not by disabling certificate validation).

Security checks: TLS v1.2/1.3 configuration, HSTS response, authenticated
process-local API metrics, 401 without a key, 429 rate limit under burst,
and 404 for the development UI in production mode.

Database recovery: persist pending approval, restart API and resume.
Then create a *second* pending approval, stop API, take a PostgreSQL
`pg_dump` archive, drop and recreate this **CI-only** database, restore
with `pg_restore`, bring API back and resume the pending approval.

The second case is a **backup/restore drill**, which is not the same
as failover of a managed production Postgres cluster.

## Security boundary / infrastructure gaps

- Hosted cloud provider, managed DNS, CA-issued certificate, identity
  federation, rate limiting across multiple ingress replicas, managed
  secrets rotation, WAF and external penetration test: **not deployed**.
- CI variables contain clearly synthetic test credentials only.
  An actual secrets manager and real private customer data are NOT used.
- Monitoring means authenticated **single-process** metrics and nginx
  request logs; there are no external dashboards, persistent traces,
  alerts or SLO evidence.
- HTTPS port is bound to `127.0.0.1:8443`; development HTTP remains
  localhost-only at 8080 as an internal diagnostic. Do not publicize
  this environment as publicly accessible or production ready.
- Do not reuse the short-lived self-signed certificate in production.
- The CI job creates and destroys disposable DB volumes; do not run the
  drop-and-restore script against any real user database.

## Provider evaluation

The opt-in OpenAI evaluation remains gated by GitHub manual dispatch
and a real account with available credits. No automated provider costs.
The existing program checks schema and latency only; separately reviewed
factuality, token/cost instrumentation and real-data generalization
remain future validation gates.

## Data review

Run blind packet exporter; genuine human raters must provide their own
decisions. The software rejects duplicate reviewer IDs and incomplete
adjudication but cannot validate identity; no independent evaluation
metric is reported until real submissions are available.
