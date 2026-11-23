# Blind human annotation protocol — no invented reviewers

This protocol **does not claim the review is complete**. The existing
40-case matrix is fictional. Our software may generate an unlabeled packet,
but must NOT generate or impersonate independent human labels.

1. Run `python -m scripts.blind_review packet --out reports/annotation_packet`.
2. Give `blind_cases.csv` (without predictions or previous synthetic labels)
   to two independent humans with appropriate domain context. They should
   work separately and record `case_id,decision,reviewer_id,evidence_note`
   in individual CSV files, using QUALIFY / REJECT / REVIEW.
3. Record each reviewer's actual identity/contact, consent, expertise and
   date in a private provenance record; do not post personal details publicly.
   The script validates format and distinct IDs, **not actual identity**.
4. Use `python -m scripts.blind_review score --review-a a.csv --review-b b.csv`
   to report raw agreement and contested IDs.
5. A third independent adjudicator must decide every disagreement in a CSV:
   `case_id,final_decision,adjudicator_id,rationale`. Supply it with
   `--adjudication adjudication.csv`.
6. Keep a frozen company-level holdout wholly separate from development
   examples for future real-world evaluation. Current 40 cases reuse ten
   company records across policies and are **not a valid independent holdout**.
7. Run live model outputs on authorized API credits and score with separate
   factuality rubric. Prevent leakage from label files into the model prompt.

Even if humans annotate the existing fictional cases, the result is only
**human judgments about synthetic profiles**, not field accuracy. Genuine
company-level, permissioned, de-identified source material and blind labels
are required before claiming real-world precision/recall.

Do not commit reviewer's personal contact details or customer records.
