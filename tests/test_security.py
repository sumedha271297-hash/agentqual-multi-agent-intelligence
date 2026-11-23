import json
import uuid
import pytest
from fastapi.testclient import TestClient
from app.api import app
from app.security import validate_security_config

client = TestClient(app)
ICP = {"industries":["SaaS"],"min_employees":20,"max_employees":300,"regions":["US"]}

def auth(monkeypatch):
    monkeypatch.setenv("AGENTQUAL_TENANT_TOKENS", json.dumps({
        "tenant-a": "a"*32, "tenant-b": "b"*32}))

def test_requires_key_when_tenants_configured(monkeypatch):
    auth(monkeypatch)
    assert client.get("/companies").status_code == 401
    assert client.get("/companies",headers={"X-API-Key":"incorrect"}).status_code==401
    assert client.get("/companies",headers={"X-API-Key":"a"*32}).status_code==200

def test_thread_isolation_and_approval(monkeypatch):
    auth(monkeypatch)
    owner={"X-API-Key":"a"*32}
    foreign={"X-API-Key":"b"*32}
    run=client.post("/graph/run",json={"company_id":"c01","icp":ICP},headers=owner)
    assert run.status_code==200,run.text
    thread=run.json()["thread_id"]
    assert run.json()["awaiting_approval"]
    assert client.get(f"/graph/{thread}",headers=foreign).status_code==404
    assert client.post(f"/graph/{thread}/approve",json={"approved":True},headers=foreign).status_code==404
    result=client.post(f"/graph/{thread}/approve",json={"approved":True},headers=owner)
    assert result.status_code==200 and result.json()["state"]["sent"] is False

def test_metrics_auth(monkeypatch):
    auth(monkeypatch)
    assert client.get("/metrics").status_code==401
    response=client.get("/metrics",headers={"X-API-Key":"a"*32})
    assert response.status_code==200
    assert response.json()["observed_request_count"]>=1

def test_production_rejects_unconfigured_secret(monkeypatch):
    monkeypatch.setenv("APP_ENV","production")
    monkeypatch.delenv("AGENTQUAL_TENANT_TOKENS",raising=False)
    with pytest.raises(RuntimeError):
        validate_security_config()

def test_production_requires_database(monkeypatch):
    auth(monkeypatch)
    monkeypatch.setenv("APP_ENV","production")
    monkeypatch.delenv("DATABASE_URL",raising=False)
    with pytest.raises(RuntimeError):
        validate_security_config()

def test_duplicate_tokens_forbidden(monkeypatch):
    monkeypatch.setenv("AGENTQUAL_TENANT_TOKENS",
                       json.dumps({"a":"x"*32,"b":"x"*32}))
    with pytest.raises(RuntimeError):
        validate_security_config()
