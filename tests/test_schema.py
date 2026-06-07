import pytest

from agent.schema import validate_plan
from agent.safety import assert_plan_safe, check_plan_safety


def test_valid_plan_passes_schema_validation():
    raw_actions = [
        {"action": "takeoff", "altitude": 1.5},
        {"action": "search", "target": "red"},
        {"action": "move_above", "target": "red", "height": 1.0},
        {"action": "hover", "duration": 5},
        {"action": "land"},
    ]

    validated = validate_plan(raw_actions)

    assert validated[0] == {"action": "takeoff", "altitude": 1.5}
    assert validated[-1] == {"action": "land"}


def test_invalid_action_is_rejected():
    raw_actions = [{"action": "flip", "duration": 3}]

    with pytest.raises(ValueError):
        validate_plan(raw_actions)


def test_missing_required_parameter_is_rejected():
    raw_actions = [{"action": "takeoff"}]

    with pytest.raises(ValueError):
        validate_plan(raw_actions)


def test_out_of_bounds_move_to_is_reported():
    raw_actions = [{"action": "move_to", "position": (10.0, 0.0, 1.0)}]
    validated = validate_plan(raw_actions)

    violations = check_plan_safety(validated)

    assert violations


def test_safe_plan_passes_safety_check():
    raw_actions = [{"action": "move_to", "position": (1.0, 1.0, 1.0)}]
    validated = validate_plan(raw_actions)

    assert_plan_safe(validated)