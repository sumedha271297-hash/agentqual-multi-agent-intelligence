# ADR-0001: Serialize human approvals by graph thread

**Status:** Accepted for candidate demonstration.

## Context
Two API workers may inspect the same checkpoint while its human
interrupt is pending. If both call `Command(resume=...)`, a time-of-check /
time-of-use race can duplicate side effects or produce inconsistent state.

## Decision
Use a PostgreSQL session advisory lock keyed by a stable 64-bit digest of
`thread_id`. Hold that lock while re-reading the snapshot, authorizing the
tenant, resuming the graph and persisting the checkpoint. Separate
connections are used for the lock and LangGraph persistence. In local
development without DATABASE_URL, use 256 in-process lock stripes.

Persist `approval_request_id` and the decision in checkpoint state.
A retry with the same UUID key and same decision returns a replayed
response; an unrelated or conflicting approval returns 409.

## Limitations
- In-process lock stripes do not protect multiple worker processes.
- Requires every writer of approval state to respect this lock protocol.
- Idempotency is for human approval only; general side effects would
  need a transactional outbox and delivery idempotency.
- A crashed process releases the session lock, but the checkpoint must
  have committed before the caller retries.
- PostgreSQL advisory-lock digest collisions cause extra serialization,
  not authorization bypass. This is not a distributed job system.
