import uuid
from fastapi.testclient import TestClient
from app.api import app

client = TestClient(app)
ICP={"industries":["SaaS","Fintech"],"min_employees":20,"max_employees":300,"regions":["US"]}

def test_api_graph_pause_resume():
    run=client.post("/graph/run",json={"company_id":"c01","icp":ICP})
    assert run.status_code==200,run.text
    data=run.json()
    assert data["awaiting_approval"]
    tid=data["thread_id"]
    assert client.get(f"/graph/{tid}").json()["awaiting_approval"]
    approved=client.post(f"/graph/{tid}/approve",json={"approved":True})
    assert approved.status_code==200,approved.text
    assert approved.json()["state"]["approved"] is True
    assert approved.json()["sent"] is False
    assert client.post(f"/graph/{tid}/approve",json={"approved":True}).status_code==409

def test_invalid_thread_rejected():
    tid=str(uuid.uuid4())
    assert client.post(f"/graph/{tid}/approve",json={"approved":True}).status_code==404

def test_llm_requires_configured_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY",raising=False)
    result=client.post("/graph/run",json={"company_id":"c01","icp":ICP,"llm_enabled":True})
    assert result.status_code==422

def test_invalid_icp():
    data={"company_id":"c01","icp":dict(ICP,min_employees=400,max_employees=20)}
    assert client.post("/graph/run",json=data).status_code==422
