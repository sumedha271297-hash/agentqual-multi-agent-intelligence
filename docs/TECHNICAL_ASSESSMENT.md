# AgentQual — Practical engineering defense exercise

This is a hands-on **candidate assessment**, not a completed interview.
It requires the candidate to independently explain and modify the code.
The repository provides questions and observable success criteria; it
does **not** generate passing answers or claim that the candidate passed.

| Task | Challenge | Minimum evidence | Timebox recommendation |
|---|---|---|---|
| A | Trace `POST /graph/run` for an ICP match and nonmatch | Show actual nodes, route, interrupt and stored state; identify no-send guarantee | 10 min |
| B | Explain why the application needs LangGraph | Compare against a plain Python state machine; justify persistence and complexity | 8 min |
| C | Attack `/graph/{thread_id}/approve` | Show cross-tenant 404, idempotent replay, conflicting approval 409 and one limitation | 12 min |
| D | Inject a faulty provider result | Demonstrate fail-closed route and explain remaining factuality vulnerability | 10 min |
| E | Explain Postgres advisory locks and recovery | Walk through commit-before-retry and a DB backup/restore demonstration | 12 min |
| F | Design outbound sending safely | Draw a transactional outbox and explain how network retries cause duplicates | 15 min |
| G | Assess whether an LLM should qualify leads | Propose an independent labeled dataset, baseline/model ablation, uncertainty and cost gate | 12 min |
| H | Diagnose a failed staging CI job | Show logs, distinguish root cause from symptoms, write regression test | 15 min |

## Scoring (manual only)

Independent interviewer or human reviewer scores each task 0–4:

- **0:** no answer or incorrect.
- **1:** surface-level terminology without mechanisms.
- **2:** describes the correct general approach but misses failure boundaries.
- **3:** demonstrates code-grounded reasoning, trade-offs and an appropriate test.
- **4:** additionally identifies hidden assumptions and produces reproducible evidence of a working fix.

The maximum is 32. There is **no automatic pass**: reviewers must inspect
answers and code, especially task E/F on failure atomicity. Reviewer's actual
identity and feedback should be recorded privately; do not fabricate them.

## Launch

Run `python -m scripts.practice_defense` from the project root, answer
interactively, and inspect the locally saved file in `reports/`. The
script does not submit your answers to an LLM, score you, or call any API.

If no reviewer is available, treat your answers as *self-practice only*,
not a verified IC4 interview outcome.
