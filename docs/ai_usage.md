

# AI 使用记录

本文件用于说明本项目中 AI 的使用范围、人工修改内容、验证方式以及仍然存在的不可靠部分。

## 1. 主要由自己实现和理解的部分

以下模块由本人根据任务要求进行设计、实现、调试和验证：

- 项目整体模块划分：Planner、Perception、Controller、Agent Loop、Safety、Recorder、Evaluation。
- 各模块及代码文件的详细功能设计。
- 根据运行结果调整系统逻辑，包括 LLM fallback、planning failure 分类、missing target fallback 和安全降落策略等。
- `experiments/evaluate.py`：批量运行 10 条自然语言任务并生成 `outputs/results.csv`
- 测试用例：使用 pytest 对 planner、schema、world、controller、perception、LLM fallback、run_demo 和 evaluation 相关逻辑进行验证
- 撰写 README、开发日志、AI 使用记录、实验报告和 research note，确保项目过程和 AI 使用情况可解释、可复现。

## 2. 参考的开源项目和资料

本项目主要使用以下开源库和工具：

- PyBullet：用于无人机仿真环境、目标物体创建和画面渲染。
- Pydantic：用于 Planner 输出的 action schema 校验。
- OpenAI Python SDK：用于调用 OpenAI-compatible LLM API。
- imageio / imageio-ffmpeg：用于将 PyBullet 渲染帧保存为 demo.mp4。
- pytest：用于单元测试和回归验证。
- pandas / csv：用于实验结果整理。

本项目没有直接复制大型开源无人机 Agent 项目的代码。系统结构主要根据任务要求自行拆分和实现。

## 3. 使用 AI 辅助的部分

AI 主要用于以下方面：

- 辅助理解任务要求，提供可行建议。
- 使用 AI 辅助解释 WSL、Ubuntu、PyBullet、gym-pybullet-drones、VLA、Embodied Agent、LLM Planner、fallback 等概念进行学习。
- 使用 AI 辅助学习了 Callable，StepCallback，pytest，pydantic库，typing 库等的用法。
- 辅助制定开发路线、commit 计划和 PR 规划。
- 辅助生成代码，大部分代码均由 AI 根据本人功能描述生成。
- 辅助分析报错原因，例如 UTF-8 编码问题、PyBullet GUI 在 WSL 中关闭时报 segmentation fault、pytest import path 问题、LLM fallback 返回信息不完整等。
- 辅助搜集 research note 的候选论文。

## 4. AI 给出的不准确建议及相应修改

- AI 建议 windows 创建项目目录并使用 ubuntu 里的虚拟环境：我认为这不符合“纯 Linux“环境，于是将项目和环境都放在 ubuntu 系统里
- 根据实际任务要求调整了 Planner 支持的 action 类型和参数范围。
- AI 生成的 LLM Planner 和 rule Planner的调用逻辑过于简单：我将其修改为 auto/rule/llm 三种模式
- 代码没有进行报错友好处理：调整代码进行报错友好处理。
- 代码初步生成的视频过短（只在 action 结束后记录少量帧）：将 recorder 接入 controller step 回调，使飞行过程能够连续记录。
- AI 生成的代码报错没有进行详细分类：我将 planning failure 从粗略的 `ValueError` 分类为更清晰的失败原因，例如 `planning_failed:safety_violation`、`planning_failed:unsupported_target_color` 和 `planning_failed:unparseable_instruction`。
- 缺少 missing target 场景：增加 missing target 场景，使合法目标在环境中缺失时能够触发 Agent Loop fallback。

- AI 对 unsupported color 的处理最初采用枚举 yellow、purple 等方式，不够通用：改为检测非 red/blue/green 的颜色目标表达并明确拒绝。

## 5. 如何验证代码正确性

### 方法一：直接阅读检查代码

直接阅读代码，查看有没有明显逻辑错误。

### 方法二：使用 pytest 进行代码测试

使用 `pytest -q` 运行单元测试和集成测试，目前测试覆盖：
- action schema validation；
- safety boundary check；
- rule planner parsing；
- LLM planner fallback；
- PyBullet world target creation；
- drone controller actions；
- perception target detection；
- run_demo planning failure handling；
- missing target fallback。

手动运行单条 demo：

```bash
python run_demo.py --planner rule --task "起飞，找到红色目标，飞到它上方1米处悬停5秒，然后降落"
```

手动验证 LLM fallback：

```
python run_demo.py --planner auto --task "起飞，找到红色目标，飞到它上方1米处悬停5秒，然后降落"
```

手动验证失败场景：

```bash
python run_demo.py --planner rule --missing-target red --task "起飞，找到红色目标，飞到它上方1米处悬停5秒，然后降落"
python run_demo.py --planner rule --task "起飞，找到青色目标，然后降落"
python run_demo.py --planner rule --task "take off, move to x=5 y=0 z=1, hover 2 seconds, then land"
```

### 方法三：运行批量评估

```bash
python experiments/evaluate.py --task-file experiments/tasks.json
```

### 方法四：检查输出文件

- `outputs/demo.mp4`：确认画面中能看到无人机、目标和飞行过程；
- `outputs/trajectory.csv`：确认记录了无人机位置、目标位置和误差；
- `outputs/events.jsonl`：确认记录了 action 状态、失败原因和 fallback；
- `outputs/results.csv`：确认 10 条任务的成功率、耗时、误差和失败原因分类。

## 6. 仍然不可靠的部分

当前 demo 仍存在以下简化和不足：

- Perception 当前使用 PyBullet simulator observation 获取目标位置，而不是从 RGB 图像中完成目标检测和世界坐标转换。
- 无人机控制采用简化位置控制，没有实现真实四旋翼动力学、PID 控制或电机级控制。
- Rule Planner 只能覆盖受控表达，不能理解任意自然语言。
- fallback replanning 采用保守策略：短暂悬停后降落，没有实现复杂的重新搜索或重新生成完整任务计划。
- 当前仿真环境较简单，没有动态障碍物、风扰动、多目标遮挡和真实传感器噪声。
- 若迁移到真实无人机，还需要补充视觉检测、深度估计、状态估计、避障、低层飞控、安全 geofence 和硬件通信等能力。
