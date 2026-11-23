"""Approval replay safety under concurrent calls."""
import json
import uuid
from concurrent.futures import ThreadPoolExecutor
from fastapi.testclient import TestClient
from app.api import app

ICP = {"industries":["SaaS"],"min_employees":20,"max_employees":300,"regions":["US"]}

def _setup(monkeypatch):
    monkeypatch.setenv("AGENTQUAL_TENANT_TOKENS",json.dumps({"org-a":"a"*32}))
    return {"X-API-Key":"a"*32}

def _run(client,headers):
    reply=client.post("/graph/run",json={"company_id":"c01","icp":ICP},headers=headers)
    assert reply.status_code==200,reply.text
    assert reply.json()["awaiting_approval"]
    return reply.json()["thread_id"]

def test_identical_concurrent_approval_key_replays(monkeypatch):
    headers=_setup(monkeypatch)
    key=str(uuid.uuid4())
    headers["Idempotency-Key"]=key
    with TestClient(app) as client:
        thread=_run(client,headers)
        def approve(_):
            response=client.post(f"/graph/{thread}/approve",json={"approved":True},headers=headers)
            return response.status_code,response.json()
        with ThreadPoolExecutor(max_workers=2) as pool:
            responses=list(pool.map(approve,range(2)))
        assert [r[0] for r in responses]==[200,200]
        assert sorted(r[1]["replayed"] for r in responses)==[False,True]
        assert all(r[1]["state"]["sent"] is False for r in responses)

def test_distinct_keys_do_not_double_approve(monkeypatch):
    headers=_setup(monkeypatch)
    with TestClient(app) as client:
        thread=_run(client,headers)
        def approve(number):
            h={**headers,"Idempotency-Key":str(uuid.uuid4())}
            return client.post(f"/graph/{thread}/approve",json={"approved":True},headers=h).status_code
        with ThreadPoolExecutor(max_workers=2) as pool:
            codes=list(pool.map(approve,range(2)))
        assert sorted(codes)==[200,409]

def test_same_key_opposite_decision_conflicts(monkeypatch):
    headers=_setup(monkeypatch)
    headers["Idempotency-Key"]=str(uuid.uuid4())
    with TestClient(app) as client:
        thread=_run(client,headers)
        assert client.post(f"/graph/{thread}/approve",json={"approved":False},headers=headers).status_code==200
        assert client.post(f"/graph/{thread}/approve",json={"approved":True},headers=headers).status_code==409
