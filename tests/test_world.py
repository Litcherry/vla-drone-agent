from sim.world import PyBulletWorld


def test_world_creates_colored_targets():
    world = PyBulletWorld(gui=False)
    world.connect()
    try:
        world.reset()

        assert world.get_target_position("red") == (1.5, 0.8, 0.05)
        assert world.get_target_position("blue") == (-1.4, 1.0, 0.05)
        assert world.get_target_position("green") == (0.4, -1.6, 0.05)
        assert world.get_target_position("yellow") is None
    finally:
        world.disconnect()