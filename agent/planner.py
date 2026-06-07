"""Rule-based planner for converting language instructions into drone actions."""

from __future__ import annotations

import re
from typing import Any

from agent.schema import validate_plan
from agent.safety import assert_plan_safe


COLOR_ALIASES = {
    "red": ("red", "红", "红色"),
    "blue": ("blue", "蓝", "蓝色"),
    "green": ("green", "绿", "绿色"),
}

DEFAULT_TAKEOFF_ALTITUDE = 1.5
DEFAULT_MOVE_ABOVE_HEIGHT = 1.0
DEFAULT_HOVER_DURATION = 5.0


def normalize_instruction(instruction: str) -> str:
    """Normalize instruction text for simple rule matching."""

    return instruction.strip().lower()


def extract_color(text: str) -> str | None:
    """Extract target color from Chinese or English instruction text."""

    for color, aliases in COLOR_ALIASES.items():
        if any(alias in text for alias in aliases):
            return color

    return None


def extract_first_number_before_keywords(
    text: str,
    keywords: tuple[str, ...],
    default: float,
) -> float:
    """Extract a nearby numeric value before or after task-specific keywords."""

    for keyword in keywords:
        patterns = [
            rf"(\d+(?:\.\d+)?)\s*(?:米|m|meter|meters)?\s*{re.escape(keyword)}",
            rf"{re.escape(keyword)}\s*(\d+(?:\.\d+)?)\s*(?:米|m|meter|meters|秒|s|second|seconds)?",
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return float(match.group(1))

    return default


def parse_instruction(instruction: str) -> list[dict[str, Any]]:
    """Parse a natural language instruction into a validated action list."""

    text = normalize_instruction(instruction)
    color = extract_color(text)

    actions: list[dict[str, Any]] = []

    if any(token in text for token in ("起飞", "takeoff", "take off")):
        altitude = extract_first_number_before_keywords(
            text,
            ("起飞", "takeoff", "take off"),
            DEFAULT_TAKEOFF_ALTITUDE,
        )
        actions.append({"action": "takeoff", "altitude": altitude})

    if color is not None and any(token in text for token in ("找", "搜索", "search", "find")):
        actions.append({"action": "search", "target": color})

    if color is not None and any(token in text for token in ("上方", "above")):
        height = extract_first_number_before_keywords(
            text,
            ("上方", "above"),
            DEFAULT_MOVE_ABOVE_HEIGHT,
        )
        actions.append({"action": "move_above", "target": color, "height": height})

    if any(token in text for token in ("悬停", "hover")):
        duration = extract_first_number_before_keywords(
            text,
            ("悬停", "hover"),
            DEFAULT_HOVER_DURATION,
        )
        actions.append({"action": "hover", "duration": duration})

    if any(token in text for token in ("降落", "land")):
        actions.append({"action": "land"})

    if not actions:
        raise ValueError(f"Could not parse instruction into actions: {instruction}")

    validated_actions = validate_plan(actions)
    assert_plan_safe(validated_actions)

    return validated_actions