"""Offline reproducible resilience experiments; not production availability statistics."""
import json
from pathlib import Path
from unittest.mock import patch
from langgraph.checkpoint.memory import MemorySaver
from app.graph import build_graph
from app.tools import ToolFailure

ROOT=Path(__file__).resolve().parent.parent
ICP={"industries":["SaaS","Fintech"],"min_employees":20,"max_employees":300,"regions":["US"]}

def measure():
    cases=[]
    for name,patch_target,exception in [
        ("research_timeout","app.graph.company_lookup",ToolFailure("synthetic timeout")),
        ("llm_timeout","app.llm.generate_llm_draft",TimeoutError("synthetic provider timeout")),
    ]:
        graph=build_graph(MemorySaver())
        state={"company_id":"c01","tenant_id":"test","icp":ICP,"sent":False,
               "llm_enabled":name=="llm_timeout"}
        with patch(patch_target,side_effect=exception):
            output=graph.invoke(state,{"configurable":{"thread_id":name}})
        cases.append({"case":name,"route":output["route"],
                      "sent":output["sent"],"passed":output["route"]=="failed" and output["sent"] is False})
    graph=build_graph(MemorySaver())
    result=graph.invoke({"company_id":"c02","tenant_id":"test","icp":ICP,"sent":False},
                        {"configurable":{"thread_id":"disqualified"}})
    cases.append({"case":"disqualified","route":result["route"],"sent":result["sent"],
                  "passed":result["route"]=="rejected" and result["sent"] is False})
    report={"kind":"synthetic_failure_injection","case_count":len(cases),
            "passed_count":sum(case["passed"] for case in cases),
            "cases":cases,"limitations":"Synthetic in-process tests, not availability, load testing or provider reliability."}
    (ROOT/"reports").mkdir(exist_ok=True)
    (ROOT/"reports/resilience.json").write_text(json.dumps(report,indent=2)+"\n")
    return report

if __name__=="__main__":
    print(json.dumps(measure(),indent=2))
