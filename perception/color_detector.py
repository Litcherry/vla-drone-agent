"""Color target detector placeholder."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from sim.world import PyBulletWorld


TargetColor = Literal["red", "blue", "green"]


@dataclass(frozen=True)
class DetectionResult:
    """Result returned by the color target detector."""

    color: TargetColor
    position: tuple[float, float, float]
    source: str = "sim_observation"


class ColorTargetDetector:
    """Detect colored targets from simulator observations.

    The current minimal demo uses PyBullet simulator observations to obtain
    world-frame target positions. This keeps the perception-control interface
    explicit and can later be replaced by image-based color segmentation.
    """

    def __init__(self, world: PyBulletWorld) -> None:
        self.world = world

    def detect(self, color: TargetColor) -> DetectionResult | None:
        """Return the target position for a known color, if visible."""

        position = self.world.get_target_position(color)
        if position is None:
            return None

        return DetectionResult(color=color, position=position)