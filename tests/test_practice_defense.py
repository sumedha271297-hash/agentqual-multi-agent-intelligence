from scripts.practice_defense import QUESTIONS,run

def test_interview_tasks_cover_system_design_and_are_not_autoscored(tmp_path):
    assert len(QUESTIONS)==8
    result=run(input_fn=lambda prompt:"SKIP",output_dir=tmp_path)
    assert result["reviewer_score"] is None
    assert len(result["tasks"])==8
    assert (tmp_path/"candidate_practice_answers.json").exists()
