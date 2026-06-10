"""Run a language-driven PyBullet drone demo."""

from __future__ import annotations

import argparse
import time
from typing import Any

from agent.planner_backend import PlannerMode, plan_instruction
from sim.controller import DroneController
from sim.drone import SimpleDrone
from sim.recorder import DemoRecorder
from sim.world import PyBulletWorld

from perception.color_detector import ColorTargetDetector

from agent.replanner import build_safe_fallback_plan
def classify_planning_error(exc: Exception) -> str:
    """Classify planning-stage failures for logging and evaluation."""

    message = str(exc).lower()

    if "unsupported target color" in message:
        return "planning_failed:unsupported_target_color"

    if "out of bounds" in message:
        return "planning_failed:safety_violation"

    if "invalid action plan" in message:
        return "planning_failed:schema_validation"

    if "could not parse instruction" in message:
        return "planning_failed:unparseable_instruction"

    return f"planning_failed:{type(exc).__name__}"

def run_task(
        task: str, 
        gui: bool = False, 
        output_dir: str = "outputs",
        planner: PlannerMode = "auto",
    ) -> dict[str, Any]:
    """Run one natural language drone task and save demo artifacts."""
    started_at = time.time()
    world = PyBulletWorld(gui=gui)
    recorder = DemoRecorder(output_dir=output_dir)

    try:
        plan_result = plan_instruction(task, mode=planner)
        actions = plan_result.actions
    except Exception as exc:
        failure_reason = classify_planning_error(exc)
        recorder.record_event(
            {
                "event": "task_started",
                "instruction": task,
                "planner": planner,
            }
        )
        recorder.record_event(
            {
                "event": "planning_failed",
                "success": False,
                "reason": failure_reason,
                "detail": str(exc),
            }
        )
        recorder.record_event(
            {
                "event": "task_finished",
                "success": False,
                "duration": time.time() - started_at,
                "final_position_error": "",
                "failure_reason": failure_reason,
            }
        )
        recorder.save()
        return {
            "success": False,
            "duration": time.time() - started_at,
            "final_position_error": "",
            "failure_reason": failure_reason,
            "actions": [],
            "planner": planner,
            "planner_fallback_reason": "",
        }

    success = True
    failure_reason = ""
    final_error = 0.0
    # started_at = time.time()
    # plan_result = plan_instruction(task, mode=planner)
    # actions = plan_result.actions

    # world = PyBulletWorld(gui=gui)
    # recorder = DemoRecorder(output_dir=output_dir)


    # success = True
    # failure_reason = ""
    # final_error = 0.0

    world.connect()

    try:
        world.reset()
        drone = SimpleDrone()
        drone.spawn()
        controller = DroneController(world, drone, speed=0.025)
        detector = ColorTargetDetector(world)

        recorder.record_event(
            {
                "event": "task_started",
                "instruction": task,
                "actions": actions,
                "planner": plan_result.source,
                "planner_fallback_reason": plan_result.fallback_reason,
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

        def execute_fallback(reason: str) -> None:
            fallback_actions = build_safe_fallback_plan(reason)
            recorder.record_event(
                {
                    "event": "fallback_started",
                    "reason": reason,
                    "actions": fallback_actions,
                }
            )

            for fallback_index, fallback_action in enumerate(fallback_actions):
                fallback_name = fallback_action["action"]
                fallback_result = None

                recorder.record_event(
                    {
                        "event": "fallback_action_started",
                        "index": fallback_index,
                        "action": fallback_action,
                    }
                )

                if fallback_name == "hover":
                    fallback_result = controller.hover(
                        float(fallback_action["duration"]),
                        on_step=record_step,
                    )
                elif fallback_name == "land":
                    fallback_result = controller.land(on_step=record_step)

                recorder.record_event(
                    {
                        "event": "fallback_action_finished",
                        "index": fallback_index,
                        "action": fallback_action,
                        "success": fallback_result.success if fallback_result else False,
                        "final_error": fallback_result.final_error if fallback_result else None,
                        "steps": fallback_result.steps if fallback_result else 0,
                        "reason": fallback_result.reason if fallback_result else "unsupported_fallback_action",
                    }
                )

            recorder.record_event({"event": "fallback_finished", "reason": reason})

        for index, action in enumerate(actions):
            action_name = action["action"]
            recorder.record_event({"event": "action_started", "index": index, "action": action})

            result = None

            if action_name == "takeoff":
                result = controller.takeoff(float(action["altitude"]), on_step=record_step)

            elif action_name == "search":
                target_color = action["target"]
                detection = detector.detect(target_color)
                if detection is None:
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
                    execute_fallback(failure_reason)
                    break

                current_target = detection.position
                recorder.record_event(
                    {
                        "event": "target_found",
                        "target": target_color,
                        "position": detection.position,
                        "source": detection.source,
                    }
                )

            elif action_name == "move_to":
                result = controller.move_to(tuple(action["position"]), on_step=record_step)

            elif action_name == "move_above":
                target_color = action["target"]
                detection = detector.detect(target_color)
                if detection is None:
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
                    execute_fallback(failure_reason)
                    break

                base_position = detection.position
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
                execute_fallback(failure_reason)
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
                    execute_fallback(failure_reason)
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
            "planner": plan_result.source,
            "planner_fallback_reason": plan_result.fallback_reason,
        }

    finally:
        world.disconnect()


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a language-driven drone demo.")
    parser.add_argument("--task", required=True, help="Natural language task instruction.")
    parser.add_argument("--gui", action="store_true", help="Use PyBullet GUI instead of DIRECT mode.")
    parser.add_argument("--output-dir", default="outputs", help="Directory for demo artifacts.")
    parser.add_argument(
        "--planner",
        choices=["auto", "llm", "rule"],
        default="auto",
        help="Planner backend: auto tries LLM first and falls back to rules.",
    )
    args = parser.parse_args()

    
    result = run_task(
        task=args.task,
        gui=args.gui,
        output_dir=args.output_dir,
        planner=args.planner,
    )
    print(result)


if __name__ == "__main__":
    main()