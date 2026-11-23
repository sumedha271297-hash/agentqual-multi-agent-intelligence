import csv
import pytest
from scripts.blind_review import packet,score

def _write(path,rows):
    with path.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=["case_id","decision","reviewer_id","evidence_note"])
        w.writeheader();w.writerows(rows)

def test_packet_contains_no_model_predictions_or_existing_labels(tmp_path):
    f=packet(tmp_path)
    txt=f.read_text()
    assert "expected_qualified" not in txt and "predicted" not in txt
    assert len(txt.splitlines())==41

def test_rejects_same_reviewer_even_if_files_differ(tmp_path):
    p=packet(tmp_path)
    ids=list(csv.DictReader(p.open()))
    a=[{"case_id":c["case_id"],"decision":"REVIEW","reviewer_id":"person-a",
        "evidence_note":"Insufficient details in fictional profile"} for c in ids]
    _write(tmp_path/"a.csv",a);_write(tmp_path/"b.csv",a)
    with pytest.raises(ValueError,match="distinct reviewers"):
        score(tmp_path/"a.csv",tmp_path/"b.csv")

def test_disagreement_only_not_publishable_ground_truth(tmp_path):
    ids=list(csv.DictReader(packet(tmp_path).open()))
    a=[{"case_id":c["case_id"],"decision":"REVIEW","reviewer_id":"person-a",
        "evidence_note":"Cannot determine fit from source"} for c in ids]
    b=[{**c,"reviewer_id":"person-b"} for c in a]
    b[0]["decision"]="REJECT"
    _write(tmp_path/"a.csv",a);_write(tmp_path/"b.csv",b)
    result=score(tmp_path/"a.csv",tmp_path/"b.csv")
    assert result["disagreement_count"]==1
    assert result["publishable_holdout_score"] is False

def test_reject_incomplete_annotation(tmp_path):
    ids=list(csv.DictReader(packet(tmp_path).open()))
    a=[{"case_id":c["case_id"],"decision":"QUALIFY","reviewer_id":"a",
        "evidence_note":"Explicit matching profile data"} for c in ids]
    b=[{**c,"reviewer_id":"b"} for c in a]
    b.pop()
    _write(tmp_path/"a.csv",a);_write(tmp_path/"b.csv",b)
    with pytest.raises(ValueError,match="each case exactly once"):
        score(tmp_path/"a.csv",tmp_path/"b.csv")
