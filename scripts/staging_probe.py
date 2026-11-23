"""Probe an ACTUAL Docker Compose API through localhost TCP, not TestClient.

Uses ephemeral test-only credentials and synthetic companies. The probe never
sends mail, and makes no provider calls. Exit nonzero on any mismatch.
"""
import json
import os
import sys
import time
import uuid
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

BASE=os.environ.get("STAGING_BASE_URL","http://127.0.0.1:8080")
TENANT_A="a"*32
TENANT_B="b"*32
ICP={"industries":["SaaS","Fintech"],"min_employees":20,
     "max_employees":300,"regions":["US"]}

def request(path, *, method="GET", tenant=None, data=None, key=None):
    headers={"Accept":"application/json"}
    if tenant: headers["X-API-Key"]=tenant
    if key: headers["Idempotency-Key"]=key
    if data is not None: headers["Content-Type"]="application/json"
    req=Request(BASE+path,method=method,headers=headers,
                data=json.dumps(data).encode() if data is not None else None)
    try:
        with urlopen(req,timeout=12) as resp:
            return resp.status,json.loads(resp.read().decode())
    except HTTPError as exc:
        return exc.code,json.loads(exc.read().decode())

def verify():
    results={}
    for attempt in range(40):
        try:
            if request("/health")[0]==200: break
        except (URLError,TimeoutError):
            time.sleep(.75)
    else:
        raise AssertionError("Container health did not respond within probe window")
    results["health"]=True
    results["unauthenticated_company_list_rejected"]=(request("/companies")[0]==401)
    results["invalid_credential_rejected"]=(request("/companies",tenant="bad")[0]==401)
    results["tenant_credential_accepted"]=(request("/companies",tenant=TENANT_A)[0]==200)
    results["development_ui_not_public_in_staging"]=(request("/demo",tenant=TENANT_A)[0]==404)
    status,created=request("/graph/run",method="POST",tenant=TENANT_A,
        data={"company_id":"c01","icp":ICP,"llm_enabled":False})
    assert status==200 and created["awaiting_approval"],(status,created)
    tid=created["thread_id"]
    results["pause"]=True
    results["foreign_thread_hidden"]=(request("/graph/"+tid,tenant=TENANT_B)[0]==404)
    results["foreign_approval_denied"]=(request("/graph/"+tid+"/approve",
        method="POST",tenant=TENANT_B,data={"approved":True})[0]==404)
    status,inspected=request("/graph/"+tid,tenant=TENANT_A)
    results["owner_can_read_checkpoint"]=(status==200 and inspected["awaiting_approval"])
    key=str(uuid.uuid4())
    status,approved=request("/graph/"+tid+"/approve",method="POST",tenant=TENANT_A,
        data={"approved":True},key=key)
    results["approval"]=(status==200 and approved["state"]["approved"] is True
                         and approved["state"]["sent"] is False and not approved["replayed"])
    status,replay=request("/graph/"+tid+"/approve",method="POST",tenant=TENANT_A,
        data={"approved":True},key=key)
    results["idempotency"]=(status==200 and replay["replayed"] is True
                            and replay["state"]["sent"] is False)
    results["conflicting_approval_rejected"]=(request("/graph/"+tid+"/approve",
        method="POST",tenant=TENANT_A,data={"approved":False},key=key)[0]==409)
    status,rejected=request("/graph/run",method="POST",tenant=TENANT_A,
        data={"company_id":"c02","icp":ICP,"llm_enabled":False})
    results["unqualified_never_sent"]=(status==200 and not rejected["awaiting_approval"]
                                     and rejected["state"]["sent"] is False)
    results["missing_llm_secret_rejected"]=(request("/graph/run",method="POST",
        tenant=TENANT_A,data={"company_id":"c01","icp":ICP,"llm_enabled":True})[0]==422)
    print(json.dumps({"type":"real_compose_tcp_staging_probe","checks":results,
        "passed":sum(results.values()),"total":len(results),
        "limitations":"GitHub ephemeral localhost Docker Compose; no TLS/ingress, cloud deployment, or real-provider calls."},indent=2))
    if not all(results.values()): sys.exit(1)

if __name__=="__main__": verify()
