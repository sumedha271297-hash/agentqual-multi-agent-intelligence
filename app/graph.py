"""LangGraph workflow with bounded tool execution and resumable human approval.
No autonomous web browsing, email sending, or unverified factual enrichment.
"""
from typing import TypedDict, Optional
from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt
from app.core import Company, qualify, generate_recommendation, validate_draft
from app.tools import company_lookup, ToolFailure

class AgentState(TypedDict, total=False):
    company_id: str
    icp: dict
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
        result = company_lookup(state['company_id'])
        return {'evidence': result['data'], 'tool_metadata': result['metadata'], 'route': 'researched'}
    except (KeyError, ToolFailure) as exc:
        return {'route': 'failed', 'error': type(exc).__name__, 'sent': False}

def route_research(state: AgentState):
    return 'failed' if state['route'] == 'failed' else 'researched'

def qualification_agent(state: AgentState):
    company = Company(**state['evidence'])
    result = qualify(company, state['icp'])
    return {'qualification': result, 'route': 'outreach' if result['qualified'] else 'rejected'}

def route_qualification(state: AgentState):
    return state['route']

def outreach_agent(state: AgentState):
    company = Company(**state['evidence'])
    draft = generate_recommendation(company, state['qualification'])
    if not validate_draft(draft):
        return {'route': 'failed', 'error': 'InvalidDraft', 'sent': False}
    return {'draft': draft, 'route': 'approval'}

def route_outreach(state: AgentState):
    return 'failed' if state['route'] == 'failed' else 'approval'

def approval_gate(state: AgentState):
    response = interrupt({'company_id': state['company_id'], 'draft': state['draft'],
                          'question': 'Approve draft for manual use? No message will be sent.'})
    return {'approved': response is True, 'sent': False,
            'route': 'approved' if response is True else 'rejected_by_reviewer'}

def build_graph(checkpointer=None):
    graph = StateGraph(AgentState)
    graph.add_node('research_agent', research_agent)
    graph.add_node('qualification_agent', qualification_agent)
    graph.add_node('outreach_agent', outreach_agent)
    graph.add_node('approval_gate', approval_gate)
    graph.add_edge(START, 'research_agent')
    graph.add_conditional_edges('research_agent', route_research,
                                {'researched': 'qualification_agent', 'failed': END})
    graph.add_conditional_edges('qualification_agent', route_qualification,
                                {'outreach': 'outreach_agent', 'rejected': END})
    graph.add_conditional_edges('outreach_agent', route_outreach,
                                {'approval': 'approval_gate', 'failed': END})
    graph.add_edge('approval_gate', END)
    return graph.compile(checkpointer=checkpointer)
