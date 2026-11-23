"""Bounded candidate-demo API with tenant-bound approval threads."""
import os
import uuid
import time
import logging
from typing import Literal
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, Request, Header
from pydantic import BaseModel, Field, model_validator
from app.core import workflow_offline, load_companies
from app.security import principal, require_owner, validate_security_config
from app.observability import record, summary
from app.approval_lock import approval_lock, ApprovalBusy

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
            try:
                yield
            finally:
                # Prevent stale graph references to a closed DB connection
                # when multiple lifespan contexts run in one process.
                app.state.graph = _development_graph
                app.state.persistence = "memory" if _development_graph else "unavailable"
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
    llm_provider: Literal['openai', 'gemini'] = 'openai'
    agentic_research: bool = False
    agentic_qualification: bool = False

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
    if (request.agentic_research or request.agentic_qualification) and not os.getenv('OPENAI_API_KEY'):
        raise HTTPException(422, 'OPENAI_API_KEY required for agentic research')
    if request.llm_enabled:
        required = "GEMINI_API_KEY" if request.llm_provider == "gemini" else "OPENAI_API_KEY"
        if not os.getenv(required):
            raise HTTPException(422, f"{required} required for LLM mode")
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    state = graph.invoke({"company_id": request.company_id,
                          "tenant_id": tenant_id,
                          "icp": request.icp.model_dump(),
                          "llm_enabled": request.llm_enabled,
                          "agentic_research": request.agentic_research,
                          "agentic_qualification": request.agentic_qualification,
                          "llm_provider": request.llm_provider,
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
                  tenant_id: str = Depends(principal),
                  idempotency_key: uuid.UUID | None = Header(default=None, alias="Idempotency-Key")):
    """Serializes approval and resumes graph once.

    Retrying with the same idempotency key and same decision returns the
    durable result instead of re-running. Other completed requests get 409.
    """
    graph = active_graph()
    config = {"configurable": {"thread_id": str(thread_id)}}
    try:
        with approval_lock(str(thread_id)):
            snapshot = graph.get_state(config)
            require_owner(snapshot, tenant_id)
            if not snapshot.interrupts:
                state = snapshot.values
                if (idempotency_key and state.get("approval_request_id") == str(idempotency_key)
                        and state.get("approved") is request.approved):
                    return {"thread_id": str(thread_id), "state": state,
                            "sent": False, "replayed": True}
                raise HTTPException(409, "Thread is not awaiting approval")
            decision = {"approved": request.approved,
                        "request_id": str(idempotency_key) if idempotency_key else None}
            state = graph.invoke(Command(resume=decision), config=config)
            return {"thread_id": str(thread_id), "state": state,
                    "sent": False, "replayed": False}
    except ApprovalBusy as exc:
        raise HTTPException(409, "Approval is already in progress") from exc
