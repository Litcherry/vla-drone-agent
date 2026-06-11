"""Recording utilities for trajectories, events, and rendered demo video."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import imageio.v2 as imageio
import pybullet as p

from sim.controller import distance
from sim.drone import SimpleDrone
from sim.world import PyBulletWorld


class DemoRecorder:
    """Record trajectory rows, event logs, and PyBullet camera frames."""

    def __init__(
        self,
        output_dir: str | Path = "outputs",
        video_name: str = "demo.mp4",
        fps: int = 20,
    ) -> None:
        self.output_dir = Path(output_dir)
        self.video_name = video_name
        self.fps = fps
        self.trajectory_rows: list[dict[str, Any]] = []
        self.events: list[dict[str, Any]] = []
        self.frames: list[Any] = []

    @property
    def trajectory_path(self) -> Path:
        return self.output_dir / "trajectory.csv"

    @property
    def events_path(self) -> Path:
        return self.output_dir / "events.jsonl"

    @property
    def video_path(self) -> Path:
        return self.output_dir / self.video_name

    def record_trajectory(
        self,
        time_s: float,
        drone_position: tuple[float, float, float],
        target_position: tuple[float, float, float] | None = None,
    ) -> None:
        """Record a single trajectory row."""

        if target_position is None:
            target_x = target_y = target_z = ""
            error = ""
        else:
            target_x, target_y, target_z = target_position
            error = distance(drone_position, target_position)

        x, y, z = drone_position
        self.trajectory_rows.append(
            {
                "time": round(time_s, 3),
                "x": round(x, 4),
                "y": round(y, 4),
                "z": round(z, 4),
                "target_x": target_x,
                "target_y": target_y,
                "target_z": target_z,
                "error": error if error == "" else round(error, 4),
            }
        )

    def record_event(self, event: dict[str, Any]) -> None:
        """Record one structured event."""

        self.events.append(event)

    def capture_frame(self) -> None:
        """Capture one RGB frame from the PyBullet scene."""

        view_matrix = p.computeViewMatrix(
            cameraEyePosition=(3.8, -4.0, 2.8),
            cameraTargetPosition=(0.0, 0.0, 0.7),
            cameraUpVector=(0.0, 0.0, 1.0),
        )
        projection_matrix = p.computeProjectionMatrixFOV(
            fov=60,
            aspect=16 / 9,
            nearVal=0.1,
            farVal=20.0,
        )
        width, height, rgba, _, _ = p.getCameraImage(
            width=960,
            height=544,
            viewMatrix=view_matrix,
            projectionMatrix=projection_matrix,
            renderer=p.ER_BULLET_HARDWARE_OPENGL,
        )
        frame = rgba[:, :, :3]
        self.frames.append(frame)

    def save(self) -> None:
        """Write all recorded outputs to disk."""

        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._write_trajectory()
        self._write_events()
        self._write_video()

    def _write_trajectory(self) -> None:
        fieldnames = ["time", "x", "y", "z", "target_x", "target_y", "target_z", "error"]
        with self.trajectory_path.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.trajectory_rows)

    def _write_events(self) -> None:
        with self.events_path.open("w", encoding="utf-8") as file:
            for event in self.events:
                file.write(json.dumps(event, ensure_ascii=False) + "\n")

    def _write_video(self) -> None:
        if not self.frames:
            return
        imageio.mimsave(self.video_path, self.frames, fps=self.fps)