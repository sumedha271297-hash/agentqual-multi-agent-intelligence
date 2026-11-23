from app.core import load_companies, qualify, workflow_offline, validate_draft
from scripts.evaluate import evaluate

ICP={'industries':['SaaS','Fintech'],'min_employees':20,'max_employees':300,'regions':['US']}

def test_qualified_needs_approval():
    r=workflow_offline('c01',ICP)
    assert r['route']=='approval' and r['approved'] is False and r['sent'] is False
    assert validate_draft(r['draft'])

def test_rejected_no_draft():
    r=workflow_offline('c02',ICP)
    assert r['route']=='rejected' and r['draft'] is None

def test_unknown_company():
    import pytest
    with pytest.raises(KeyError): workflow_offline('missing',ICP)

def test_baseline_reproducible():
    r=evaluate()
    assert r['sample_count']==10
    assert r['confusion']=={'tp':4,'fp':0,'tn':6,'fn':0}

def test_no_automatic_send():
    for cid in load_companies():
        assert workflow_offline(cid,ICP)['sent'] is False
