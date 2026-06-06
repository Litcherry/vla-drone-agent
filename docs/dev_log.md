# Development Log

## Day 1

- **今日完成内容：**今天完成了项目仓库创建、任务要求分析和初始模块设计。本地也开始配置 Ubuntu/WSL 开发环境，为后续在 Linux 环境下运行 PyBullet 仿真做准备。初步确定采用 PyBullet + rule-based planner + color perception 的最小闭环方案。
- **遇到的问题：**对 WSL、Ubuntu、PyBullet 和 gym-pybullet-drones 这些环境和工具不够熟悉；配置 WSL 时也遇到了 WSL2 不能直接使用的问题，提示需要启用“虚拟机平台”和虚拟化支持；
- **解决方式：**查找资料了解相关工具；检查 CPU 虚拟化状态，并启用 Windows 相关组件，继续完成 Ubuntu 环境安装。
- **AI 使用情况：**使用 AI 学习了解任务中不够熟悉的工具和知识；使用 AI 辅助分析任务要求、拆分模块；
- **明日计划：**完成 action schema、规则 Planner 和最小 PyBullet 场景搭建，让示例任务能够被解析为结构化 action list，并为后续无人机控制闭环做准备。