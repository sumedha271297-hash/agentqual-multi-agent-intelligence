"""Reproducible synthetic baseline evaluation; never imply this is LLM performance."""
import json
import time
from pathlib import Path
from statistics import mean
from app.core import load_companies, workflow_offline
ROOT = Path(__file__).resolve().parent.parent

def evaluate():
    dataset = json.loads((ROOT/'data/evaluation.json').read_text())
    companies = load_companies()
    tp=fp=tn=fn=0
    latencies=[]
    rows=[]
    for cid, expected in dataset['labels'].items():
        start=time.perf_counter()
        outcome=workflow_offline(cid, dataset['icp'], companies)
        latencies.append((time.perf_counter()-start)*1000)
        predicted=outcome['qualification']['qualified']
        tp += predicted and expected
        fp += predicted and not expected
        tn += not predicted and not expected
        fn += not predicted and expected
        rows.append({'id':cid,'expected':expected,'predicted':predicted,'route':outcome['route']})
    precision=tp/(tp+fp) if tp+fp else 0
    recall=tp/(tp+fn) if tp+fn else 0
    f1=2*precision*recall/(precision+recall) if precision+recall else 0
    result={'evaluation_type':'synthetic_deterministic_rules_baseline','sample_count':len(rows),
            'metrics':{'precision':precision,'recall':recall,'f1':f1,'accuracy':(tp+tn)/len(rows),
                       'mean_latency_ms':mean(latencies)},
            'confusion':{'tp':tp,'fp':fp,'tn':tn,'fn':fn},'rows':rows,
            'limitations':['Synthetic labels constructed from matching rules','No LLM calls','Latency excludes network and deployment','Not production evidence']}
    (ROOT/'reports').mkdir(exist_ok=True)
    (ROOT/'reports/evaluation.json').write_text(json.dumps(result,indent=2)+'\n')
    return result

if __name__=='__main__':
    print(json.dumps(evaluate(),indent=2))
