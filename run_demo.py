"""Run a language-driven PyBullet drone demo."""

from __future__ import annotations

import argparse
import time
from typing import Any

from agent.planner import parse_instruction
from sim.controller import DroneController
from sim.drone import SimpleDrone
from sim.recorder import DemoRecorder
from sim.world import PyBulletWorld


def run_task(task: str, gui: bool = False, output_dir: str = "outputs") -> dict[str, Any]:
    """Run one natural language drone task and save demo artifacts."""

    started_at = time.time()
    actions = parse_instruction(task)

    world = PyBulletWorld(gui=gui)
    recorder = DemoRecorder(output_dir=output_dir)

    success = True
    failure_reason = ""
    final_error = 0.0

    world.connect()

    try:
        world.reset()
        drone = SimpleDrone()
        drone.spawn()
        controller = DroneController(world, drone, speed=0.025)

        recorder.record_event(
            {
                "event": "task_started",
                "instruction": task,
                "actions": actions,
            }
        )

        current_target: tuple[float, float, float] | None = None
        elapsed_steps = 0

        def record_step() -> None:
            nonlocal elapsed_steps
            position = drone.get_state().position
            recorder.record_trajectory(
                time_s=elapsed_steps * world.time_step,
                drone_position=position,
                target_position=current_target,
            )
            if elapsed_steps % 3 == 0:
                recorder.capture_frame()
            elapsed_steps += 1

        for index, action in enumerate(actions):
            action_name = action["action"]
            recorder.record_event({"event": "action_started", "index": index, "action": action})

            result = None

            if action_name == "takeoff":
                result = controller.takeoff(float(action["altitude"]), on_step=record_step)

            elif action_name == "search":
                target_color = action["target"]
                target_position = world.get_target_position(target_color)
                if target_position is None:
                    success = False
                    failure_reason = f"target_not_found:{target_color}"
                    recorder.record_event(
                        {
                            "event": "action_failed",
                            "index": index,
                            "action": action,
                            "reason": failure_reason,
                        }
                    )
                    break

                current_target = target_position
                recorder.record_event(
                    {
                        "event": "target_found",
                        "target": target_color,
                        "position": target_position,
                    }
                )

            elif action_name == "move_to":
                result = controller.move_to(tuple(action["position"]), on_step=record_step)

            elif action_name == "move_above":
                target_color = action["target"]
                base_position = world.get_target_position(target_color)
                if base_position is None:
                    success = False
                    failure_reason = f"target_not_found:{target_color}"
                    recorder.record_event(
                        {
                            "event": "action_failed",
                            "index": index,
                            "action": action,
                            "reason": failure_reason,
                        }
                    )
                    break

                target_position = (base_position[0], base_position[1], float(action["height"]))
                current_target = target_position
                result = controller.move_to(target_position, on_step=record_step)

            elif action_name == "hover":
                result = controller.hover(float(action["duration"]), on_step=record_step)

            elif action_name == "land":
                result = controller.land(on_step=record_step)

            else:
                success = False
                failure_reason = f"unsupported_action:{action_name}"
                break

            if result is not None:
                final_error = result.final_error
                recorder.record_event(
                    {
                        "event": "action_finished",
                        "index": index,
                        "action": action,
                        "success": result.success,
                        "final_error": result.final_error,
                        "steps": result.steps,
                        "reason": result.reason,
                    }
                )

                if not result.success:
                    success = False
                    failure_reason = result.reason
                    break

        duration = time.time() - started_at
        recorder.record_event(
            {
                "event": "task_finished",
                "success": success,
                "duration": duration,
                "final_position_error": final_error,
                "failure_reason": failure_reason,
            }
        )
        recorder.save()

        return {
            "success": success,
            "duration": duration,
            "final_position_error": final_error,
            "failure_reason": failure_reason,
            "actions": actions,
        }

    finally:
        world.disconnect()


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a language-driven drone demo.")
    parser.add_argument("--task", required=True, help="Natural language task instruction.")
    parser.add_argument("--gui", action="store_true", help="Use PyBullet GUI instead of DIRECT mode.")
    parser.add_argument("--output-dir", default="outputs", help="Directory for demo artifacts.")
    args = parser.parse_args()

    result = run_task(task=args.task, gui=args.gui, output_dir=args.output_dir)
    print(result)


if __name__ == "__main__":
    main()