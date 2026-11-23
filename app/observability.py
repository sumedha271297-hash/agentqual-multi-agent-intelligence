"""Minimal process-local API diagnostics, no message bodies or token logging."""
from collections import Counter, deque
from threading import Lock
from time import perf_counter

_lock = Lock()
_counts = Counter()
_latencies = deque(maxlen=2000)

def record(method: str, route: str, status: int, latency_ms: float):
    # Whitelist the route template, not literal path IDs or query strings.
    key = (method, route, str(status))
    with _lock:
        _counts[key] += 1
        _latencies.append(latency_ms)

def summary():
    with _lock:
        ms = sorted(_latencies)
        p95 = ms[max(0, (len(ms)*95+99)//100-1)] if ms else None
        return {"requests_by_route_status": [
            {"method": m, "route": path, "status": int(s), "count": n}
            for (m, path, s), n in sorted(_counts.items())],
            "observed_request_count": len(ms),
            "recent_p95_request_latency_ms": round(p95, 3) if p95 is not None else None,
            "scope": "single-process, last 2000 requests; not distributed observability"}
