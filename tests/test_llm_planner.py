import pytest

from agent.llm_planner import extract_json_array
from agent.planner_backend import plan_instruction


def test_extract_json_array_from_plain_json():
    text = '[{"action": "land"}]'

    assert extract_json_array(text) == text


def test_extract_json_array_from_markdown_block():
    text = '```json\n[{"action": "land"}]\n```'

    assert extract_json_array(text) == '[{"action": "land"}]'


def test_auto_planner_falls_back_to_rule_when_llm_fails(monkeypatch):
    def fake_plan_with_llm(_instruction: str):
        raise RuntimeError("network error")

    monkeypatch.setattr("agent.planner_backend.plan_with_llm", fake_plan_with_llm)

    result = plan_instruction(
        "起飞，找到红色目标，飞到它上方 1 米处悬停 5 秒，然后降落",
        mode="auto",
    )

    assert result.source == "rule"
    assert result.fallback_reason.startswith("llm_failed")
    assert result.actions[0]["action"] == "takeoff"


def test_llm_mode_raises_when_llm_fails(monkeypatch):
    def fake_plan_with_llm(_instruction: str):
        raise RuntimeError("network error")

    monkeypatch.setattr("agent.planner_backend.plan_with_llm", fake_plan_with_llm)

    with pytest.raises(RuntimeError):
        plan_instruction("take off and land", mode="llm")