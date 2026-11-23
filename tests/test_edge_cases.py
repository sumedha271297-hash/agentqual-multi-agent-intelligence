"""Additional adversarial and validation tests for the offline baseline."""
import pytest
from app.core import Company, qualify, workflow_offline, validate_draft

ICP = {'industries':['SaaS'], 'min_employees':20, 'max_employees':300, 'regions':['US']}

def test_boundary_minimum_inclusive():
    assert qualify(Company('x','Example','SaaS',20,'US',''),ICP)['qualified']

def test_boundary_maximum_inclusive():
    assert qualify(Company('x','Example','SaaS',300,'US',''),ICP)['qualified']

def test_outside_boundary_rejected():
    assert not qualify(Company('x','Example','SaaS',301,'US',''),ICP)['qualified']

def test_case_insensitive_categories():
    assert qualify(Company('x','Example','saas',30,'us',''),ICP)['qualified']

def test_no_draft_on_rejection():
    result = workflow_offline('c02',ICP)
    assert result['draft'] is None and result['sent'] is False

def test_never_automatically_sends():
    result = workflow_offline('c01',ICP)
    assert result['sent'] is False and result['approved'] is False

def test_missing_company_raises():
    with pytest.raises(KeyError):
        workflow_offline('unknown',ICP)

def test_draft_requires_approval():
    assert not validate_draft({'subject':'a','message':'b','requires_approval':False})
