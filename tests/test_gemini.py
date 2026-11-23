"""Gemini adapter integration; mocked API to avoid charges."""
import json
from types import SimpleNamespace
import pytest
from fastapi.testclient import TestClient
from app.gemini import generate_gemini_draft
from app.api import app

FACTS={"name":"Northstar","industry":"SaaS","employees":120,"region":"US",
       "description":"Synthetic company"}

class FakeModels:
    def __init__(self,payload=None):
        self.payload=payload if payload is not None else {
            "subject":"Exploring Northstar fit",
            "message":"Hello Northstar team, would you be open to an introductory conversation?"}
        self.called=False
    def generate_content(self,**kwargs):
        self.called=True
        assert kwargs["config"].response_mime_type=="application/json"
        return SimpleNamespace(parsed=self.payload,text=json.dumps(self.payload))
class FakeClient:
    def __init__(self,payload=None):
        self.models=FakeModels(payload)

def test_gemini_structured_output():
    client=FakeClient()
    draft=generate_gemini_draft(FACTS,client=client)
    assert client.models.called
    assert draft["generated_by"]=="gemini"
    assert draft["requires_approval"] and not draft["sent"]

def test_gemini_invalid_schema():
    with pytest.raises(ValueError):
        generate_gemini_draft(FACTS,client=FakeClient({"subject":"x","message":"y"}))

def test_gemini_missing_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY",raising=False)
    with pytest.raises(RuntimeError,match="GEMINI_API_KEY"):
        generate_gemini_draft(FACTS)

def test_gemini_api_requires_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY",raising=False)
    request={"company_id":"c01",
             "icp":{"industries":["SaaS"],"min_employees":20,
                    "max_employees":300,"regions":["US"]},
             "llm_enabled":True,"llm_provider":"gemini"}
    assert TestClient(app).post("/graph/run",json=request).status_code==422

def test_gemini_graph_requires_human_approval():
    from langgraph.checkpoint.memory import MemorySaver
    from app.graph import build_graph
    from unittest.mock import patch
    from uuid import uuid4
    graph=build_graph(MemorySaver())
    config={"configurable":{"thread_id":str(uuid4())}}
    icp={"industries":["SaaS"],"min_employees":20,"max_employees":300,"regions":["US"]}
    fake={"subject":"Exploring a fit",
          "message":"Hello, would you like to discuss a potential fit with our offering?",
          "requires_approval":True,"sent":False,"generated_by":"gemini"}
    with patch("app.gemini.generate_gemini_draft",return_value=fake) as mocked:
        state=graph.invoke({"company_id":"c01","icp":icp,"llm_enabled":True,
                            "llm_provider":"gemini","sent":False},config)
    mocked.assert_called_once()
    assert graph.get_state(config).interrupts
    assert state["draft"]["generated_by"]=="gemini"
    assert state["sent"] is False
