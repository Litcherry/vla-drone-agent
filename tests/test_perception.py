from perception.color_detector import ColorTargetDetector
from sim.world import PyBulletWorld


def test_color_detector_returns_known_target_position():
    world = PyBulletWorld(gui=False)
    world.connect()
    try:
        world.reset()
        detector = ColorTargetDetector(world)

        detection = detector.detect("red")

        assert detection is not None
        assert detection.color == "red"
        assert detection.position == (1.5, 0.8, 0.05)
        assert detection.source == "sim_observation"
    finally:
        world.disconnect()


def test_color_detector_returns_none_for_missing_target():
    world = PyBulletWorld(gui=False)
    world.connect()
    try:
        world.reset()
        detector = ColorTargetDetector(world)

        detection = detector.detect("yellow")  # type: ignore[arg-type]

        assert detection is None
    finally:
        world.disconnect()