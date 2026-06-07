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