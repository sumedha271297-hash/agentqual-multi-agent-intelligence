# Evaluation v2: frozen, synthetic scenario matrix

The `data/eval_v2.json` fixture contains 40 labeled cases (ten fictional
companies × four ICP policies). Each case has an explicit frozen outcome,
an explanation, and a split assignment; the evaluator does NOT generate
labels using the code it tests. They are authored simulated labels, **not**
a sample of independently labeled real customer data.

The same ten fictional companies occur in both splits with different ICP
policies; **this is not an independent company-level holdout** and is not
suitable for a statistical generalization claim. Evaluate against the locked
holdout without tuning on it; any synthetic disagreements illustrate limits
of the simplistic ICP scoring rules.

`python -m scripts.evaluate_v2` emits confusion, precision, recall, F1,
coverage, and per-ICP/per-split errors. The evaluator reports both
`development` and `holdout` splits and checks deterministic reproducibility.
Zero-cost, no external API calls.

Next evidence gate: replace simulated outcomes with consented, de-identified
real company profiles scored by two blinded independent reviewers; record
disagreements and version data provenance. Never call the 40 examples
independent human ground truth or report their metrics as model accuracy.
