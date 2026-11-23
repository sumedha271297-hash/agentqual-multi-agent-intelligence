"""Blinded annotation packet and independent review audit.

No auto-created labels or synthetic reviewer personas. Reviewer files must be
created by genuine humans and are never silently fabricated. Do not treat
existing synthetic labels as ground truth.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path
from app.core import load_companies, qualify, Company
from scripts.evaluate_v2 import metrics
ROOT=Path(__file__).resolve().parent.parent

def packet(output_dir):
    source=json.loads((ROOT/"data/eval_v2.json").read_text())
    companies=load_companies()
    output_dir=Path(output_dir)
    output_dir.mkdir(parents=True,exist_ok=True)
    # Blinding removes model outcomes, original synthetic labels and annotations.
    rows=[]
    for case in source["cases"]:
        c=companies[case["company_id"]]
        rows.append({"case_id":case["case_id"],"company_id":c.id,
          "company_name":c.name,"industry":c.industry,"employees":c.employees,
          "region":c.region,"description":c.description,
          "icp_policy":json.dumps(source["policies"][case["icp_id"]],sort_keys=True)})
    path=output_dir/"blind_cases.csv"
    with path.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    return path

def _load_review(path, known_ids):
    with Path(path).open(newline="",encoding="utf-8") as f:
        reader=csv.DictReader(f)
        if not {"case_id","decision","reviewer_id","evidence_note"}.issubset(reader.fieldnames or []):
            raise ValueError("Reviewer file missing fields: case_id, decision, reviewer_id, evidence_note")
        data=list(reader)
    if not data or len(data)!=len(known_ids) or set(x["case_id"] for x in data)!=known_ids:
        raise ValueError("Reviewer must label each case exactly once, with no duplicates")
    reviewers={x["reviewer_id"].strip() for x in data}
    if len(reviewers)!=1 or not next(iter(reviewers)):
        raise ValueError("Exactly one nonempty stable reviewer_id per file required")
    for x in data:
        if x["decision"] not in {"QUALIFY","REJECT","REVIEW"}:
            raise ValueError("Decision must be QUALIFY / REJECT / REVIEW")
        if len(x["evidence_note"].strip())<8:
            raise ValueError("Every decision requires a descriptive evidence note")
    return next(iter(reviewers)),{x["case_id"]:x for x in data}

def score(review_a,review_b,adjudication=None):
    source=json.loads((ROOT/"data/eval_v2.json").read_text())
    known_ids={x["case_id"] for x in source["cases"]}
    a_id,a=_load_review(review_a,known_ids)
    b_id,b=_load_review(review_b,known_ids)
    if a_id==b_id:
        raise ValueError("Two distinct reviewers required")
    conflicts=sorted(x for x in known_ids if a[x]["decision"]!=b[x]["decision"])
    agreement=sum(a[x]["decision"]==b[x]["decision"] for x in known_ids)/len(known_ids)
    result={"source":"human_submitted_reviews_unverified_identity",
            "reviewer_ids":[a_id,b_id],"case_count":len(known_ids),
            "exact_agreement":round(agreement,4),
            "disagreements":conflicts,
            "disagreement_count":len(conflicts),
            "annotation_file_hashes":[hashlib.sha256(Path(p).read_bytes()).hexdigest()
                                       for p in (review_a,review_b)],
            "publishable_holdout_score":False}
    if adjudication is None:
        return result
    with Path(adjudication).open(newline="",encoding="utf-8") as f:
        reader=csv.DictReader(f)
        if not {"case_id","final_decision","adjudicator_id","rationale"}.issubset(reader.fieldnames or []):
            raise ValueError("Missing adjudication fields")
        resolutions=list(reader)
    if set(x["case_id"] for x in resolutions)!=set(conflicts) or len(resolutions)!=len(conflicts):
        raise ValueError("Adjudication must resolve each disagreement once")
    for r in resolutions:
        if r["final_decision"] not in {"QUALIFY","REJECT","REVIEW"} or len(r["rationale"].strip())<8:
            raise ValueError("Incomplete final decision or rationale")
        if r["adjudicator_id"] in {a_id,b_id} or not r["adjudicator_id"].strip():
            raise ValueError("Adjudicator must be distinct and identified")
    final={cid:a[cid]["decision"] for cid in known_ids}
    final.update({r["case_id"]:r["final_decision"] for r in resolutions})
    result["resolved"]=True
    result["adjudication_sha256"]=hashlib.sha256(Path(adjudication).read_bytes()).hexdigest()
    comparisons=[]
    companies=load_companies()
    for case in source["cases"]:
        label=final[case["case_id"]]
        if label=="REVIEW": continue
        pred=qualify(companies[case["company_id"]],source["policies"][case["icp_id"]])["qualified"]
        comparisons.append({"expected":label=="QUALIFY","predicted":pred,
                            "case_id":case["case_id"]})
    result["baseline_results"]=metrics(comparisons)
    result["abstained_count"]=sum(x=="REVIEW" for x in final.values())
    # Human labels on synthetic inputs; no real-company generalization.
    result["publishable_holdout_score"]=False
    result["limitations"]="Identity/provenance not verified by software; fictional cases; repeated companies across policies."
    return result

def main():
    parser=argparse.ArgumentParser()
    sub=parser.add_subparsers(dest="mode",required=True)
    p=sub.add_parser("packet");p.add_argument("--out",default="reports/annotation_packet")
    s=sub.add_parser("score");s.add_argument("--review-a",required=True);s.add_argument("--review-b",required=True)
    s.add_argument("--adjudication")
    args=parser.parse_args()
    if args.mode=="packet":
        print("Blind reviewer packet:",packet(args.out))
    else:
        result=score(args.review_a,args.review_b,args.adjudication)
        print(json.dumps(result,indent=2))

if __name__=="__main__":main()
