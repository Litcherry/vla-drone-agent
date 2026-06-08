"""Position-based controller for the simple PyBullet drone."""

from __future__ import annotations

import math
from dataclasses import dataclass

from sim.drone import SimpleDrone
from sim.world import PyBulletWorld


@dataclass(frozen=True)
class ControlResult:
    """Result of executing a controller command."""

    success: bool
    final_error: float
    steps: int
    reason: str = ""


class DroneController:
    """Execute high-level drone actions with simple position control."""

    def __init__(
        self,
        world: PyBulletWorld,
        drone: SimpleDrone,
        speed: float = 0.04,
        arrival_threshold: float = 0.08,
    ) -> None:
        self.world = world
        self.drone = drone
        self.speed = speed
        self.arrival_threshold = arrival_threshold

    def takeoff(self, altitude: float) -> ControlResult:
        current = self.drone.get_state().position
        target = (current[0], current[1], altitude)
        return self.move_to(target)

    def move_to(
        self,
        target_position: tuple[float, float, float],
        max_steps: int = 500,
    ) -> ControlResult:
        for step in range(max_steps):
            current = self.drone.get_state().position
            error = distance(current, target_position)

            if error <= self.arrival_threshold:
                return ControlResult(success=True, final_error=error, steps=step)

            next_position = step_towards(current, target_position, self.speed)
            self.drone.set_position(next_position)
            self.world.step()

        final_error = distance(self.drone.get_state().position, target_position)
        return ControlResult(
            success=False,
            final_error=final_error,
            steps=max_steps,
            reason="max_steps_exceeded",
        )

    def hover(self, duration: float) -> ControlResult:
        steps = max(1, int(duration / self.world.time_step))
        start = self.drone.get_state().position

        for _ in range(steps):
            self.drone.set_position(start)
            self.world.step()

        final_error = distance(self.drone.get_state().position, start)
        return ControlResult(success=True, final_error=final_error, steps=steps)

    def land(self) -> ControlResult:
        current = self.drone.get_state().position
        target = (current[0], current[1], 0.05)
        return self.move_to(target)


def distance(
    a: tuple[float, float, float],
    b: tuple[float, float, float],
) -> float:
    """Euclidean distance between two 3D points."""

    return math.sqrt(sum((a_i - b_i) ** 2 for a_i, b_i in zip(a, b)))


def step_towards(
    current: tuple[float, float, float],
    target: tuple[float, float, float],
    step_size: float,
) -> tuple[float, float, float]:
    """Move from current toward target by at most step_size."""

    error = distance(current, target)
    if error <= step_size:
        return target

    ratio = step_size / error
    return (
        current[0] + (target[0] - current[0]) * ratio,
        current[1] + (target[1] - current[1]) * ratio,
        current[2] + (target[2] - current[2]) * ratio,
    )