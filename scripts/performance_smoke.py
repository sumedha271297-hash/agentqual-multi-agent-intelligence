"""Bounded localhost/in-process HTTP stress check with reproducible report.

No external API calls, no reliability SLA. This is a GitHub-runner sample,
not a statistically powered load test on deployed infrastructure.
"""
import json
import math
import statistics
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from fastapi.testclient import TestClient
from app.api import app

ROOT=Path(__file__).resolve().parent.parent
ICP={"industries":["SaaS","Fintech"],"min_employees":20,"max_employees":300,"regions":["US"]}

def percentile(values,p):
    ordered=sorted(values)
    if not ordered: return 0
    rank=max(0, math.ceil(p/100*len(ordered))-1)
    return round(ordered[rank],3)

def measure(request_count=80, workers=8):
    if not (1<=request_count<=300 and 1<=workers<=16):
        raise ValueError("Limits: requests 1..300, workers 1..16")
    payload={"company_id":"c01","icp":ICP,"llm_enabled":False}
    def task(index):
        started=time.perf_counter()
        # Separate TestClient per worker task avoids sharing client request state.
        # No lifespan needed for deterministic route; avoids concurrent DB setup.
        client=TestClient(app)
        res=client.post("/offline/run",json=payload)
        elapsed=(time.perf_counter()-started)*1000
        return {"status":res.status_code,"latency_ms":elapsed,
                "safe":res.status_code==200 and res.json().get("sent") is False}
    start=time.perf_counter()
    with ThreadPoolExecutor(max_workers=workers) as pool:
        records=list(pool.map(task,range(request_count)))
    wall=time.perf_counter()-start
    latencies=[r["latency_ms"] for r in records]
    successes=sum(r["safe"] for r in records)
    report={"kind":"inprocess_http_smoke_load","requests":request_count,
            "workers":workers,"safe_successes":successes,"failures":request_count-successes,
            "latency_ms":{"p50":percentile(latencies,50),
                          "p95":percentile(latencies,95),
                          "max":round(max(latencies),3)},
            "wall_seconds":round(wall,3),
            "observed_requests_per_second":round(request_count/wall,2) if wall else 0,
            "limitations":"In-process TestClient overhead includes client startup; fictional data, no network, no model, no staging infrastructure. Not production throughput."}
    (ROOT/"reports").mkdir(exist_ok=True)
    (ROOT/"reports/performance_smoke.json").write_text(json.dumps(report,indent=2)+"\n")
    if successes!=request_count:
        raise AssertionError("Load smoke saw unsuccessful or unsafe responses")
    return report

if __name__=="__main__":
    print(json.dumps(measure(),indent=2))
