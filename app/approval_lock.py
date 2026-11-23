"""Per-thread approval locks across API workers using PostgreSQL advisory locks.

Postgres mode uses session-scoped locks, so the lock remains held while
LangGraph commits its checkpoint on a *separate* Postgres connection.
Memory mode uses striped process-local locks and is development-only.
"""
import hashlib
import os
import threading
import time
from contextlib import contextmanager

_stripes = tuple(threading.Lock() for _ in range(256))

class ApprovalBusy(Exception):
    """Concurrent approval is being handled by another request."""

def _lock_id(thread_id: str) -> int:
    digest = hashlib.blake2b(thread_id.encode("utf-8"), digest_size=8).digest()
    return int.from_bytes(digest, "big", signed=True)

@contextmanager
def approval_lock(thread_id: str, *, timeout_seconds: float = 2.0):
    lock_id = _lock_id(thread_id)
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        lock = _stripes[lock_id % len(_stripes)]
        if not lock.acquire(timeout=timeout_seconds):
            raise ApprovalBusy()
        try:
            yield
        finally:
            lock.release()
        return

    import psycopg
    # Connection is distinct from the LangGraph checkpointer connection.
    with psycopg.connect(database_url, autocommit=True, connect_timeout=3) as conn:
        deadline = time.monotonic() + timeout_seconds
        while True:
            acquired = conn.execute(
                "SELECT pg_try_advisory_lock(%s)", (lock_id,)
            ).fetchone()[0]
            if acquired:
                break
            if time.monotonic() >= deadline:
                raise ApprovalBusy()
            time.sleep(0.03)
        try:
            yield
        finally:
            conn.execute("SELECT pg_advisory_unlock(%s)", (lock_id,))
