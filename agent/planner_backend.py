"""Planner backend selection with optional LLM and rule fallback."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from agent.llm_planner import plan_with_llm
from agent.planner import parse_instruction


PlannerMode = Literal["auto", "llm", "rule"]


@dataclass(frozen=True)
class PlannerResult:
    """Planner result with source metadata."""

    actions: list[dict[str, Any]]
    source: str
    fallback_reason: str = ""


def plan_instruction(instruction: str, mode: PlannerMode = "auto") -> PlannerResult:
    """Plan an instruction using rule, LLM, or auto fallback mode."""

    if mode == "rule":
        return PlannerResult(actions=parse_instruction(instruction), source="rule")

    if mode == "llm":
        return PlannerResult(actions=plan_with_llm(instruction), source="llm")

    if mode == "auto":
        try:
            return PlannerResult(actions=plan_with_llm(instruction), source="llm")
        except Exception as exc:
            return PlannerResult(
                actions=parse_instruction(instruction),
                source="rule",
                fallback_reason=f"llm_failed:{type(exc).__name__}",
            )

    raise ValueError(f"Unsupported planner mode: {mode}")