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
