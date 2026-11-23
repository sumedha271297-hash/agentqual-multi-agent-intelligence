# Executable application demo and evidence

Run locally after installing Python dependencies:

```bash
python -m scripts.demo
python -m scripts.evaluate_v2
```

`scripts.demo` invokes the **real LangGraph workflow** with the offline
research tool on two fictional companies, verifies the approval interrupt,
resumes one workflow, and verifies no message was dispatched. It emits
`reports/demo_trace.json` without outreach text or secrets.

GitHub CI runs this script and uploads the JSON artifact, so reviewers can
inspect a run tied to a specific commit. This is a **live code-execution
demonstration**, not a browser screen recording, a hosted URL, or proof of
paid-model inference.

To create a true screen-recorded video, open the FastAPI Swagger UI on a
local running service and record run/status/approval endpoints. A video is
not published from this repository.
