# Hermes Harness 通用项目开发方法

日期：2026-04-14

## 目标

给出一套适用于“任何新项目起步阶段”的通用 harness 方法，让你以后只要输入需求，就能先用本仓库选方法，再启动新项目。

## 核心结论

不要先问“让 Hermes 写什么代码”，要先问：
- 这是什么项目类型
- 这个项目的 source of truth 应该放在哪里
- 最小控制面是什么
- 什么叫 done
- 结果如何验证

## 三层心智模型

### 第 1 层：模型层
基础模型负责推理与生成。

### 第 2 层：runtime 层
Hermes、Claude Code、Codex、OpenCode 等属于执行层。

### 第 3 层：harness 层
harness 决定：
- 目录如何组织
- 计划如何写
- 验证如何跑
- 实验和运行如何登记
- 人和 agent 如何协作

## 启动新项目的标准顺序

1. 先查 `docs/catalog/project-types.md`
2. 选择项目类型方法
3. 先建立控制面，再让 agent 写大块实现
4. 先做最小 batch，再扩大范围
5. 每个 batch 结束都做验证与文档同步

## Runtime 能力预检

在真正执行大任务前，Hermes 应把 runtime 能力映射成 harness 决策，而不是反过来让工具能力主导项目：

- 如果要并发：先定义子任务边界、toolsets、验证命令和 handoff artifact
- 如果任务很长：先写 active plan，再使用 background / watch_patterns / focused compression
- 如果依赖 provider 稳定性：记录模型、fallback、timeout、代理和成本约束
- 如果要定时执行：cron prompt 必须自足，并只启用必要 toolsets
- 如果要固化自动化：优先从 runbook + script + test 开始，再考虑 plugin / shell hook
- 如果用户问“有没有更新”：先按 `docs/runbooks/hermes-method-update-sync.md` 检查，不要凭记忆回答

## 所有新项目都建议具备的最小骨架

- `README.md`
- `AGENTS.md`
- `ARCHITECTURE.md`
- `docs/README.md`
- `docs/specs/`
- `docs/plans/active/`
- `docs/runbooks/`
- `tests/` 或其他验证入口
- `Makefile`
- CI

## 如果你明天开始一个新项目

最推荐的操作方式是直接告诉 Hermes：

“请先根据当前需求阅读这个 harness 参考仓库，判断项目类型，选择最匹配的方法；如果现有文档缺少该项目类型，就先补齐该类型 playbook 和最小控制面，再开始项目实现。”

## 常见反模式

- 没有项目类型判断就直接进入实现
- 把 agent runtime 当作方法本身
- 没有控制面就追求自动化
- 只有实现，没有计划、验证、交接面
