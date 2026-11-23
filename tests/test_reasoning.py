from types import SimpleNamespace
import pytest
from app.reasoning import assess, ReasonedDecision
from app.core import Company

ICP={"industries":["SaaS"],"min_employees":20,"max_employees":300,"regions":["US"]}
A=Company("x","Acme","SaaS",100,"US","Synthetic company")
B=Company("y","Bizz","Retail",100,"US","Synthetic company")

class FakeModel:
    def __init__(self, verdict): self.verdict=verdict
    def with_structured_output(self, schema, method):
        assert schema is ReasonedDecision
        assert method=="json_schema"
        return self
    def invoke(self, messages):
        return ReasonedDecision(verdict=self.verdict,reason="Evidence from matching fields",
                                evidence_fields=["industry","region"])

def test_model_qualifies_matching():
    assert assess(A,ICP,FakeModel("QUALIFY"))["verdict"]=="QUALIFY"

def test_model_rejects():
    assert assess(A,ICP,FakeModel("REJECT"))["verdict"]=="REJECT"

def test_model_abstains():
    assert assess(A,ICP,FakeModel("REVIEW"))["verdict"]=="REVIEW"

def test_guardrail_overrides_unsupported_positive():
    result=assess(B,ICP,FakeModel("QUALIFY"))
    assert result["verdict"]=="REVIEW" and result["guardrail_overrode"]

def test_missing_key_fails_closed(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY",raising=False)
    with pytest.raises(RuntimeError):
        assess(A,ICP)
