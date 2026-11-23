"""Record a real Chromium browser driving the real FastAPI review UI.

This does not fake screenshots or create a slides-only video. It verifies
network-backed API interactions and produces the browser video as an artifact.
"""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

ROOT=Path(__file__).resolve().parent.parent
DEST=ROOT/"reports"/"browser"
DEST.mkdir(parents=True,exist_ok=True)
BASE="http://127.0.0.1:8000"

def record():
    checkpoints=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,args=["--no-sandbox"])
        context=browser.new_context(
            viewport={"width":1280,"height":820},
            record_video_dir=str(DEST),
            record_video_size={"width":1280,"height":820},
            reduced_motion="reduce")
        page=context.new_page()
        page.goto(BASE+"/demo",wait_until="networkidle")
        expect(page.get_by_role("heading",name="AgentQual")).to_be_visible()
        page.wait_for_timeout(1000)
        page.screenshot(path=str(DEST/"01_start.png"))
        page.locator("#run").click()
        expect(page.locator("#status")).to_contain_text("human approval pending")
        pending=json.loads(page.locator("#result").inner_text())
        assert pending["awaiting_approval"] and not pending["state"]["sent"]
        checkpoints.append("qualified_pause")
        page.wait_for_timeout(900)
        page.screenshot(path=str(DEST/"02_pending.png"))
        page.locator("#inspect").click()
        expect(page.locator("#status")).to_contain_text("human approval pending")
        checkpoints.append("checkpoint_inspection")
        page.wait_for_timeout(700)
        page.locator("#approve").click()
        expect(page.locator("#status")).to_contain_text("Route: approved")
        completed=json.loads(page.locator("#result").inner_text())
        assert completed["state"]["approved"] and completed["state"]["sent"] is False
        checkpoints.append("manual_approval_no_send")
        page.wait_for_timeout(1000)
        page.screenshot(path=str(DEST/"03_approved.png"))
        page.locator("#company").select_option("c02")
        page.locator("#run").click()
        expect(page.locator("#status")).to_contain_text("Route: rejected")
        rejected=json.loads(page.locator("#result").inner_text())
        assert rejected["state"]["sent"] is False and not rejected["awaiting_approval"]
        checkpoints.append("rejected_no_send")
        page.wait_for_timeout(1300)
        page.screenshot(path=str(DEST/"04_rejected.png"))
        recording=page.video
        context.close()
        video_path=recording.path()
        browser.close()
    summary={"type":"chromium_network_backed_walkthrough","checkpoints":checkpoints,
        "browser_video":Path(video_path).name,
        "limitations":"localhost development UI, synthetic records, offline graph, no paid model, not a publicly deployed app."}
    (DEST/"verification.json").write_text(json.dumps(summary,indent=2)+"\n")
    print(json.dumps(summary,indent=2))
    return video_path

if __name__=="__main__":record()
