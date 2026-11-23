"""Opt-in live LLM provider check for structured drafting.

Never runs in CI. Requires explicit opt-in and provider credential. Evaluates a few
synthetic, known-qualified companies. Measures API outcomes and latency only;
does not claim objective factual correctness or real-world qualification accuracy.
"""
import argparse
import json
import os
import statistics
import time
from pathlib import Path
from app.core import load_companies
from app.llm import generate_llm_draft

ROOT = Path(__file__).resolve().parent.parent

def evaluate_live(ids, provider='openai'):
    data = load_companies()
    results = []
    for cid in ids:
        company = data[cid]
        started = time.perf_counter()
        try:
            if provider == "gemini":
                from app.gemini import generate_gemini_draft
                draft = generate_gemini_draft(vars(company))
            else:
                draft = generate_llm_draft(vars(company))
            status = "schema_valid"
            error_type = None
            # No automatic approval; text deliberately NOT saved in public report.
            schema_valid = bool(draft.get("subject") and draft.get("message") and
                                draft.get("requires_approval") and not draft.get("sent"))
        except Exception as exc:
            schema_valid = False
            status = "failed"
            error_type = type(exc).__name__
        results.append({"company_id":cid,"status":status,"schema_valid":schema_valid,
                        "latency_ms":round((time.perf_counter()-started)*1000,1),
                        "error_type":error_type})
    metrics = {"total": len(results), "successful_schema_outputs":
               sum(x["schema_valid"] for x in results),
               "schema_success_rate": sum(x["schema_valid"] for x in results)/len(results),
               "median_latency_ms": round(statistics.median(x["latency_ms"] for x in results),1),
               "provider": provider,
               "provider_model": (os.environ.get("GEMINI_MODEL","gemini-2.5-flash-lite") if provider == "gemini" else os.environ.get("OPENAI_MODEL","gpt-4.1-mini")),
               "limitations": "Synthetic data, small sample, schema only; no factuality, token-cost or qualitative accuracy measured."}
    return {"evaluation_type":"LIVE_PROVIDER_SCHEMAS_ONLY","metrics":metrics,"rows":results}

if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--provider",choices=["openai","gemini"],default="gemini")
    parser.add_argument("--allow-provider-calls",action="store_true",help="Explicitly authorize live requests (may incur charges)")
    parser.add_argument("--allow-billable",action="store_true",help="Legacy opt-in alias")
    parser.add_argument("--max-cases",type=int,default=3)
    args=parser.parse_args()
    if not (args.allow_provider_calls or args.allow_billable):
        parser.error("Requires --allow-provider-calls for live requests")
    key = "GEMINI_API_KEY" if args.provider == "gemini" else "OPENAI_API_KEY"
    if not os.getenv(key):
        parser.error(f"{key} is not set")
    if not 1 <= args.max_cases <= 3:
        parser.error("--max-cases must be in [1,3]")
    ids=["c01","c04","c08"][:args.max_cases]
    output=evaluate_live(ids,provider=args.provider)
    (ROOT/"reports").mkdir(exist_ok=True)
    destination=ROOT/"reports/live_provider_evaluation.json"
    destination.write_text(json.dumps(output,indent=2)+"\n")
    print(json.dumps(output,indent=2))
