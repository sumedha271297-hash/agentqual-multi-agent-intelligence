# Candidate verification: staging, model, and real browser walkthrough

## Evidence gates

**1. Offline model mocks:** the earlier 81 passing tests verify application
routing and policies with injected synthetic model responses. They do not
establish provider availability, output factuality or model accuracy.

**2. Real container staging rehearsal:** GitHub Actions builds the actual
non-root Docker image and starts a production-mode FastAPI process alongside
PostgreSQL using the localhost-only Docker Compose configuration.
`scripts/staging_probe.py` makes real HTTP requests over TCP, testing
authentication, cross-tenant denial, checkpoint approval, no-send guarantees,
idempotent replay and conflict. Ephemeral CI credentials are visibly fake and
are not valid production secrets. This demonstrates actual deployment into
a CI runner, **not a public cloud service**, ingress TLS or long-term uptime.

**3. Browser recording:** GitHub Actions starts the actual FastAPI server in
development mode bound to 127.0.0.1, then uses Chromium/Playwright to click
Run → Inspect → Approve → Run rejected company. The resulting WebM recording,
MP4 conversion and screenshots are stored as artifacts from that run.
The video is genuine browser interaction with running application code,
but is **not** real OpenAI inference or hosted staging.

**4. Live provider:** remain manual-only using
`Manual Live OpenAI Evaluation` Actions workflow, a valid API secret and
available API credits. A configured secret cannot prove credits are usable;
do not report real-model metrics until an approved billable workflow
has completed successfully. Never print model credentials.

## Candidate presentation

Clearly distinguish tests (software correctness), simulation (synthetic
labels), real container execution (CI staging), browser interaction (local
UI), provider inference (pending) and public deployment (pending).
Never claim an IC4-equivalent professional tenure or verified production
performance solely from an independent portfolio exercise.
