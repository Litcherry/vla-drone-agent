"""Optional LLM planner using an OpenAI-compatible API."""

from __future__ import annotations

import json
import os
import re
from typing import Any

from openai import OpenAI

from agent.schema import validate_plan
from agent.safety import assert_plan_safe


class LLMPlannerUnavailable(RuntimeError):
    """Raised when the LLM planner cannot be used."""


SYSTEM_PROMPT = """You are a drone task planner.
Convert the user's Chinese or English instruction into a JSON action list only.

Allowed actions:
- takeoff: {"action": "takeoff", "altitude": 1.5}
- search: {"action": "search", "target": "red|blue|green"}
- move_to: {"action": "move_to", "position": [x, y, z]}
- move_above: {"action": "move_above", "target": "red|blue|green", "height": 1.0}
- hover: {"action": "hover", "duration": 5}
- land: {"action": "land"}

Rules:
- Output JSON only, no markdown.
- Use only red, blue, or green targets.
- Keep positions within x/y [-3, 3] and z [0, 3].
- If unspecified, use takeoff altitude 1.5, move_above height 1.0, hover duration 5.
"""


def plan_with_llm(instruction: str) -> list[dict[str, Any]]:
    """Plan with an OpenAI-compatible LLM and validate the result."""

    api_key = os.getenv("DASHSCOPE_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise LLMPlannerUnavailable("DASHSCOPE_API_KEY is not set")

    base_url = os.getenv("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
    model = os.getenv("DASHSCOPE_MODEL", "qwen-plus")

    client = OpenAI(api_key=api_key, base_url=base_url)
    response = client.chat.completions.create(
        model=model,
        temperature=0,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": instruction},
        ],
    )

    content = response.choices[0].message.content or ""
    raw_actions = json.loads(extract_json_array(content))
    validated_actions = validate_plan(raw_actions)
    assert_plan_safe(validated_actions)
    return validated_actions


def extract_json_array(text: str) -> str:
    """Extract a JSON array from an LLM response."""

    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?", "", cleaned)
    cleaned = re.sub(r"```$", "", cleaned).strip()

    if cleaned.startswith("[") and cleaned.endswith("]"):
        return cleaned

    match = re.search(r"\[.*\]", cleaned, flags=re.DOTALL)
    if not match:
        raise ValueError(f"LLM response does not contain a JSON array: {text}")

    return match.group(0)