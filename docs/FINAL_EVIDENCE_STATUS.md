# AgentQual — final evidence status (verified 2026-11-24)

## What actually passed

| Capability | Verification | Evidence |
|---|---|---|
| Python tests | 88 passed, including blind-review validation and self-practice harness | [CI run 45248497843](https://github.com/sumedha271297-hash/agentqual-multi-agent-intelligence/actions/runs/45248497843) |
| Genuine UI walkthrough | Browser executed run, inspect, approve and reject; Playwright video generated and uploaded | [Staging/browser run 45248497792](https://github.com/sumedha271297-hash/agentqual-multi-agent-intelligence/actions/runs/45248497792) |
| HTTP tenant isolation | Real Compose API denied unauthorized and cross-tenant reads/approvals | [Staging/browser run 45248497792](https://github.com/sumedha271297-hash/agentqual-multi-agent-intelligence/actions/runs/45248497792) |
| TLS ingress | Ephemeral localhost self-signed certificate explicitly trusted and verified; HSTS present | [Staging/browser run 45248497792](https://github.com/sumedha271297-hash/agentqual-multi-agent-intelligence/actions/runs/45248497792) |
| Rate limiting | nginx ingress returned HTTP 429 for a burst | [Staging/browser run 45248497792](https://github.com/sumedha271297-hash/agentqual-multi-agent-intelligence/actions/runs/45248497792) |
| Basic monitoring | Authenticated process-local API metrics endpoint over HTTPS | [Staging/browser run 45248497792](https://github.com/sumedha271297-hash/agentqual-multi-agent-intelligence/actions/runs/45248497792) |
| Restart recovery | Pending approval recovered after actual API restart with PostgreSQL state | [Staging/browser run 45248497792](https://github.com/sumedha271297-hash/agentqual-multi-agent-intelligence/actions/runs/45248497792) |
| Backup and restore | CI dumped and restored the actual PostgreSQL database and resumed a pending approval | [Staging/browser run 45248497792](https://github.com/sumedha271297-hash/agentqual-multi-agent-intelligence/actions/runs/45248497792) |
| Blind annotation process | Generates 40 unlabeled synthetic scenarios and validates separate reviewer CSV files; no reviewer file is supplied | [Blind-review module](../scripts/blind_review.py) |
| Interview assessment | Eight tasks, local answer recorder, manual rubric; candidate participation not claimed | [Assessment](TECHNICAL_ASSESSMENT.md) |

## What has NOT been accomplished

1. **Independent human review**: reviewers have not provided labels. The tool cannot create independent human judgments.
2. **Real LLM evaluation**: no successful provider runs or measured model factuality. Requires credits, manual opt-in and a genuine evaluation rubric.
3. **Actual private cloud deployment**: no cloud account, managed HTTPS certificate, DNS, managed secret store, centralized monitoring, or public ingress. All successful staging tests are on an ephemeral GitHub runner and local-only endpoints.
4. **Verified engineering interview performance**: a preparation and practice system exists; no candidate answers or human interviewer ratings were recorded.
5. **Commercial production impact**: no customer deployments, outreach sending, ROI or real precision metric.

## Candidate-safe project positioning

> Built an independent FastAPI/LangGraph qualification workflow with PostgreSQL-backed human approval, bounded model-tool policies, an optional schema-constrained LLM path and tenant-aware approval controls. Verified with 88 tests, real localhost TLS/rate-limit staging probes, database backup/restore recovery and a Chromium walkthrough. Synthetic benchmark results are identified as synthetic; live model evaluation and cloud deployment remain outstanding.

This is a credible portfolio case study; it is not proof of professional tenure, model accuracy on real leads, or production security.
