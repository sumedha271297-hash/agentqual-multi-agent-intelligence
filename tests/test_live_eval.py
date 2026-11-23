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

def test_gemini_503_retries_once_then_succeeds(monkeypatch):
    from unittest.mock import patch
    class TemporaryServerError(Exception):
        code=503
        status="UNAVAILABLE"
    count={"n":0}
    def flaky(_):
        count["n"]+=1
        if count["n"]==1:
            raise TemporaryServerError("provider overloaded")
        return {"subject":"Valid subject","message":"This message is long enough.",
                "requires_approval":True,"sent":False}
    monkeypatch.setattr("app.gemini.generate_gemini_draft",flaky)
    with patch("scripts.evaluate_live.time.sleep") as pause:
        result=evaluate_live(["c01"],provider="gemini")
    assert count["n"]==2
    assert result["rows"][0]["schema_valid"] is True
    assert result["rows"][0]["attempts"]==2
    assert result["rows"][0]["retried_after_503"] is True
    pause.assert_called_once_with(2.0)

def test_gemini_503_max_two_attempts_and_preserves_error(monkeypatch):
    from unittest.mock import patch
    class TemporaryServerError(Exception):
        code=503
        status="UNAVAILABLE"
    calls=[]
    def unavailable(_):
        calls.append(1)
        raise TemporaryServerError("private data")
    monkeypatch.setattr("app.gemini.generate_gemini_draft",unavailable)
    with patch("scripts.evaluate_live.time.sleep"):
        result=evaluate_live(["c01"],provider="gemini")
    row=result["rows"][0]
    assert len(calls)==2
    assert row["http_status"]==503
    assert row["attempts"]==2
    assert row["schema_valid"] is False
    assert "private data" not in str(result)

def test_gemini_does_not_retry_non_transient_errors(monkeypatch):
    from unittest.mock import patch
    class BadRequest(Exception):
        code=404
        status="NOT_FOUND"
    calls=[]
    def not_found(_):
        calls.append(1)
        raise BadRequest("model unavailable")
    monkeypatch.setattr("app.gemini.generate_gemini_draft",not_found)
    with patch("scripts.evaluate_live.time.sleep") as pause:
        result=evaluate_live(["c01"],provider="gemini")
    assert len(calls)==1
    assert result["rows"][0]["attempts"]==1
    pause.assert_not_called()
