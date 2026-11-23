"""End-to-end graph route tests with mocked model reasoning."""
import uuid
from unittest.mock import patch
from langgraph.checkpoint.memory import MemorySaver
from app.graph import build_graph

ICP={"industries":["SaaS"],"min_employees":20,"max_employees":300,"regions":["US"]}

def run(verdict):
    graph=build_graph(MemorySaver())
    cfg={"configurable":{"thread_id":str(uuid.uuid4())}}
    with patch("app.reasoning.assess", return_value={"verdict":verdict,
                "reason":"synthetic assessment","evidence_fields":["industry"]}):
        result=graph.invoke({"company_id":"c01","icp":ICP,"tenant_id":"demo",
          "agentic_qualification":True,"llm_enabled":False,"sent":False},cfg)
    return graph,cfg,result

def test_reasoning_accept_route_needs_approval():
    g,c,r=run("QUALIFY")
    assert r["route"]=="approval" and g.get_state(c).interrupts

def test_reasoning_abstains_without_draft():
    g,c,r=run("REVIEW")
    assert r["route"]=="needs_review"
    assert not r.get("draft") and not g.get_state(c).interrupts

def test_reasoning_rejects_without_draft():
    g,c,r=run("REJECT")
    assert r["route"]=="rejected"
    assert not r.get("draft") and not g.get_state(c).interrupts

def test_reasoning_failure_fails_closed():
    g=build_graph(MemorySaver()); cfg={"configurable":{"thread_id":str(uuid.uuid4())}}
    with patch("app.reasoning.assess",side_effect=TimeoutError("provider offline")):
        r=g.invoke({"company_id":"c01","icp":ICP,"tenant_id":"demo",
          "agentic_qualification":True,"llm_enabled":False,"sent":False},cfg)
    assert r["route"]=="needs_review" and not r.get("draft")
