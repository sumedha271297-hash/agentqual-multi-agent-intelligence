"""Verify ephemeral TLS ingress, authentication, metrics and 429 rate limit."""
import json
import ssl
import time
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.error import HTTPError
ROOT=Path(__file__).resolve().parent.parent
URL="https://localhost:8443"
CRT=ROOT/"deploy/tls/server.crt"
KEY="a"*32

def fetch(path,tenant=None):
    headers={"X-API-Key":tenant} if tenant else {}
    req=Request(URL+path,headers=headers)
    ctx=ssl.create_default_context(cafile=str(CRT))
    try:
        with urlopen(req,context=ctx,timeout=10) as r:
            return r.status,json.loads(r.read().decode()),r.headers
    except HTTPError as e:
        return e.code,{},e.headers

def verify():
    # Avoid initial warmup request bursts affecting auth checks.
    time.sleep(.9)
    s,body,headers=fetch("/health")
    assert s==200 and body["status"]=="ok"
    assert headers.get("Strict-Transport-Security") is not None
    time.sleep(.2)
    s,_,_=fetch("/companies")
    assert s==401
    time.sleep(.2)
    s,body,_=fetch("/metrics",KEY)
    assert s==200 and body["scope"].startswith("single-process")
    # Repeated local requests MUST trip ingress controls, not become an
    # availability SLO claim.
    statuses=[fetch("/health")[0] for _ in range(20)]
    assert 429 in statuses, statuses
    result={"https_verified_with_ephemeral_trusted_certificate":True,
            "security_header":True,"unauthorized_rejected":True,
            "authenticated_process_local_metrics":True,
            "rate_limit_429_observed":True,
            "limitations":"GitHub localhost self-signed TLS ingress; no public domain, managed CA, centralized monitoring or cloud infrastructure"}
    print(json.dumps(result,indent=2))
    return result

if __name__=="__main__":verify()
