from perception.image_color_detector import ImageColorDetector
from sim.world import PyBulletWorld


def test_image_color_detector_detects_red_target():
    world = PyBulletWorld(gui=False)
    world.connect()
    try:
        world.reset()
        detector = ImageColorDetector()

        detection = detector.detect("red")

        assert detection is not None
        assert detection.color == "red"
        assert detection.confidence > 0.0
        assert detection.source == "image_color_segmentation"
    finally:
        world.disconnect()