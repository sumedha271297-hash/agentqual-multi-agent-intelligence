"use strict";
const $ = id => document.getElementById(id);
const ICP = {industries:["SaaS","Fintech"],min_employees:20,max_employees:300,regions:["US"]};
let threadId = null;
let approvalKey = null;
let busy = false;
const buttons = ["run","inspect","approve","reject"];
const state = (msg, data) => {
  $("status").textContent = msg;
  if (data !== undefined) $("result").textContent = JSON.stringify(data,null,2);
};
function setButtons(waiting) {
  $("run").disabled = busy;
  $("inspect").disabled = busy || !threadId;
  $("approve").disabled = busy || !waiting;
  $("reject").disabled = busy || !waiting;
}
async function call(path, options = {}) {
  const headers = {"Content-Type":"application/json"};
  const key = $("apiKey").value.trim();
  if (key) headers["X-API-Key"] = key;
  if (options.idempotency) headers["Idempotency-Key"] = options.idempotency;
  const response = await fetch(path,{method:options.method || "GET",headers,
    body:options.body ? JSON.stringify(options.body) : undefined,cache:"no-store",
    credentials:"same-origin"});
  const data = await response.json();
  if (!response.ok) throw new Error("HTTP " + response.status + ": " + (data.detail || "Request failed"));
  return data;
}
async function runAction(operation) {
  if (busy) return;
  busy=true; setButtons(false);
  try {
    let data;
    if (operation === "run") {
      threadId = null; approvalKey = null;
      data=await call("/graph/run",{method:"POST",body:{
        company_id:$("company").value,icp:ICP,llm_enabled:false,
        agentic_research:false,agentic_qualification:false}});
      threadId=data.thread_id;
    } else if(operation === "inspect"){
      data=await call("/graph/"+encodeURIComponent(threadId));
    } else {
      approvalKey = approvalKey || crypto.randomUUID();
      data=await call("/graph/"+encodeURIComponent(threadId)+"/approve",
        {method:"POST",idempotency:approvalKey,body:{approved:operation==="approve"}});
    }
    state("Route: "+(data.state?.route || "unknown")+
      (data.awaiting_approval ? " · human approval pending" : " · no pending approval"),data);
    busy=false;setButtons(Boolean(data.awaiting_approval));
  } catch (err) {
    busy=false;state("Request failed: "+String(err.message));
    setButtons(Boolean(threadId) && (operation==="approve" || operation==="reject"));
  }
}
buttons.forEach(id => $(id).addEventListener("click",()=>runAction(id)));
setButtons(false);
