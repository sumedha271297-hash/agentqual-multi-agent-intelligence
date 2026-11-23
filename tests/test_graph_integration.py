"""True LangGraph integration: run / interrupt / resume / reject / fail closed."""
import uuid
from unittest.mock import patch
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command
from app.graph import build_graph
from app.tools import ToolFailure
from app.core import load_companies

ICP = {"industries": ["SaaS", "Fintech"], "min_employees": 20,
       "max_employees": 300, "regions": ["US"]}

def new_run(cid="c01", llm=False):
    graph = build_graph(MemorySaver())
    config = {"configurable": {"thread_id": str(uuid.uuid4())}}
    result = graph.invoke({"company_id": cid, "icp": ICP, "llm_enabled": llm, "sent": False}, config)
    return graph, config, result

def test_qualified_interrupt_then_approve():
    graph, config, state = new_run()
    assert graph.get_state(config).interrupts
    assert state["sent"] is False
    resumed = graph.invoke(Command(resume=True), config)
    assert resumed["approved"] is True and resumed["sent"] is False
    assert resumed["route"] == "approved"
    assert not graph.get_state(config).interrupts

def test_reject_approval():
    graph, config, _ = new_run()
    result = graph.invoke(Command(resume=False), config)
    assert result["approved"] is False and result["route"] == "rejected_by_reviewer"
    assert result["sent"] is False

def test_disqualified_never_interrupts():
    graph, config, result = new_run("c02")
    assert result["route"] == "rejected"
    assert not graph.get_state(config).interrupts

def test_tool_failure_stops_graph():
    with patch("app.graph.company_lookup", side_effect=ToolFailure("offline")):
        graph, config, result = new_run()
    assert result["route"] == "failed" and result["sent"] is False
    assert not graph.get_state(config).interrupts

def test_llm_failure_fails_closed():
    with patch("app.llm.generate_llm_draft", side_effect=TimeoutError("provider timeout")):
        graph, config, result = new_run(llm=True)
    assert result["route"] == "failed"
    assert result["draft"] is None
    assert not graph.get_state(config).interrupts
