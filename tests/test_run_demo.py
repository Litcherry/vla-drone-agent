from pathlib import Path

from run_demo import run_task


def test_run_task_handles_planning_failure(tmp_path: Path):
    result = run_task(
        task="随便做点什么",
        output_dir=str(tmp_path),
        planner="rule",
    )

    assert result["success"] is False
    assert result["failure_reason"].startswith("planning_failed")
    assert result["actions"] == []

    events_path = tmp_path / "events.jsonl"
    assert events_path.exists()

    events_text = events_path.read_text(encoding="utf-8")
    assert "planning_failed" in events_text
    assert "task_finished" in events_text


def test_run_task_handles_out_of_bounds_move_to(tmp_path: Path):
    result = run_task(
        task="take off, move to x=5 y=0 z=1, hover 2 seconds, then land",
        output_dir=str(tmp_path),
        planner="rule",
    )

    assert result["success"] is False
    assert result["failure_reason"].startswith("planning_failed")

    events_text = (tmp_path / "events.jsonl").read_text(encoding="utf-8")
    assert "planning_failed" in events_text