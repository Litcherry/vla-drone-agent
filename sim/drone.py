"""Simple drone body wrapper for the PyBullet demo."""

from __future__ import annotations

from dataclasses import dataclass

import pybullet as p


@dataclass
class DroneState:
    """Current drone state in the simulation."""

    position: tuple[float, float, float]


class SimpleDrone:
    """A lightweight visible drone model controlled by position commands."""

    def __init__(
        self,
        start_position: tuple[float, float, float] = (0.0, 0.0, 0.05),
    ) -> None:
        self.start_position = start_position
        self.body_id: int | None = None

    def spawn(self) -> None:
        """Create a simple drone body in PyBullet."""

        visual_id = p.createVisualShape(
            shapeType=p.GEOM_BOX,
            halfExtents=(0.16, 0.16, 0.04),
            rgbaColor=(0.1, 0.1, 0.1, 1.0),
        )
        collision_id = p.createCollisionShape(
            shapeType=p.GEOM_BOX,
            halfExtents=(0.16, 0.16, 0.04),
        )
        self.body_id = p.createMultiBody(
            baseMass=0.2,
            baseCollisionShapeIndex=collision_id,
            baseVisualShapeIndex=visual_id,
            basePosition=self.start_position,
        )

        self._create_arm((0.28, 0.02, 0.01), (0.0, 0.0, 0.0))
        self._create_arm((0.02, 0.28, 0.01), (0.0, 0.0, 0.0))

    def get_state(self) -> DroneState:
        """Return the current drone position."""

        self._require_body()
        position, _ = p.getBasePositionAndOrientation(self.body_id)
        return DroneState(position=tuple(position))

    def set_position(self, position: tuple[float, float, float]) -> None:
        """Move the drone body to a new position."""

        self._require_body()
        p.resetBasePositionAndOrientation(self.body_id, position, (0.0, 0.0, 0.0, 1.0))

    def _create_arm(
        self,
        half_extents: tuple[float, float, float],
        local_offset: tuple[float, float, float],
    ) -> None:
        visual_id = p.createVisualShape(
            shapeType=p.GEOM_BOX,
            halfExtents=half_extents,
            rgbaColor=(0.2, 0.2, 0.2, 1.0),
        )
        collision_id = p.createCollisionShape(
            shapeType=p.GEOM_BOX,
            halfExtents=half_extents,
        )
        p.createMultiBody(
            baseMass=0.0,
            baseCollisionShapeIndex=collision_id,
            baseVisualShapeIndex=visual_id,
            basePosition=(
                self.start_position[0] + local_offset[0],
                self.start_position[1] + local_offset[1],
                self.start_position[2] + local_offset[2],
            ),
        )

    def _require_body(self) -> None:
        if self.body_id is None:
            raise RuntimeError("SimpleDrone.spawn() must be called before controlling the drone.")