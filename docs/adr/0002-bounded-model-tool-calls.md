# ADR-0002: Allow model-driven tools only behind a deterministic policy

**Status:** Experimental, optional, no live-provider evidence.

## Decision
The research stage can use OpenAI tool calling to select a request to
`company_lookup`. The server enforces a single tool request, exact
company ID matching, exact JSON arguments and an allowlisted tool name.
On malformed plans, cross-record attempts or provider failures, the
workflow fails closed. The offline deterministic path remains the default.

## Rationale
This makes tool selection genuinely model-directed without granting an
LLM arbitrary URLs, data access, writes, messaging or unlimited calls.

## Limitations
Only a single tool is available and qualification still uses
deterministic rules. This is **not** a team of autonomous agents.
Mock tests validate policy enforcement, not the live-model's ability to
choose useful tools. Tool-output prompt injection still needs dedicated
red-team evaluation before wider data sources are connected.
