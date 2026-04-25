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
- 如果用户要求 intake `agent-skills` 或类似 workflow pack：按 `docs/runbooks/agent-skills-method-intake.md`，先把外部方法映射到本仓库 source-of-truth surfaces

## 任务级 workflow selection

本仓库先做“项目级 harness 选择”，再做“任务级 workflow 选择”。
这吸收了 `agent-skills` 的有用部分，但不把外部仓库作为 source of truth。

标准顺序：

1. 先按 `docs/catalog/project-types.md` 判断项目类型
2. 读取对应 playbook / runbook / spec / active plan
3. 再判断当前动作属于哪个 task-level workflow
4. 把结果写回本仓库工件，而不是只留在聊天里

| 当前动作 | 采用的 task-level workflow | 本仓库落点 |
|---|---|---|
| 想法模糊 | idea refine / requirement clarification | `docs/specs/` 或 active plan 的 open questions |
| 新项目 / 新功能 / 大改动 | spec-driven development | `docs/specs/`，必要时 ADR |
| 已有 spec，需要拆解 | planning and task breakdown | `docs/plans/active/` |
| 多文件实现 | incremental implementation | bounded batch + verification |
| 行为变化 / bugfix | test-driven development | 先写/更新测试，再实现 |
| 测试失败 / 异常行为 | debugging and error recovery | reproduce / localize / fix / guard |
| 合并前检查 | code review and quality | diff review + verification story |
| 发布 / 交付 | shipping and launch | go/no-go + rollback plan |

每个 task-level workflow 都应包含：

- When to use / when not to use
- Inputs
- Process
- Common rationalizations（agent 容易跳步的借口）
- Red flags
- Verification evidence

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
