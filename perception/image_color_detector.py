"""Image-based color detector using PyBullet camera RGB and depth images."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import cv2
import numpy as np
import pybullet as p


TargetColor = Literal["red", "blue", "green"]


@dataclass(frozen=True)
class ImageDetectionResult:
    """Image-based color detection result."""

    color: TargetColor
    pixel_center: tuple[int, int]
    bbox: tuple[int, int, int, int]
    confidence: float
    position: tuple[float, float, float]
    source: str = "image_color_segmentation"


class ImageColorDetector:
    """Detect colored targets from PyBullet RGB/depth camera observations."""

    def __init__(
        self,
        width: int = 960,
        height: int = 544,
        camera_eye: tuple[float, float, float] = (3.8, -4.0, 2.8),
        camera_target: tuple[float, float, float] = (0.0, 0.0, 0.7),
    ) -> None:
        self.width = width
        self.height = height
        self.camera_eye = camera_eye
        self.camera_target = camera_target
        self.near = 0.1
        self.far = 20.0
        self.fov = 60.0
        self.aspect = width / height

    def detect(self, color: TargetColor) -> ImageDetectionResult | None:
        """Detect a color blob and estimate its world position."""

        rgb, depth, view_matrix, projection_matrix = self._capture()
        mask = self._build_color_mask(rgb, color)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return None

        contour = max(contours, key=cv2.contourArea)
        area = float(cv2.contourArea(contour))
        image_area = float(self.width * self.height)
        confidence = area / image_area

        if area < 20.0:
            return None

        x, y, w, h = cv2.boundingRect(contour)
        center_u = int(x + w / 2)
        center_v = int(y + h / 2)

        world_position = unproject_pixel_to_world(
            pixel=(center_u, center_v),
            depth_buffer=float(depth[center_v, center_u]),
            width=self.width,
            height=self.height,
            view_matrix=view_matrix,
            projection_matrix=projection_matrix,
        )

        return ImageDetectionResult(
            color=color,
            pixel_center=(center_u, center_v),
            bbox=(x, y, w, h),
            confidence=confidence,
            position=world_position,
        )

    def _capture(self) -> tuple[np.ndarray, np.ndarray, list[float], list[float]]:
        view_matrix = p.computeViewMatrix(
            cameraEyePosition=self.camera_eye,
            cameraTargetPosition=self.camera_target,
            cameraUpVector=(0.0, 0.0, 1.0),
        )
        projection_matrix = p.computeProjectionMatrixFOV(
            fov=self.fov,
            aspect=self.aspect,
            nearVal=self.near,
            farVal=self.far,
        )

        _, _, rgba, depth, _ = p.getCameraImage(
            width=self.width,
            height=self.height,
            viewMatrix=view_matrix,
            projectionMatrix=projection_matrix,
            renderer=p.ER_BULLET_HARDWARE_OPENGL,
        )

        rgb = np.asarray(rgba[:, :, :3], dtype=np.uint8)
        depth_array = np.asarray(depth, dtype=np.float32)
        return rgb, depth_array, view_matrix, projection_matrix

    def _build_color_mask(self, rgb: np.ndarray, color: TargetColor) -> np.ndarray:
        hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)

        if color == "red":
            lower1 = np.array([0, 80, 80])
            upper1 = np.array([10, 255, 255])
            lower2 = np.array([170, 80, 80])
            upper2 = np.array([180, 255, 255])
            mask1 = cv2.inRange(hsv, lower1, upper1)
            mask2 = cv2.inRange(hsv, lower2, upper2)
            mask = cv2.bitwise_or(mask1, mask2)
        elif color == "blue":
            lower = np.array([95, 80, 60])
            upper = np.array([130, 255, 255])
            mask = cv2.inRange(hsv, lower, upper)
        elif color == "green":
            lower = np.array([35, 60, 50])
            upper = np.array([85, 255, 255])
            mask = cv2.inRange(hsv, lower, upper)
        else:
            raise ValueError(f"Unsupported color: {color}")

        kernel = np.ones((3, 3), dtype=np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        return mask


def unproject_pixel_to_world(
    pixel: tuple[int, int],
    depth_buffer: float,
    width: int,
    height: int,
    view_matrix: list[float],
    projection_matrix: list[float],
) -> tuple[float, float, float]:
    """Convert a pixel and depth buffer value into a PyBullet world coordinate."""

    u, v = pixel
    x_ndc = (2.0 * u / width) - 1.0
    y_ndc = 1.0 - (2.0 * v / height)
    z_ndc = 2.0 * depth_buffer - 1.0

    clip = np.array([x_ndc, y_ndc, z_ndc, 1.0], dtype=np.float64)

    view = np.array(view_matrix, dtype=np.float64).reshape(4, 4, order="F")
    projection = np.array(projection_matrix, dtype=np.float64).reshape(4, 4, order="F")
    inv_view_projection = np.linalg.inv(projection @ view)

    world = inv_view_projection @ clip
    world = world / world[3]

    return (float(world[0]), float(world[1]), float(world[2]))