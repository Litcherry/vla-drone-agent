# VLA Drone Agent

A minimal reproducible VLA-style drone agent demo for language-driven planning, color target perception, PyBullet simulation control, safety checking, and experiment logging.

## Goal

This project implements a minimal closed-loop drone agent that converts natural language instructions into structured actions and executes them in a PyBullet simulation.

Example instruction:

```text
起飞，找到红色目标，飞到它上方 1 米处悬停 5 秒，然后降落。
```

Expected action list:

```json
[
  {"action": "takeoff", "altitude": 1.5},
  {"action": "search", "target": "red"},
  {"action": "move_above", "target": "red", "height": 1.0},
  {"action": "hover", "duration": 5},
  {"action": "land"}
]
```

## Planned Modules

- Planner: rule-based Chinese/English instruction parser with schema validation.
- Perception: color target localization for red, blue, and green objects.
- Controller: PyBullet drone control for takeoff, search, move, hover, and land.
- Agent Loop: action execution, state checking, fallback, and event logging.
- Evaluation: 10 natural language tasks with success/failure analysis.

## Reproducibility

```bash
pip install -r requirements.txt
python run_demo.py --task "起飞，找到红色目标，飞到它上方 1 米处悬停 5 秒，然后降落"
python experiments/evaluate.py --task-file experiments/tasks.json
```

