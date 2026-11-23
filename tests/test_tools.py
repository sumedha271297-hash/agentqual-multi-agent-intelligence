import pytest
from app.tools import company_lookup, ToolFailure

SAMPLE = {'id':'x','name':'X','industry':'SaaS','employees':10,'region':'US','description':'demo'}

def test_tool_retries_transient_failure():
    calls = []
    def provider(key):
        calls.append(key)
        if len(calls) < 3:
            raise TimeoutError('temporary')
        return SAMPLE
    result = company_lookup('x', provider=provider, backoff=0)
    assert result['metadata']['attempts'] == 3
    assert result['data']['name'] == 'X'

def test_tool_exhausted():
    def fail(_):
        raise ConnectionError('offline')
    with pytest.raises(ToolFailure):
        company_lookup('x', provider=fail, attempts=2, backoff=0)

def test_tool_invalid_schema():
    with pytest.raises(ToolFailure):
        company_lookup('x', provider=lambda _: {'name':'x'}, attempts=1)

def test_tool_does_not_retry_not_found():
    calls = []
    def missing(key):
        calls.append(key)
        raise KeyError(key)
    with pytest.raises(KeyError):
        company_lookup('missing', provider=missing, attempts=3)
    assert len(calls) == 1

def test_tool_attempts_bounded():
    with pytest.raises(ValueError):
        company_lookup('x', attempts=6)
