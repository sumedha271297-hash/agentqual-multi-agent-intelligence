"""Bounded candidate-demo API with tenant-bound approval threads."""
import os
import uuid
import time
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, Request
from pydantic import BaseModel, Field, model_validator
from app.core import workflow_offline, load_companies
from app.security import principal, require_owner, validate_security_config
from app.observability import record, summary

logger = logging.getLogger("agentqual.requests")

try:
    from langgraph.checkpoint.memory import MemorySaver
    from langgraph.types import Command
    from app.graph import build_graph
    _development_graph = build_graph(MemorySaver())
except ImportError:
    _development_graph = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    validate_security_config()
    url = os.getenv("DATABASE_URL")
    if url:
        from langgraph.checkpoint.postgres import PostgresSaver
        with PostgresSaver.from_conn_string(url) as saver:
            saver.setup()
            app.state.graph = build_graph(saver)
            app.state.persistence = "postgres"
            yield
    else:
        app.state.graph = _development_graph
        app.state.persistence = "memory" if _development_graph else "unavailable"
        yield

app = FastAPI(title="AgentQual", version="0.3.0",
              description="Independent portfolio demonstration. Never sends messages.", lifespan=lifespan)
app.state.graph = _development_graph
app.state.persistence = "memory" if _development_graph else "unavailable"

@app.middleware("http")
async def audit_request(request: Request, call_next):
    started = time.perf_counter()
    request_id = uuid.uuid4().hex
    status = 500
    try:
        response = await call_next(request)
        status = response.status_code
        response.headers["X-Request-ID"] = request_id
        return response
    finally:
        elapsed = (time.perf_counter() - started) * 1000
        # Use route template when available, never raw path/uuid
        route = request.scope.get("route")
        pattern = getattr(route, "path", "unmatched")
        record(request.method, pattern, status, elapsed)
        logger.info("request_id=%s method=%s route=%s status=%s duration_ms=%.1f",
                    request_id, request.method, pattern, status, elapsed)

class ICP(BaseModel):
    industries: list[str] = Field(min_length=1)
    min_employees: int = Field(ge=0)
    max_employees: int = Field(ge=0)
    regions: list[str] = Field(min_length=1)
    @model_validator(mode="after")
    def valid_range(self):
        if self.max_employees < self.min_employees:
            raise ValueError("max_employees must be >= min_employees")
        return self

class RunRequest(BaseModel):
    company_id: str
    icp: ICP
    llm_enabled: bool = False

class ApprovalRequest(BaseModel):
    approved: bool

def active_graph():
    if app.state.graph is None:
        raise HTTPException(503, "LangGraph unavailable")
    return app.state.graph

@app.get("/health")
def health():
    # health only; no account-level data or model configuration revealed
    return {"status": "ok"}

@app.get("/metrics")
def metrics(tenant_id: str = Depends(principal)):
    return summary()

@app.get("/companies")
def companies(tenant_id: str = Depends(principal)):
    return list(load_companies())

@app.post("/offline/run")
def offline_run(request: RunRequest, tenant_id: str = Depends(principal)):
    try:
        return workflow_offline(request.company_id, request.icp.model_dump())
    except KeyError as exc:
        raise HTTPException(404, "Unknown company") from exc

@app.post("/graph/run")
def graph_run(request: RunRequest, tenant_id: str = Depends(principal)):
    graph = active_graph()
    if request.company_id not in load_companies():
        raise HTTPException(404, "Unknown company")
    if request.llm_enabled and not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(422, "OPENAI_API_KEY required for LLM mode")
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    state = graph.invoke({"company_id": request.company_id,
                          "tenant_id": tenant_id,
                          "icp": request.icp.model_dump(),
                          "llm_enabled": request.llm_enabled,
                          "approved": False, "sent": False}, config=config)
    snapshot = graph.get_state(config)
    return {"thread_id": thread_id, "state": state,
            "awaiting_approval": bool(snapshot.interrupts)}

@app.get("/graph/{thread_id}")
def graph_state(thread_id: uuid.UUID, tenant_id: str = Depends(principal)):
    graph = active_graph()
    snapshot = graph.get_state({"configurable": {"thread_id": str(thread_id)}})
    require_owner(snapshot, tenant_id)
    return {"thread_id": str(thread_id), "state": snapshot.values,
            "awaiting_approval": bool(snapshot.interrupts)}

@app.post("/graph/{thread_id}/approve")
def graph_approve(thread_id: uuid.UUID, request: ApprovalRequest,
                  tenant_id: str = Depends(principal)):
    graph = active_graph()
    config = {"configurable": {"thread_id": str(thread_id)}}
    snapshot = graph.get_state(config)
    require_owner(snapshot, tenant_id)
    if not snapshot.interrupts:
        raise HTTPException(409, "Thread is not awaiting approval")
    state = graph.invoke(Command(resume=request.approved), config=config)
    return {"thread_id": str(thread_id), "state": state, "sent": False}
