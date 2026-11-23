from scripts.evaluate_live import evaluate_live

def test_live_evaluation_stubbed(monkeypatch):
    monkeypatch.setattr("scripts.evaluate_live.generate_llm_draft",
                        lambda _:{"subject":"subject","message":"draft content",
                                  "requires_approval":True,"sent":False})
    result=evaluate_live(["c01","c04"])
    assert result["metrics"]["total"]==2
    assert result["metrics"]["schema_success_rate"]==1.0
    assert result["evaluation_type"]=="LIVE_PROVIDER_SCHEMAS_ONLY"

def test_provider_error_captured_not_faked(monkeypatch):
    def fail(_):
        raise TimeoutError("provider unavailable")
    monkeypatch.setattr("scripts.evaluate_live.generate_llm_draft",fail)
    result=evaluate_live(["c01"])
    assert result["metrics"]["schema_success_rate"]==0
    assert result["rows"][0]["error_type"]=="TimeoutError"

def test_invalid_schema_is_not_counted_as_success(monkeypatch):
    monkeypatch.setattr("scripts.evaluate_live.generate_llm_draft",
                        lambda _: {"subject":"", "message":"", "requires_approval":False,"sent":False})
    result=evaluate_live(["c01"])
    assert result["metrics"]["successful_schema_outputs"]==0
    assert result["rows"][0]["status"]=="invalid_schema"

def test_provider_http_status_is_recorded_without_secret_text(monkeypatch):
    class FakeClientError(Exception):
        code=400
        status="INVALID_ARGUMENT"
    def fail(_):
        raise FakeClientError("never-log-secret-value")
    monkeypatch.setattr("scripts.evaluate_live.generate_llm_draft", fail)
    result=evaluate_live(["c01"])
    row=result["rows"][0]
    assert row["http_status"]==400
    assert row["provider_status"]=="INVALID_ARGUMENT"
    assert "never-log-secret-value" not in str(result)

def test_untrusted_provider_diagnostics_are_not_recorded(monkeypatch):
    class FakeClientError(Exception):
        code="invalid"
        status="never-log-secret-value"
    def fail(_):
        raise FakeClientError("never-log-secret-value")
    monkeypatch.setattr("scripts.evaluate_live.generate_llm_draft", fail)
    row=evaluate_live(["c01"])["rows"][0]
    assert row["http_status"] is None
    assert row["provider_status"] is None
