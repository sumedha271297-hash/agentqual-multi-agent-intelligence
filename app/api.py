"""FastAPI application: deterministic local demo and resumable LangGraph endpoints."""
import uuid
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from app.core import workflow_offline, load_companies

app = FastAPI(title='AgentQual', version='0.1.0', description='Candidate portfolio demonstration; no external outreach')

class ICP(BaseModel):
    industries: list[str] = Field(min_length=1)
    min_employees: int = Field(ge=0)
    max_employees: int = Field(ge=0)
    regions: list[str] = Field(min_length=1)

class RunRequest(BaseModel):
    company_id: str
    icp: ICP

class ApprovalRequest(BaseModel):
    approved: bool

@app.get('/health')
def health():
    return {'status': 'ok', 'mode': 'offline baseline available'}

@app.get('/companies')
def companies():
    return list(load_companies())

@app.post('/offline/run')
def offline_run(request: RunRequest):
    if request.icp.max_employees < request.icp.min_employees:
        raise HTTPException(422, 'max_employees must be >= min_employees')
    try:
        return workflow_offline(request.company_id, request.icp.model_dump())
    except KeyError as exc:
        raise HTTPException(404, str(exc)) from exc

# In-memory checkpoint is for demonstration only; not multi-worker durable production storage.
try:
    from langgraph.checkpoint.memory import MemorySaver
    from langgraph.types import Command
    from app.graph import build_graph
    graph = build_graph(MemorySaver())
except ImportError:
    graph = None

@app.post('/graph/run')
def graph_run(request: RunRequest):
    if graph is None:
        raise HTTPException(503, 'Install LangGraph dependencies to enable graph endpoints')
    if request.icp.max_employees < request.icp.min_employees:
        raise HTTPException(422, 'Invalid employee range')
    if request.company_id not in load_companies():
        raise HTTPException(404, 'Unknown company')
    thread_id = str(uuid.uuid4())
    config = {'configurable': {'thread_id': thread_id}}
    state = graph.invoke({'company_id': request.company_id, 'icp': request.icp.model_dump(), 'sent': False}, config=config)
    snapshot = graph.get_state(config)
    return {'thread_id': thread_id, 'state': state, 'awaiting_approval': bool(snapshot.interrupts)}

@app.post('/graph/{thread_id}/approve')
def graph_approve(thread_id: str, request: ApprovalRequest):
    if graph is None:
        raise HTTPException(503, 'LangGraph unavailable')
    config = {'configurable': {'thread_id': thread_id}}
    snapshot = graph.get_state(config)
    if not snapshot.values:
        raise HTTPException(404, 'Unknown thread')
    if not snapshot.interrupts:
        raise HTTPException(409, 'Thread is not awaiting approval')
    state = graph.invoke(Command(resume=request.approved), config=config)
    return {'thread_id': thread_id, 'state': state}
