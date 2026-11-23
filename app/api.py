"""API with optional durable PostgreSQL checkpoint lifecycle.

Default memory mode is local development only. Set DATABASE_URL to enable
PostgresSaver and verify interrupt state across independent application starts.
"""
import os
import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, model_validator
from app.core import workflow_offline, load_companies

try:
    from langgraph.checkpoint.memory import MemorySaver
    from langgraph.types import Command
    from app.graph import build_graph
    _development_graph = build_graph(MemorySaver())
except ImportError:
    _development_graph = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        from langgraph.checkpoint.postgres import PostgresSaver
        # Explicit context keeps the database connection alive for API requests.
        with PostgresSaver.from_conn_string(database_url) as saver:
            saver.setup()
            app.state.graph = build_graph(saver)
            app.state.persistence = "postgres"
            yield
    else:
        app.state.graph = _development_graph
        app.state.persistence = "memory" if _development_graph else "unavailable"
        yield

app = FastAPI(title="AgentQual", version="0.2.0",
              description="Independent candidate demo. Never sends email.", lifespan=lifespan)
# This also supports tests using TestClient without explicit lifespan context.
app.state.graph = _development_graph
app.state.persistence = "memory" if _development_graph else "unavailable"

class ICP(BaseModel):
    industries: list[str] = Field(min_length=1)
    min_employees: int = Field(ge=0)
    max_employees: int = Field(ge=0)
    regions: list[str] = Field(min_length=1)

    @model_validator(mode="after")
    def valid_employee_range(self):
        if self.max_employees < self.min_employees:
            raise ValueError("Maximum employees must be >= minimum employees")
        return self

class RunRequest(BaseModel):
    company_id: str
    icp: ICP
    llm_enabled: bool = False

class ApprovalRequest(BaseModel):
    approved: bool

def active_graph():
    graph = app.state.graph
    if graph is None:
        raise HTTPException(503, "LangGraph dependencies unavailable")
    return graph

@app.get("/health")
def health():
    return {"status": "ok", "persistence": app.state.persistence,
            "llm_configured": bool(os.getenv("OPENAI_API_KEY")),
            "outbound_messaging": False}

@app.get("/companies")
def companies():
    return list(load_companies())

@app.post("/offline/run")
def offline_run(request: RunRequest):
    try:
        return workflow_offline(request.company_id, request.icp.model_dump())
    except KeyError as exc:
        raise HTTPException(404, "Unknown company") from exc

@app.post("/graph/run")
def graph_run(request: RunRequest):
    graph = active_graph()
    if request.company_id not in load_companies():
        raise HTTPException(404, "Unknown company")
    if request.llm_enabled and not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(422, "OPENAI_API_KEY required for LLM mode")
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    state = graph.invoke({"company_id": request.company_id, "icp": request.icp.model_dump(),
                          "llm_enabled": request.llm_enabled, "approved": False,
                          "sent": False}, config=config)
    snapshot = graph.get_state(config)
    return {"thread_id": thread_id, "state": state,
            "awaiting_approval": bool(snapshot.interrupts)}

@app.get("/graph/{thread_id}")
def graph_state(thread_id: uuid.UUID):
    graph = active_graph()
    snapshot = graph.get_state({"configurable": {"thread_id": str(thread_id)}})
    if not snapshot.values:
        raise HTTPException(404, "Unknown thread")
    return {"thread_id": str(thread_id), "state": snapshot.values,
            "awaiting_approval": bool(snapshot.interrupts)}

@app.post("/graph/{thread_id}/approve")
def graph_approve(thread_id: uuid.UUID, request: ApprovalRequest):
    graph = active_graph()
    config = {"configurable": {"thread_id": str(thread_id)}}
    snapshot = graph.get_state(config)
    if not snapshot.values:
        raise HTTPException(404, "Unknown thread")
    if not snapshot.interrupts:
        raise HTTPException(409, "Thread is not awaiting approval")
    state = graph.invoke(Command(resume=request.approved), config=config)
    return {"thread_id": str(thread_id), "state": state, "sent": False}
