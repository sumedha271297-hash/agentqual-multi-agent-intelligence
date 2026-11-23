"""Fake-model tests exercise actual tool selection without paying for inference."""
import pytest
from app.agentic import model_research
from app.tools import ToolFailure

class FakeReply:
    def __init__(self, calls):
        self.tool_calls = calls

class FakeModel:
    def __init__(self, calls):
        self.calls = calls
    def bind_tools(self, specs, tool_choice=None):
        assert specs[0]["function"]["name"] == "company_lookup"
        assert tool_choice == "required"
        return self
    def invoke(self, messages):
        assert "company_id" in messages[1][1]
        return FakeReply(self.calls)

def call(name="company_lookup", args=None):
    return {"name": name, "args": args or {"company_id": "c01"}}

def test_model_requests_and_executes_lookup():
    result = model_research("c01", FakeModel([call()]))
    assert result["data"]["id"] == "c01"
    assert result["metadata"]["tool_calls"] == 1
    assert result["metadata"]["mode"] == "model_directed"

@pytest.mark.parametrize("calls", [
    [],
    [call(), call()],
    [call("send_email")],
    [call(args={"company_id": "c02"})],
    [call(args={"company_id": "c01", "url": "https://invalid.example"})],
])
def test_invalid_tool_plans_fail_closed(calls):
    with pytest.raises(ToolFailure):
        model_research("c01", FakeModel(calls))

def test_wrong_record_missing_rejected():
    with pytest.raises(KeyError):
        model_research("missing", FakeModel([call(args={"company_id": "missing"})]))
