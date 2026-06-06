# 纯 Linux 环境下语言-视觉-动作 Agent 控制无人机的最小闭环复现任务

## 一、任务背景

本任务用于考察你在 **VLA（Vision-Language-Action）/ Embodied Agent / 无人系统控制 / 工程复现** 方向的综合能力。

任务重点不在于做一个复杂炫目的系统，而在于你是否能够在有限时间内完成一个 **可运行、可解释、可复现、可迭代** 的最小闭环 demo，并通过 GitHub 开发历史体现真实的工程推进过程。

本任务允许使用 AI 工具辅助开发，但必须如实记录 AI 使用范围。考核重点不是“能不能生成代码”，而是你是否能设计系统、验证代码、解释结果、发现问题并持续迭代。

## 二、任务周期

5 天。

## 三、任务目标

在 Ubuntu/Linux 环境下，实现一个自然语言指令驱动的无人机仿真系统。

系统需要根据语言指令完成：

1. 任务分解；
2. 目标感知；
3. 动作规划；
4. 无人机控制；
5. 状态检查；
6. 失败重规划；
7. 实验记录与结果分析。

示例输入指令：

```text
起飞，找到红色目标，飞到它上方 1 米处悬停 5 秒，然后降落。
```

系统应解析为类似如下结构化动作序列：

```json
[
  {"action": "takeoff", "altitude": 1.5},
  {"action": "search", "target": "red"},
  {"action": "move_above", "target": "red", "height": 1.0},
  {"action": "hover", "duration": 5},
  {"action": "land"}
]
```

随后系统应在仿真环境中执行该任务，并保存演示视频、轨迹、事件日志和实验结果。

## 四、环境限制

1. 必须在 Linux 环境运行；
2. Python 3.10+；
3. 使用 PyBullet 或 gym-pybullet-drones；
4. 不使用 AirSim、Unity、Unreal 或 Windows 专属工具；
5. 可以使用 LLM API 或本地模型辅助 Planner，但必须保留规则 fallback；
6. 可以使用 AI 辅助开发，但必须在文档中如实记录。

## 五、核心模块要求

### 1. Planner

要求：

- 输入中文或英文自然语言；
- 输出 JSON 格式 action list；
- 使用 schema 校验 action list；
- 对非法 action、缺失参数、越界任务进行拒绝或修正；
- 若使用 LLM，需要提供规则 fallback，避免系统完全依赖外部 API。

至少支持以下动作：

```text
takeoff
search
move_to
move_above
hover
land
```

### 2. Perception

要求：

- 至少支持红、蓝、绿三种颜色目标定位；
- 能从仿真画面或环境观测中定位目标；
- 输出目标位置；
- 说明视觉坐标或观测信息如何转化为控制目标；
- 可以使用简单颜色检测，不强制使用 GroundingDINO、CLIP 或开放词汇检测模型。

### 3. Controller

要求：

- 支持 `takeoff`、`search`、`move_to`、`move_above`、`hover`、`land`；
- 能控制仿真无人机完成动作，而不是只打印动作；
- 记录无人机位置、目标位置、控制误差；
- 输出 `trajectory.csv`；
- 说明到达判定阈值，例如距离目标小于多少视为到达。

### 4. Agent Loop

要求：

- 按 Planner 输出的 action list 执行任务；
- 每一步执行后检查状态；
- 找不到目标、动作失败或越界时，至少进行一次 replan 或 fallback；
- 输出 `events.jsonl`，记录每一步动作、状态、结果和失败原因。

### 5. Safety

要求：

- 支持仿真空间边界检查；
- 对越界目标、非法 action、找不到目标等情况进行处理；
- 不能因为 planner 输出错误动作导致程序直接崩溃；
- 需要在报告中说明 safety 设计。

## 六、实验要求

至少设计 10 条自然语言任务，覆盖以下情况：

1. 正常任务；
2. 不同颜色目标；
3. 不同 hover 时间；
4. 找不到目标；
5. 越界或非法任务；
6. 需要 fallback 或 replan 的任务。

输出 `results.csv`，至少包含：

```text
task_id
instruction
success
duration
final_position_error
failure_reason
```

需要统计：

- 成功率；
- 平均任务耗时；
- 平均最终位置误差；
- 失败原因分类；
- 至少 3 个失败案例分析。
- demo.mp4 必须包含 PyBullet/gym-pybullet-drones 仿真画面，画面中应能清楚看到无人机模型、目标物、飞行轨迹或位置变化，以及起飞、移动、悬停、降落过程。不接受仅包含终端输出、PPT、静态截图或日志滚动的视频。

## 七、Research Note 要求

选择一篇 VLA / Embodied Agent / Robot Agent 相关论文或开源项目，写一份 2-3 页 research note。

可选方向包括但不限于：

- SayCan；
- RT-1 / RT-2；
- OpenVLA；
- VIMA；
- Voyager；
- Octo；
- PaLM-E；
- EmbodiedGPT；
- UAV-Agent / DroneGPT 相关工作。

research note 需要回答：

1. 原方法解决什么问题；
2. 核心思想是什么；
3. 本 demo 复现或借鉴了哪一部分；
4. 本 demo 做了哪些简化；
5. 如果迁移到真实无人机，还缺哪些关键能力；
6. 你认为该方向最核心的研究难点是什么。

## 八、GitHub 开发过程要求

最终结果不是唯一考核对象。请从空仓库开始开发，保留完整 GitHub 开发历史。

要求：

1. 从空仓库开始；
2. 不接受最后一天一次性上传完整项目；
3. 每天至少 2 个有效 commit；
4. 总 commit 数不少于 10；
5. commit message 必须具体，不能只写 `update`、`fix`、`final`；
8. 至少提交 2 个 pull request，可以自己 merge，但 PR 中要说明改动内容；
9. 每天在 `docs/dev_log.md` 或 GitHub issue 中写 progress log；

建议 issue 包括：

```text
environment setup
planner design
perception module
controller module
agent loop and safety
evaluation and report
```

每日 progress log 格式：

```text
Day N:
- 今天完成了什么；
- 遇到了什么问题；
- 如何解决；
- 哪些地方使用了 AI；
- 明天计划做什么。
```

## 九、AI 使用记录要求

必须提交 `docs/ai_usage.md`。

内容包括：

1. 哪些模块主要由自己实现；
2. 哪些模块参考了开源项目；
3. 哪些模块使用了 AI 辅助；
4. AI 生成的代码中你修改了什么；
5. AI 给过哪些错误建议；
6. 你如何验证代码正确；
7. 哪些部分你认为仍然不可靠。

允许使用 AI，但必须能够解释、验证和修改 AI 生成的内容。

## 十、建议仓库结构

```text
vla-drone-agent/
  README.md
  requirements.txt
  run_demo.py
  agent/
    planner.py
    schema.py
    safety.py
    replanner.py
  perception/
    color_detector.py
    camera.py
  sim/
    world.py
    drone.py
    controller.py
    recorder.py
  experiments/
    tasks.json
    evaluate.py
  outputs/
    demo.mp4
    trajectory.csv
    events.jsonl
    results.csv
  docs/
    dev_log.md
    ai_usage.md
    report.pdf
    research_note.pdf
```

可以调整结构，但需要保持模块边界清晰。

## 十一、最终提交物

请提交以下内容：

1. GitHub 仓库链接；
2. `README.md`；
3. `requirements.txt`；
4. `run_demo.py`；
5. `outputs/demo.mp4`；
6. `outputs/trajectory.csv`；
7. `outputs/events.jsonl`；
8. `outputs/results.csv`；
9. `docs/dev_log.md`；
10. `docs/ai_usage.md`；
11. `docs/report.pdf`；
12. `docs/research_note.pdf`。

README 必须包含可复现命令，例如：

```bash
pip install -r requirements.txt
python run_demo.py --task "起飞，找到红色目标，飞到它上方 1 米处悬停 5 秒，然后降落"
python experiments/evaluate.py --task-file experiments/tasks.json
```

本任务不要求系统复杂，但要求真实、可运行、可解释。
