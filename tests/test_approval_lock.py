from app.approval_lock import _lock_id, approval_lock, ApprovalBusy
import threading
import pytest

def test_lock_id_stable_and_distinct():
    assert _lock_id("a") == _lock_id("a")
    assert _lock_id("a") != _lock_id("b")

def test_busy_lock_fails_fast(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    entered=threading.Event()
    release=threading.Event()
    def holder():
        with approval_lock("stable-lock"):
            entered.set()
            release.wait(2)
    thread=threading.Thread(target=holder)
    thread.start()
    assert entered.wait(1)
    try:
        with pytest.raises(ApprovalBusy):
            with approval_lock("stable-lock",timeout_seconds=0.01):
                pass
    finally:
        release.set()
        thread.join(timeout=2)
