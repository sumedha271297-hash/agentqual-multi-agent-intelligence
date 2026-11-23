from scripts.evaluate_resilience import measure

def test_failure_injection_report():
    result=measure()
    assert result["kind"]=="synthetic_failure_injection"
    assert result["case_count"]==3
    assert result["passed_count"]==3
    assert all(case["sent"] is False for case in result["cases"])
