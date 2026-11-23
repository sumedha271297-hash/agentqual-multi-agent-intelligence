from scripts.evaluate_rubric import evaluate

def test_synthetic_review_rubric_identifies_disagreement():
    r=evaluate()
    assert r["n"]==10
    assert r["confusion"]=={"tp":3,"tn":6,"fp":1,"fn":0}
    assert r["precision"]==0.75 and r["recall"]==1.0
    assert len(r["errors"])==1 and r["errors"][0]["id"]=="c09"
