"""Disclosure-forward evaluation against a synthetic review rubric.

Do not describe this as independent human labeling or real-world accuracy.
"""
import json
from pathlib import Path
from app.core import workflow_offline
ROOT=Path(__file__).resolve().parent.parent
ICP={"industries":["SaaS","Fintech"],"min_employees":20,
     "max_employees":300,"regions":["US"]}

def evaluate():
    rows=json.loads((ROOT/"data/review_rubric.json").read_text())["labels"]
    tp=tn=fp=fn=0
    errors=[]
    for row in rows:
        actual=workflow_offline(row["id"],ICP)["qualification"]["qualified"]
        expected=row["qualified"]
        if actual and expected: tp+=1
        elif not actual and not expected: tn+=1
        elif actual: fp+=1; errors.append({"id":row["id"],"kind":"false_positive","reason":row["reason"]})
        else: fn+=1; errors.append({"id":row["id"],"kind":"false_negative","reason":row["reason"]})
    precision=tp/(tp+fp) if tp+fp else 0.
    recall=tp/(tp+fn) if tp+fn else 0.
    f1=2*precision*recall/(precision+recall) if precision+recall else 0.
    outcome={"dataset":"synthetic_review_rubric","n":len(rows),
             "confusion":{"tp":tp,"tn":tn,"fp":fp,"fn":fn},
             "precision":precision,"recall":recall,"f1":f1,
             "errors":errors,"disclaimer":"Synthetic qualitative labels; no generalization claims."}
    (ROOT/"reports").mkdir(exist_ok=True)
    (ROOT/"reports/rubric_evaluation.json").write_text(json.dumps(outcome,indent=2)+"\n")
    return outcome

if __name__=="__main__":
    print(json.dumps(evaluate(),indent=2))
