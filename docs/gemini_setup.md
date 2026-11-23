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
6. To opt in to **one** real API request:

```bash
python -m scripts.evaluate_live --provider gemini --max-cases 1 --allow-provider-calls
```

Live evaluation is **not** run in CI. Only schema success, provider error type,
and request latency are saved to ignored `reports/live_provider_evaluation.json`.
No generated email text or secrets are persisted in the report. This is not a
qualification accuracy or factual-grounding evaluation.

Default model: `gemini-2.5-flash-lite` (override with `GEMINI_MODEL` if
unavailable). The graph requires `llm_enabled=true` and
`llm_provider="gemini"`, with tenant API authentication as configured.
Human approval is still mandatory and messages are **never** sent.

Existing offline and OpenAI modes remain available.
