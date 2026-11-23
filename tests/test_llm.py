"""No API keys or real network calls required."""
import pytest
from app.llm import OutreachDraft, generate_llm_draft

FACTS = {"name": "Northstar Analytics", "industry": "SaaS", "employees": 120,
         "region": "US", "description": "Synthetic company"}

class FakeStructured:
    def invoke(self, messages):
        return OutreachDraft(subject="Discussing Northstar Analytics",
                             message="Hello, I saw your SaaS company and would like to explore a conversation.")

class FakeModel:
    def with_structured_output(self, schema, method):
        assert schema is OutreachDraft and method == "json_schema"
        return FakeStructured()

def test_mock_llm_structured_output():
    result = generate_llm_draft(FACTS, llm=FakeModel())
    assert result["generated_by"] == "llm"
    assert result["requires_approval"] and not result["sent"]
    assert set(result["source_fields"]) == set(FACTS)

def test_no_key_without_injected_llm(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="OPENAI_API_KEY"):
        generate_llm_draft(FACTS)
