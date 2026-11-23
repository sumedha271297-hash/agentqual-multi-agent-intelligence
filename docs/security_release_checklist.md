# Local hardening and release checklist

## Implemented (verify with CI)
- [x] Container runs as a non-root Unix user
- [x] Python container health check queries local `/health`
- [x] Docker Compose binds API and database ports to localhost
- [x] Tenant identity is server-derived, not selected by client
- [x] Graph read and approval APIs reject foreign tenant IDs
- [x] Production startup requires configured tokens and PostgreSQL
- [x] CI includes a PostgreSQL service and interrupt/recovery tests
- [x] No automated outbound messaging action

## Blocking a public release
- [ ] Real login and per-user/role authorization
- [ ] Concurrency-safe, idempotent approval transactions
- [ ] HTTPS reverse proxy, trusted hosts and network restrictions
- [ ] Secret rotation, managed secrets and audit log retention
- [ ] Rate limits and abuse controls
- [ ] Distributed metrics/traces, alerts and backup restore drills
- [ ] Dependency and container vulnerability scans
- [ ] Public staging deployment with load and failure tests
- [ ] Independently reviewed domain-specific evaluation dataset

**Conclusion:** Improved local-container baseline; no public cloud deployment and no claim of production readiness.
