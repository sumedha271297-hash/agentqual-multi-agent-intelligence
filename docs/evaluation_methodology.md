# Evaluation methodology and limitations

## Why two synthetic baselines?
1. `python -m scripts.evaluate`: ten rule-aligned labels; demonstrates code reproducibility and should score 100% by construction.
2. `python -m scripts.evaluate_rubric`: ten synthetic analyst-style decisions; one contextual exclusion (c09) intentionally disagrees with rule-based ICP scoring. Expected confusion: TP=3, FP=1, TN=6, FN=0; precision=0.75, recall=1.0, F1≈0.8571.

The additional label is **not** a real annotator's judgment. Neither baseline measures LLM output factuality or deployment quality. Sample sizes are far too small for a credible performance promise. Latency is local-only.

## Future defensible evaluation
- Assemble permissioned, de-identified profiles and independent reviewer annotations.
- Blind two annotators to predictions; reconcile disagreements and record inter-annotator agreement.
- Lock a holdout set before prompt/threshold tuning; track split provenance and versions.
- Evaluate precision/recall/F1 with uncertainty intervals, calibration, latency p50/p95, token costs and request failure rates.
- Manually assess unsupported factual statements and human rejection rates for outreach drafts.
- Track failures by failure type, retry behavior, and abstention / human-escalation rate.

No invented 91% precision, 98.5% tool-call success, or production service metrics are used here.
