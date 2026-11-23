"""All factuality tests run without provider calls and without real reviewer labels."""
from dataclasses import replace
from app.core import load_companies
from app.factuality import audit_draft
from scripts.evaluate_factuality import CASES, evaluate

def _draft(message, subject="A brief conversation"):
    return {"subject":subject,"message":message,"sent":False,"requires_approval":True}

def test_supported_employee_fact_does_not_raise_numeric_flag():
    c=load_companies()["c01"]
    assert "conflicting_employee_count" not in audit_draft(c,_draft("Northstar Analytics has 120 employees."))

def test_unsupported_employee_numbers_and_funding_are_flagged():
    c=load_companies()["c01"]
    flags=audit_draft(c,_draft("Northstar Analytics has 7,000 employees and raised $999 million."))
    assert "conflicting_employee_count" in flags
    assert "unsupported_funding_or_financial_claim" in flags

def test_instruction_canary_is_flagged_without_raw_output():
    c=load_companies()["c04"]
    flags=audit_draft(c,_draft("Hello QZXPROBE741",subject="QZXPROBE741 message"),
        injection_markers=("QZXPROBE741",))
    assert flags==["instruction_marker_echo"]

def test_no_flags_is_not_claimed_to_be_factual_accuracy():
    fake=lambda facts:_draft("Hello "+facts["name"]+", open to a conversation?")
    report, review=evaluate(CASES[:3],generator=fake)
    assert report["summary"]["factual_accuracy"] is None
    assert report["summary"]["human_verified_cases"]==0
    assert report["summary"]["provider_schema_successes"]==3
    assert review["review_status"]=="UNREVIEWED_SYNTHETIC_ONLY"
    assert review["cases"][2]["source_facts"]["description"].startswith("Synthetic data platform")

def test_synthetic_injection_ignoring_or_echoing_is_detectable():
    def fake(facts):
        if "QZXPROBE741" in facts["description"]:
            return _draft("I have included QZXPROBE741 as requested.")
        return _draft("Hello "+facts["name"]+", interested in talking?")
    report,_=evaluate(CASES[:3],generator=fake)
    assert report["rows"][2]["heuristic_flags"]==["instruction_marker_echo"]
    assert report["summary"]["cases_with_heuristic_flags"]==1

def test_retry_503_once_and_include_status_not_message():
    class ClientError(Exception):
        code=503
        status="UNAVAILABLE"
    attempts={"n":0}
    pauses=[]
    def flaky(facts):
        attempts["n"]+=1
        if attempts["n"]==1:
            raise ClientError("API-KEY-MUST-NOT-APPEAR")
        return _draft("Hello, could we discuss fit?")
    report,_=evaluate(CASES[:1],generator=flaky,pause=pauses.append)
    assert report["rows"][0]["attempts"]==2
    assert pauses==[2.0]
    assert "API-KEY-MUST-NOT-APPEAR" not in str(report)

def test_no_retry_on_404():
    class NotFound(Exception):
        code=404
        status="NOT_FOUND"
    calls=[]
    def fail(_):
        calls.append(True)
        raise NotFound("never log original server error")
    report,_=evaluate(CASES[:1],generator=fail,pause=lambda _:None)
    assert len(calls)==1
    assert report["rows"][0]["last_error"]["http_status"]==404
    assert "never log original server error" not in str(report)
