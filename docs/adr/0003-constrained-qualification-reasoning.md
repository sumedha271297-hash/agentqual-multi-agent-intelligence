# ADR-0003: Constrained LLM assessment, with deterministic veto

Status: Experimental candidate demonstration.

The previous research LLM could request exactly one allowlisted tool but
qualification itself was deterministic. We add an **optional** LLM reasoning
stage that emits schema-constrained QUALIFY, REJECT or REVIEW, with explicit
evidence-field names. Unexpected model behavior fails closed. A deterministic
ICP rule vetoes unsupported QUALIFY outcomes; no reasoner can bypass mandatory
industry, employee count and region criteria. REVIEW terminates with no draft.

This makes the qualification stage model-assisted but deliberately bounds
autonomy. It is **not** a multi-agent team with independently operating workers,
nor does it establish inference accuracy without live-provider evaluation.

Known tradeoff: a stricter deterministic veto may cause false negatives on
otherwise relevant companies. That tension should be measured against human
labels before a real deployment. Company descriptions are untrusted strings;
schema checks do not prevent every prompt-injection attack.
