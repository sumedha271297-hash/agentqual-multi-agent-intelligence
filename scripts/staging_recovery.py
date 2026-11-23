"""Real PostgreSQL persisted LangGraph approval across Docker API restart."""
import json
import sys
import uuid
from pathlib import Path
from scripts.staging_probe import request,TENANT_A,ICP
FILE=Path("reports/staging_pending.json")

def run(mode):
    if mode=="prepare":
        status,run=request("/graph/run",method="POST",tenant=TENANT_A,
            data={"company_id":"c01","icp":ICP,"llm_enabled":False})
        assert status==200 and run["awaiting_approval"]
        FILE.parent.mkdir(exist_ok=True)
        FILE.write_text(json.dumps({"thread_id":run["thread_id"]})+"\n")
        print("Checkpoint saved before API restart.")
    elif mode=="resume":
        thread_id=json.loads(FILE.read_text())["thread_id"]
        status,checkpoint=request("/graph/"+thread_id,tenant=TENANT_A)
        assert status==200 and checkpoint["awaiting_approval"]
        status,approved=request("/graph/"+thread_id+"/approve",method="POST",
            tenant=TENANT_A,data={"approved":True},key=str(uuid.uuid4()))
        assert status==200 and approved["state"]["approved"] is True
        assert approved["state"]["sent"] is False
        print("Postgres checkpoint survived real API container restart; approved and sent=false.")
    else:
        raise ValueError("Use prepare or resume")

if __name__=="__main__":
    run(sys.argv[1])
