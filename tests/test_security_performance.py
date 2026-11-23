"""Security policy tests use malicious data and mocked model results."""
import os
from fastapi.testclient import TestClient
from app.api import app
from scripts.security_matrix import run as redteam
from scripts.performance_smoke import measure,percentile
from app.core import Company
from app.reasoning import assess
from unittest.mock import patch
from langgraph.checkpoint.memory import MemorySaver
from app.graph import build_graph
import uuid

ICP={"industries":["SaaS"],"min_employees":20,"max_employees":300,"regions":["US"]}

def test_security_matrix_all_blocked():
    report=redteam()
    assert report["blocked"]==report["total"]==6

def test_local_reviewer_shell_not_exposed_in_production(monkeypatch):
    monkeypatch.setenv("APP_ENV","production")
    client=TestClient(app,raise_server_exceptions=False)
    response=client.get("/demo")
    assert response.status_code==404

def test_reviewer_shell_has_security_headers(monkeypatch):
    monkeypatch.setenv("APP_ENV","development")
    client=TestClient(app)
    page=client.get("/demo")
    script=client.get("/demo/app.js")
    assert page.status_code==200 and "Content-Security-Policy" in page.headers
    assert "local" in page.text.lower()
    assert script.status_code==200
    assert 'localStorage' not in script.text
    assert 'sessionStorage' not in script.text

def test_none_draft_cannot_enter_approval():
    graph=build_graph(MemorySaver())
    cfg={"configurable":{"thread_id":str(uuid.uuid4())}}
    with patch("app.graph.generate_recommendation",return_value=None):
        r=graph.invoke({"company_id":"c01","icp":ICP,"tenant_id":"test","sent":False},cfg)
    assert r["route"]=="failed" and r.get("draft") is None
    assert not graph.get_state(cfg).interrupts

def test_percentile_definitions():
    assert percentile([1,2,3,4,5],95)==5
    assert percentile([1,2,3,4,5],50)==3

def test_bounded_smoke_performance_report():
    result=measure(request_count=8,workers=2)
    assert result["safe_successes"]==8
    assert result["failures"]==0
