import pytest

from agent.planner import parse_instruction


def test_parse_chinese_red_target_task():
    instruction = "起飞，找到红色目标，飞到它上方 1 米处悬停 5 秒，然后降落。"

    actions = parse_instruction(instruction)

    assert actions == [
        {"action": "takeoff", "altitude": 1.5},
        {"action": "search", "target": "red"},
        {"action": "move_above", "target": "red", "height": 1.0},
        {"action": "hover", "duration": 5.0},
        {"action": "land"},
    ]


def test_parse_english_blue_target_task():
    instruction = "take off, find the blue target, move above it 1 meter, hover 3 seconds, then land"

    actions = parse_instruction(instruction)

    assert actions == [
        {"action": "takeoff", "altitude": 1.5},
        {"action": "search", "target": "blue"},
        {"action": "move_above", "target": "blue", "height": 1.0},
        {"action": "hover", "duration": 3.0},
        {"action": "land"},
    ]


def test_parse_green_target_with_default_hover_duration():
    instruction = "起飞，搜索绿色目标，飞到绿色目标上方，然后悬停，最后降落"

    actions = parse_instruction(instruction)

    assert {"action": "search", "target": "green"} in actions
    assert {"action": "hover", "duration": 5.0} in actions


def test_unknown_instruction_is_rejected():
    with pytest.raises(ValueError):
        parse_instruction("随便做点什么")