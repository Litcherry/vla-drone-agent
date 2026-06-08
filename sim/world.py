"""PyBullet world setup for the drone agent demo."""

from __future__ import annotations

from dataclasses import dataclass

import pybullet as p
import pybullet_data


@dataclass(frozen=True)
class TargetObject:
    
    """A colored target object in the simulation world."""

    color: str
    position: tuple[float, float, float]
    body_id: int


class PyBulletWorld:
    """Minimal PyBullet world with a plane and colored targets."""

    def __init__(self, gui: bool = True, time_step: float = 1.0 / 60.0) -> None:
        self.gui = gui
        self.time_step = time_step
        self.client_id: int | None = None
        self.targets: dict[str, TargetObject] = {}

    def connect(self) -> None:
        """Connect to PyBullet and configure basic simulation settings."""

        if self.client_id is not None:
            return

        connection_mode = p.GUI if self.gui else p.DIRECT
        self.client_id = p.connect(connection_mode)
        p.setAdditionalSearchPath(pybullet_data.getDataPath())
        p.setGravity(0, 0, -9.8)
        p.setTimeStep(self.time_step)

    def reset(self) -> None:
        """Reset the world and recreate static scene objects."""

        self._require_connection()
        p.resetSimulation()
        p.setGravity(0, 0, -9.8)
        p.setTimeStep(self.time_step)

        p.loadURDF("plane.urdf")
        self.targets = {}
        self._create_target("red", (1.5, 0.8, 0.05), (1.0, 0.0, 0.0, 1.0))
        self._create_target("blue", (-1.4, 1.0, 0.05), (0.0, 0.1, 1.0, 1.0))
        self._create_target("green", (0.4, -1.6, 0.05), (0.0, 0.8, 0.1, 1.0))

        p.resetDebugVisualizerCamera(
            cameraDistance=5.0,
            cameraYaw=45,
            cameraPitch=-35,
            cameraTargetPosition=(0.0, 0.0, 0.5),
        )

    def step(self, steps: int = 1) -> None:
        """Advance the simulation."""

        self._require_connection()
        for _ in range(steps):
            p.stepSimulation()

    def get_target_position(self, color: str) -> tuple[float, float, float] | None:
        """Return the target position for a color if it exists."""

        target = self.targets.get(color)
        if target is None:
            return None
        return target.position

    def disconnect(self) -> None:
        """Disconnect from PyBullet."""

        if self.client_id is not None:
            p.disconnect()
            self.client_id = None

    def _create_target(
        self,
        color: str,
        position: tuple[float, float, float],
        rgba: tuple[float, float, float, float],
    ) -> None:
        visual_id = p.createVisualShape(
            shapeType=p.GEOM_SPHERE,
            radius=0.12,
            rgbaColor=rgba,
        )
        collision_id = p.createCollisionShape(
            shapeType=p.GEOM_SPHERE,
            radius=0.12,
        )
        body_id = p.createMultiBody(
            baseMass=0.0,
            baseCollisionShapeIndex=collision_id,
            baseVisualShapeIndex=visual_id,
            basePosition=position,
        )
        self.targets[color] = TargetObject(color=color, position=position, body_id=body_id)

    def _require_connection(self) -> None:
        if self.client_id is None:
            raise RuntimeError("PyBulletWorld.connect() must be called before using the world.")