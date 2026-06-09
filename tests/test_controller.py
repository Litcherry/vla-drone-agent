from sim.controller import DroneController
from sim.drone import SimpleDrone
from sim.world import PyBulletWorld


def test_controller_takeoff_hover_and_land():
    world = PyBulletWorld(gui=False)
    world.connect()
    try:
        world.reset()
        drone = SimpleDrone()
        drone.spawn()
        controller = DroneController(world, drone)

        takeoff_result = controller.takeoff(1.0)
        assert takeoff_result.success
        assert drone.get_state().position[2] > 0.9

        hover_result = controller.hover(0.2)
        assert hover_result.success

        land_result = controller.land()
        assert land_result.success
        assert drone.get_state().position[2] < 0.15
    finally:
        world.disconnect()


def test_controller_move_to_target_position():
    world = PyBulletWorld(gui=False)
    world.connect()
    try:
        world.reset()
        drone = SimpleDrone()
        drone.spawn()
        controller = DroneController(world, drone)

        result = controller.move_to((0.5, -0.5, 1.0))

        assert result.success
        x, y, z = drone.get_state().position
        assert abs(x - 0.5) < 0.1
        assert abs(y + 0.5) < 0.1
        assert abs(z - 1.0) < 0.1
    finally:
        world.disconnect()