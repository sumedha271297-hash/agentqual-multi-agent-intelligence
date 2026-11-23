"""Interactive engineering interview practice; stores responses, never scores them."""
import json
import time
from pathlib import Path
QUESTIONS=[
 ("A","Walk through the actual graph nodes for qualified and rejected company IDs. Which state fields prove no sending?"),
 ("B","Where does LangGraph add value over a plain state machine? What is the simplest viable alternative?"),
 ("C","How can concurrent or foreign-tenant approvals fail, and how are retries bounded?"),
 ("D","Show what happens on invalid model output. What attack is still possible?"),
 ("E","Explain how database checkpoint recovery and backup restoration can be verified."),
 ("F","Design safe outbound delivery using a transactional outbox. Describe duplicate network send risks."),
 ("G","Design an independent evaluation comparing deterministic and LLM-assisted qualification."),
 ("H","Describe how you would debug failing CI logs and capture regression evidence."),
]
def run(input_fn=input,output_dir="reports"):
    answers=[]
    for key,question in QUESTIONS:
        print(f"\n[{key}] {question}\n(Submit one paragraph. Enter SKIP to skip.)")
        started=time.monotonic()
        answer=input_fn("> ").strip()
        answers.append({"task":key,"answer":answer,"elapsed_seconds":round(time.monotonic()-started,2)})
    result={"type":"unscored_self_practice","tasks":answers,
            "reviewer_score":None,"limitation":"No independent reviewer has assessed the answers."}
    output=Path(output_dir);output.mkdir(parents=True,exist_ok=True)
    destination=output/"candidate_practice_answers.json"
    destination.write_text(json.dumps(result,indent=2)+"\n")
    print(f"Saved unscored responses at {destination}")
    return result
if __name__=="__main__":
    run()
