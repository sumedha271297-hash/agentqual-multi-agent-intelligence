from scripts.demo import demonstrate

def test_real_workflow_trace():
    result=demonstrate()
    assert result["provider_calls"]==0
    assert result["cases"][0]["final_route"]=="approved"
    assert result["cases"][0]["sent_after_resume"] is False
    assert result["cases"][1]["initial_route"]=="rejected"
