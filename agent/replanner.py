"""Fallback and replanning logic placeholder."""

from __future__ import annotations

from typing import Any

from agent.schema import validate_plan


def build_safe_fallback_plan(reason: str) -> list[dict[str, Any]]:
    """Build a conservative fallback plan after task failure.

    The fallback policy is intentionally simple and deterministic: hover briefly
    to stabilize, then land. This prevents task failures from leaving the drone
    in an uncontrolled state.
    """

    raw_actions = [
        {"action": "hover", "duration": 1.0},
        {"action": "land"},
    ]
    fallback_actions = validate_plan(raw_actions)

    for action in fallback_actions:
        action["fallback_reason"] = reason

    return fallback_actions