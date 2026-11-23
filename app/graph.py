"""Explicit LangGraph workflow with fail-closed LLM and human review."""
from typing import TypedDict, Optional
from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt
from app.core import Company, qualify, generate_recommendation, validate_draft
from app.tools import company_lookup, ToolFailure

class AgentState(TypedDict, total=False):
    company_id: str
    agentic_research: bool
    agentic_qualification: bool
    reasoning: dict
    approval_request_id: Optional[str]
    tenant_id: str
    icp: dict
    llm_enabled: bool
    llm_provider: str
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
        if state.get("agentic_research", False):
            from app.agentic import model_research
            result = model_research(state["company_id"])
        else:
            result = company_lookup(state["company_id"])
        return {"evidence": result["data"], "tool_metadata": result["metadata"],
                "route": "researched", "sent": False}
    except (KeyError, ToolFailure, ValueError, RuntimeError, TimeoutError, ConnectionError) as exc:
        return {"route": "failed", "error": type(exc).__name__, "sent": False}

def route_research(state: AgentState):
    return "failed" if state["route"] == "failed" else "researched"

def qualification_agent(state: AgentState):
    company = Company(**state["evidence"])
    result = qualify(company, state["icp"])
    if state.get("agentic_qualification", False):
        try:
            from app.reasoning import assess
            reasoned = assess(company, state["icp"])
            route = {"QUALIFY": "outreach", "REJECT": "rejected",
                     "REVIEW": "needs_review"}[reasoned["verdict"]]
            return {"qualification": result, "reasoning": reasoned, "route": route}
        except Exception:
            return {"qualification": result, "reasoning": {"verdict": "REVIEW",
                    "reason": "Model evaluation failed"}, "route": "needs_review"}
    return {"qualification": result, "route": "outreach" if result["qualified"] else "rejected"}

def route_qualification(state: AgentState):
    return state["route"]

def outreach_agent(state: AgentState):
    try:
        if state.get("llm_enabled", False):
            from app.llm import generate_llm_draft
            if state.get("llm_provider", "openai") == "gemini":
                from app.gemini import generate_gemini_draft
                draft = generate_gemini_draft(state["evidence"])
            else:
                draft = generate_llm_draft(state["evidence"])
        else:
            draft = generate_recommendation(Company(**state["evidence"]), state["qualification"])
        if draft is None or not validate_draft(draft):
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
    approved = response.get("approved") is True if isinstance(response, dict) else response is True
    request_id = response.get("request_id") if isinstance(response, dict) else None
    return {"approved": approved, "approval_request_id": request_id, "sent": False,
            "route": "approved" if approved else "rejected_by_reviewer"}

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
                                  {"outreach": "outreach_agent", "rejected": END, "needs_review": END})
    builder.add_conditional_edges("outreach_agent", route_outreach,
                                  {"approval": "approval_gate", "failed": END})
    builder.add_edge("approval_gate", END)
    return builder.compile(checkpointer=checkpointer)
