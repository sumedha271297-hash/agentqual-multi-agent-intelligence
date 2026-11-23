from scripts.evaluate_v2 import evaluate

def test_scenario_matrix_is_frozen_and_complete():
    result=evaluate()
    assert result["overall"]["n"]==40
    assert result["splits"]["development"]["n"]==20
    assert result["splits"]["holdout"]["n"]==20

def test_contextual_ambiguity_produces_observable_disagreement():
    result=evaluate()
    assert any(r["case_id"]=="us-b2b-c09" for r in result["errors"])
    assert result["overall"]["fp"]>=1

def test_evaluation_is_reproducible():
    x=evaluate(); y=evaluate()
    assert x==y
