# Development Log

## Day 1

- **今日完成内容：**今天完成了项目仓库创建、任务要求分析和初始模块设计。本地也开始配置 Ubuntu/WSL 开发环境，为后续在 Linux 环境下运行 PyBullet 仿真做准备。初步确定采用 PyBullet + rule-based planner + color perception 的最小闭环方案。
- **遇到的问题：**对 WSL、Ubuntu、PyBullet 和 gym-pybullet-drones 这些环境和工具不够熟悉；配置 WSL 时也遇到了 WSL2 不能直接使用的问题，提示需要启用“虚拟机平台”和虚拟化支持；
- **解决方式：**查找资料了解相关工具；检查 CPU 虚拟化状态，并启用 Windows 相关组件，继续完成 Ubuntu 环境安装。
- **AI 使用情况：**使用 AI 学习了解任务中不够熟悉的工具和知识；使用 AI 辅助分析任务要求、拆分模块；
- **明日计划：**完成 action schema、规则 Planner 和最小 PyBullet 场景搭建，让示例任务能够被解析为结构化 action list，并为后续无人机控制闭环做准备。

## Day 2

### 今日完成内容

1. 完成 Action Schema 模块初步实现。基于 Pydantic 对 Planner 输出的 Action List 进行校验，能够检测并拒绝非法 Action、缺失必要参数以及超出约束范围的参数，保证后续执行模块接收到的任务计划合法可靠。
2. 完成 Safety 模块的初步实现。针对 takeoff、move_to、move_above 等动作增加边界检查，防止无人机飞出预设仿真空间。
3. 完成 Rule-based Planner 的初步实现。支持将中英文自然语言任务解析为结构化动作序列，并支持 red、blue、green 三类目标颜色以及 hover 持续时间参数的解析。
4. 编写 Schema 模块对应的单元测试，并通过 pytest 完成基础功能验证。

### 遇到的问题

1. 之前将项目目录建立在 Windows 文件系统中，我认为这不符合任务要求的”纯 Linux"环境。
2. 总是因为中文编码问题报错。

### 解决方式

1. 将远程仓库拉到 Ubuntu 磁盘中继续进行开发。
2. 项目根目录添加 `.editorconfig` 文件，使项目默认用 UTF-8，避免编程及复现时不必要的麻烦。

### AI 使用情况

1. 通过 AI 调研和学习任务所需的 python 库。
2. 通过 AI 修改报错代码、分析报错原因。
3. 参考了 AI 对代码结构和工程组织方式提出的优化建议，包括：Pydantic、 Annotations、pytest、.editorconfig 等。更符合工程实践的开发工具与规范。

### 明日计划

1. 搭建最小 PyBullet 仿真场景，包括地面、彩色目标以及简化无人机模型。
2. 实现起飞、移动、悬停和降落等基础控制动作。
3. 开始记录 trajectory.csv 和 events.jsonl，为后续实验评估与结果分析做准备。

## Day 3

### 今日完成内容

1. 搭建了最小 PyBullet 仿真场景。实现 `PyBulletWorld`，能够创建地面和 red、blue、green 三类彩色目标，并提供目标位置查询接口。
2. 实现了简化无人机模型 `SimpleDrone`。当前无人机使用可见的 box 和机臂结构表示，重点用于展示无人机在仿真空间中的位置变化和任务执行过程。
3. 实现了基于位置控制的 `DroneController`，支持 takeoff、move_to、hover 和 land 等基础动作，并使用距离阈值判断动作是否到达目标位置。
4. 将 Planner、PyBullet World、Drone Controller 和 Recorder 串联到 `run_demo.py` 中，能够从自然语言任务生成 action list，并在仿真中执行。
5. 实现了 `DemoRecorder`，能够输出 `trajectory.csv`、`events.jsonl` 和 `demo.mp4`，展示轨迹、事件日志和演示视频。
6. 为 PyBullet world 和 controller 编写了基础测试，并通过 pytest 验证。

### 遇到的问题

1. 在 WSL Ubuntu 中测试 PyBullet GUI 时，窗口可以启动并渲染，但关闭时出现 segmentation fault。
2. 第一次生成的 `demo.mp4` 只有2秒，画面只记录了各动作结束后的状态，看起来不够连续，无法很好展示无人机起飞、移动、悬停和降落的完整过程。
3. 简化无人机模型和真实四旋翼动力学之间还有明显差距，目前控制方式更接近位置控制，而不是真实的底层飞控。

### 解决方式

1. 正式 demo 改为使用 PyBullet DIRECT 模式运行，并通过 `getCameraImage` 渲染仿真画面后保存为视频，避免依赖不稳定的交互式 GUI。
2. 将 recorder 接入 controller 的 step 回调，在无人机每一步移动后记录轨迹和视频帧，而不是等一个动作结束后再录制。这样重新生成的视频更加连续，能够更清楚地展示任务执行过程。
3. 在当前阶段明确采用最小闭环简化方案：无人机控制使用位置控制近似，先保证自然语言规划、目标定位、动作执行、状态记录和结果输出完整跑通，后续在报告中说明该简化与真实无人机控制之间的差距。

### AI 使用情况

1. 使用 AI 辅助梳理 PyBullet world、drone model、controller 和 recorder 的模块边界。
2. 使用 AI 辅助分析 PyBullet GUI 在 WSL 中出现 segmentation fault 报错的原因并参考建议选择更稳定的 DIRECT 渲染视频方案。
3. 使用 AI 解决 `demo.mp4` 过短的问题，修改为按仿真 step 录制轨迹和画面。

### 明日计划

1. 完成 Perception 模块，使 Agent 通过 perception 接口获取 red、blue、green 目标位置。
2. 增加 Agent Loop 中的失败处理和 fallback 逻辑，覆盖找不到目标、非法任务和越界任务等情况。
3. 编写 `experiments/tasks.json` 和 `experiments/evaluate.py`，设计至少 10 条自然语言任务，并输出 `results.csv`。