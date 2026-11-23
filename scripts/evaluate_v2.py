"""Score explicit frozen synthetic labels; no label is generated from predictions."""
import json
from pathlib import Path
from app.core import workflow_offline
ROOT=Path(__file__).resolve().parent.parent

def metrics(rows):
    tp=sum(r["predicted"] and r["expected"] for r in rows)
    fp=sum(r["predicted"] and not r["expected"] for r in rows)
    tn=sum(not r["predicted"] and not r["expected"] for r in rows)
    fn=sum(not r["predicted"] and r["expected"] for r in rows)
    precision=tp/(tp+fp) if tp+fp else 0.0
    recall=tp/(tp+fn) if tp+fn else 0.0
    f1=2*precision*recall/(precision+recall) if precision+recall else 0.0
    return {"n":len(rows),"tp":tp,"fp":fp,"tn":tn,"fn":fn,
            "precision":round(precision,4),"recall":round(recall,4),
            "f1":round(f1,4),"coverage":1.0 if rows else 0.0}

def evaluate():
    data=json.loads((ROOT/"data/eval_v2.json").read_text())
    cases=data["cases"]
    ids=[c["case_id"] for c in cases]
    if len(ids)!=40 or len(set(ids))!=40:
        raise ValueError("Expected exactly 40 unique frozen synthetic cases")
    rows=[]
    for case in cases:
        policy=data["policies"][case["icp_id"]]
        result=workflow_offline(case["company_id"],policy)
        rows.append({"case_id":case["case_id"],"split":case["split"],
                     "icp_id":case["icp_id"],
                     "expected":case["expected_qualified"],
                     "predicted":result["qualification"]["qualified"]})
    report={"version":data["version"],"provenance":data["label_provenance"],
            "overall":metrics(rows),
            "splits":{s:metrics([r for r in rows if r["split"]==s])
                       for s in ("development","holdout")},
            "by_policy":{p:metrics([r for r in rows if r["icp_id"]==p])
                         for p in sorted(data["policies"])},
            "errors":[r for r in rows if r["expected"]!=r["predicted"]],
            "caution":"Synthetic labels and overlapping companies across splits; no out-of-sample real-world inference"}
    (ROOT/"reports").mkdir(exist_ok=True)
    (ROOT/"reports/eval_v2.json").write_text(json.dumps(report,indent=2)+"\n")
    return report

if __name__=="__main__":
    print(json.dumps(evaluate(),indent=2))
