"""Actually invoke LangGraph in CI and save a sanitized, reproducible trace.

No provider key and no network calls. Real workflow execution, not synthetic
console transcript. No source/customer data or outreach text in trace.
"""
import json
import uuid
from pathlib import Path
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command
from app.graph import build_graph

ROOT=Path(__file__).resolve().parent.parent
ICP={"industries":["SaaS","Fintech"],"min_employees":20,
     "max_employees":300,"regions":["US"]}

def demonstrate():
    graph=build_graph(MemorySaver())
    cases=[]
    for company_id, expected in [("c01","approval"),("c02","rejected")]:
        cfg={"configurable":{"thread_id":str(uuid.uuid4())}}
        r=graph.invoke({"company_id":company_id,"tenant_id":"demo","icp":ICP,
                        "llm_enabled":False,"agentic_research":False,
                        "agentic_qualification":False,"sent":False},cfg)
        waiting=bool(graph.get_state(cfg).interrupts)
        if r["route"]!=expected:
            raise AssertionError(f"{company_id}: expected {expected}, got {r['route']}")
        item={"company_id":company_id,"initial_route":r["route"],
              "awaiting_approval":waiting,"sent":r["sent"]}
        if waiting:
            r=graph.invoke(Command(resume={"approved":True,"request_id":"ci-demo"}),cfg)
            item.update({"final_route":r["route"],"approved":r["approved"],
                         "sent_after_resume":r["sent"]})
            if not (r["approved"] and r["sent"] is False):
                raise AssertionError("Approval safety invariant failed")
        cases.append(item)
    report={"artifact_type":"verified_offline_langgraph_trace",
            "provider_calls":0,"cases":cases,"limitations":
            "CI in-memory graph, synthetic records, no real LLM or cloud deployment"}
    path=ROOT/"reports"/"demo_trace.json"
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(report,indent=2)+"\n")
    return report

if __name__=="__main__":
    print(json.dumps(demonstrate(),indent=2))
