# Gemini provider setup (optional)

AgentQual supports structured draft generation using Google's official
`google-genai` Python SDK.

1. Visit https://aistudio.google.com/apikey and create a Google AI Studio API key.
2. Verify your project's specific free-tier model availability and request quotas
   at https://ai.google.dev/gemini-api/docs/pricing. Free access is **not**
   guaranteed for every account, region, or model. Paid projects may incur fees.
3. Set `GEMINI_API_KEY` as a local environment variable (or private, untracked
   `.env` file). Never publish or paste a secret into chat or commit history.
4. Install dependencies: `pip install -r requirements-dev.txt`.
5. Run offline tests: `python -m pytest -q`.
6. To opt in to **one** real API request locally:

```bash
python -m scripts.evaluate_live --provider gemini --max-cases 1 --allow-provider-calls
```

Live evaluation is **not** run automatically in CI. Only schema success, provider error type,
and request latency are saved to ignored `reports/live_provider_evaluation.json`.
No generated email text or secrets are persisted in the report. This is not a
qualification accuracy or factual-grounding evaluation.

Default model: `gemini-2.5-flash-lite` (override with `GEMINI_MODEL` if
unavailable). The graph requires `llm_enabled=true` and
`llm_provider="gemini"`, with tenant API authentication as configured.
Human approval is still mandatory and messages are **never** sent.

Existing offline and OpenAI modes remain available.

## Recommended GitHub Actions test (without local Python)

**Manual-only:** [Manual Free-Tier Gemini Smoke Evaluation](../.github/workflows/live-gemini-free.yml).

1. Visit https://aistudio.google.com/api-keys. Create/select a Google AI Studio project and ensure its billing and model-specific usage **actually show a Free tier**. **If billing is enabled, this workflow cannot guarantee a $0 invoice.** Check free-tier model availability and quotas before continuing.
2. Create a Gemini API key for that free-tier project. Do not paste the key into chat or source files.
3. In GitHub repository: **Settings → Secrets and variables → Actions → New repository secret**, set the exact name `GEMINI_API_KEY`, paste the key into the GitHub secret value, and save. The existing `OPENAI_API_KEY` secret does not work for Gemini.
4. Go to **Actions → Manual Free-Tier Gemini Smoke Evaluation → Run workflow**, enter `RUN_GEMINI_FREE`, and select **1** case to start.
5. Inspect the completed run and the `agentqual-gemini-free-tier-smoke` artifact. A 403/429/404 or missing secret is not a successful result; check AI Studio model/region/quota permissions before retrying.
6. Only after the one-case result succeeds should you select two or three cases.

**Privacy:** Gemini free-tier inputs and outputs may be used to improve Google's products; this demo uses fictional company fields only. Never use private leads or confidential company information.

**Evidence:** A green run establishes that the real Gemini SDK generated a schema-valid draft and reports latency for the tested fictional input(s). It does **not** establish qualified-lead accuracy, factual grounding, or independent human review.
