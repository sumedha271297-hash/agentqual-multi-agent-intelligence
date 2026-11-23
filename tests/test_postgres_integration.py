"""Runs in CI with actual PostgreSQL; skips locally without DATABASE_URL."""
import os
import uuid
import pytest
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.types import Command
from app.graph import build_graph

@pytest.mark.skipif(not os.getenv("DATABASE_URL"), reason="Postgres service not configured")
def test_resume_after_reopening_database_connection():
    url=os.environ["DATABASE_URL"]
    thread=str(uuid.uuid4())
    cfg={"configurable":{"thread_id":thread}}
    icp={"industries":["SaaS","Fintech"],"min_employees":20,
         "max_employees":300,"regions":["US"]}
    with PostgresSaver.from_conn_string(url) as saver:
        saver.setup()
        graph=build_graph(saver)
        first=graph.invoke({"company_id":"c01","icp":icp,"llm_enabled":False,"sent":False},cfg)
        assert first["sent"] is False
        assert graph.get_state(cfg).interrupts
    # A completely fresh saver and graph can load the pending interrupt.
    with PostgresSaver.from_conn_string(url) as saver:
        recovered=build_graph(saver)
        assert recovered.get_state(cfg).interrupts
        state=recovered.invoke(Command(resume=True),cfg)
        assert state["approved"] is True and state["sent"] is False
        assert not recovered.get_state(cfg).interrupts
