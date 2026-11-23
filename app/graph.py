"""Explicit LangGraph workflow with fail-closed LLM and human review."""
from typing import TypedDict, Optional
from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt
from app.core import Company, qualify, generate_recommendation, validate_draft
from app.tools import company_lookup, ToolFailure

class AgentState(TypedDict, total=False):
    company_id: str
    tenant_id: str
    icp: dict
    llm_enabled: bool
    evidence: dict
    tool_metadata: dict
    qualification: dict
    draft: Optional[dict]
    route: str
    error: Optional[str]
    approved: bool
    sent: bool

def research_agent(state: AgentState):
    try:
        result = company_lookup(state["company_id"])
        return {"evidence": result["data"], "tool_metadata": result["metadata"],
                "route": "researched", "sent": False}
    except (KeyError, ToolFailure) as exc:
        return {"route": "failed", "error": type(exc).__name__, "sent": False}

def route_research(state: AgentState):
    return "failed" if state["route"] == "failed" else "researched"

def qualification_agent(state: AgentState):
    company = Company(**state["evidence"])
    result = qualify(company, state["icp"])
    return {"qualification": result, "route": "outreach" if result["qualified"] else "rejected"}

def route_qualification(state: AgentState):
    return state["route"]

def outreach_agent(state: AgentState):
    try:
        if state.get("llm_enabled", False):
            from app.llm import generate_llm_draft
            draft = generate_llm_draft(state["evidence"])
        else:
            draft = generate_recommendation(Company(**state["evidence"]), state["qualification"])
        if not validate_draft(draft):
            raise ValueError("Invalid draft schema")
        return {"draft": draft, "route": "approval", "sent": False}
    except (ValueError, RuntimeError, TimeoutError, ConnectionError, ImportError) as exc:
        # Do not silently switch to an offline draft after provider failure.
        return {"route": "failed", "draft": None, "error": type(exc).__name__, "sent": False}
    except Exception:
        # Provider SDKs may raise different errors; do not leak internals or approve.
        return {"route": "failed", "draft": None, "error": "ProviderError", "sent": False}

def route_outreach(state: AgentState):
    return "failed" if state["route"] == "failed" else "approval"

def approval_gate(state: AgentState):
    response = interrupt({"company_id": state["company_id"], "draft": state["draft"],
                          "question": "Approve this draft for manual use? No message is sent."})
    return {"approved": response is True, "sent": False,
            "route": "approved" if response is True else "rejected_by_reviewer"}

def build_graph(checkpointer=None):
    builder = StateGraph(AgentState)
    builder.add_node("research_agent", research_agent)
    builder.add_node("qualification_agent", qualification_agent)
    builder.add_node("outreach_agent", outreach_agent)
    builder.add_node("approval_gate", approval_gate)
    builder.add_edge(START, "research_agent")
    builder.add_conditional_edges("research_agent", route_research,
                                  {"researched": "qualification_agent", "failed": END})
    builder.add_conditional_edges("qualification_agent", route_qualification,
                                  {"outreach": "outreach_agent", "rejected": END})
    builder.add_conditional_edges("outreach_agent", route_outreach,
                                  {"approval": "approval_gate", "failed": END})
    builder.add_edge("approval_gate", END)
    return builder.compile(checkpointer=checkpointer)
