"""Regression checks for opt-in provider use. No network/API calls here."""
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def test_free_gemini_workflow_is_manual_opt_in():
    workflow=(ROOT/".github/workflows/live-gemini-free.yml").read_text()
    assert "workflow_dispatch:" in workflow
    assert "RUN_GEMINI_FREE" in workflow
    assert "secrets.GEMINI_API_KEY" in workflow
    assert "gemini-2.5-flash-lite" in workflow
    assert "--provider gemini --allow-provider-calls" in workflow
    assert "push:" not in workflow.split("jobs:",1)[0]
    assert "pull_request:" not in workflow.split("jobs:",1)[0]

def test_gemini_client_uses_structured_output_without_sending():
    source=(ROOT/"app/gemini.py").read_text()
    assert "response_schema=OutreachDraft" in source
    assert '"sent": False' in source
