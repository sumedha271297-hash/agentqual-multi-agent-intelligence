"""Integration checks of model-directed tool routing inside LangGraph.

Provider response is mocked to avoid billable API use.
"""
import uuid
from unittest.mock import patch
from langgraph.checkpoint.memory import MemorySaver
from app.graph import build_graph
from app.tools import company_lookup, ToolFailure

ICP = {"industries":["SaaS","Fintech"],"min_employees":20,
       "max_employees":300,"regions":["US"]}

def run_with_model():
    graph=build_graph(MemorySaver())
    config={"configurable":{"thread_id":str(uuid.uuid4())}}
    return graph,config,graph.invoke({
        "company_id":"c01","tenant_id":"test","icp":ICP,
        "agentic_research":True,"llm_enabled":False,"sent":False
    },config)

def test_model_directed_research_enters_approval():
    with patch("app.agentic.model_research",side_effect=lambda cid: company_lookup(cid)) as model:
        graph,cfg,result=run_with_model()
    model.assert_called_once_with("c01")
    assert graph.get_state(cfg).interrupts
    assert result["route"]=="approval"
    assert result["sent"] is False

def test_model_directed_research_denial_terminates():
    with patch("app.agentic.model_research",side_effect=ToolFailure("Rejected model tool call")):
        graph,cfg,result=run_with_model()
    assert result["route"]=="failed"
    assert result["sent"] is False
    assert not graph.get_state(cfg).interrupts
