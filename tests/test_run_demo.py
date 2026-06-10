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

def test_run_task_classifies_unsupported_color(tmp_path: Path):
    result = run_task(
        task="起飞，找到青色目标，然后降落",
        output_dir=str(tmp_path),
        planner="rule",
    )

    assert result["success"] is False
    assert result["failure_reason"] == "planning_failed:unsupported_target_color"

def test_run_task_executes_fallback_when_target_is_missing(tmp_path: Path):
    result = run_task(
        task="起飞，找到红色目标，飞到它上方 1 米处悬停 2 秒，然后降落",
        output_dir=str(tmp_path),
        planner="rule",
        missing_targets=["red"],
    )

    assert result["success"] is False
    assert result["failure_reason"] == "target_not_found:red"

    events_text = (tmp_path / "events.jsonl").read_text(encoding="utf-8")
    assert "target_removed" in events_text
    assert "action_failed" in events_text
    assert "fallback_started" in events_text
    assert "fallback_finished" in events_text