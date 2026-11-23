# Adversarial exercise and performance smoke methodology

Run `python -m scripts.security_matrix` to execute six **mocked and
deterministic** policy attacks: forbidden tool, cross-record lookup,
multiple tool requests, extra tool argument, a prompt-injection-induced
positive decision, and empty draft interrupt bypass. The script asserts
all six are blocked by application policy. These results **do not**
show that a live LLM resists prompt injection or fabricated facts.

Run `python -m scripts.performance_smoke` for 80 HTTP requests with
eight threads using the FastAPI in-process TestClient. This exercises
the deterministic offline endpoint; it includes TestClient startup
overhead and is not a network benchmark. Report p50/p95/max latency,
observed requests/second and failure counts as **CI-runner-only smoke
measurements**. No absolute latency or availability promises are made.

Artifacts are uploaded from a passing GitHub Actions run. A future
realistic load test must deploy to a private, monitored staging service,
record its instance sizing, DB connection utilization, workload mix,
queueing, and failures at increasing concurrency. A future LLM security
assessment must use real provider calls and independently judged results.
