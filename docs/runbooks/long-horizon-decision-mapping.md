# 长周期决策映射 Runbook

## 适用场景

满足以下特征之一时使用：

- 工作会跨多个会话、多人或多个 agent；
- 目标明确，但到达目标的路线仍有大量未知；
- 直接列实现任务会制造虚假确定性；
- 多个工作项被同一个架构、产品或数据决策阻塞。

如果路线已知，只需要执行既定任务，不要启动本 runbook；直接使用 active plan。

## 核心模型

长周期工作不是一份静态 backlog，而是一张逐步显影的地图：

- Destination：完成后可观察到的目标状态。
- Known reality：当前系统的真实约束和证据。
- Decisions so far：已经解决、会约束后续工作的决定。
- Frontier：当前最值得解决的下一个决策。
- Fog：知道存在，但还无法可靠拆分的区域。
- Not yet specified：尚未形成验收标准的能力。
- Out of scope：明确不进入当前路线的内容。
- Implementation tracks：决策完成后生成的可执行工作流。

地图的 canonical artifact 是 `docs/plans/active/<date>-<slug>.md`；issue tracker 可以镜像状态，但不能取代仓库计划。

## 流程

### 1. 定义 Destination

使用用户可观察或系统可验证的状态描述完成，不写“重构完成”“平台就绪”之类不可验证的口号。明确非目标和时间/兼容性约束。

### 2. 建立 Known Reality

通过仓库、运行结果、日志、数据和现有决策收集证据。区分：

- 已验证事实；
- 合理假设；
- 未知；
- 已知风险。

假设不能伪装成任务前提。

### 3. 创建 decision frontier

一个 decision item 应包含：

- 要决定什么；
- 为什么现在必须决定；
- 它阻塞哪些工作；
- 需要哪些证据；
- 候选方案和 trade-off；
- 完成标准：产生了哪个 spec/ADR/plan 更新。

默认每次只推进一个 frontier decision。只有证据收集相互独立时，才并行 research；最终决定仍由一个 owner 汇总。

### 4. 决策落地后再展开实现任务

每个 resolved decision 必须：

1. 写入 spec 或 ADR；
2. 从 Fog/Frontier 移到 Decisions so far；
3. 生成 dependency-aware implementation items；
4. 为新任务写验收和验证；
5. 更新所有被解除或新增的 blocker。

不得把“调查 X”标记为完成，却没有任何 durable artifact。

### 5. 按 tracer bullet 切片

优先拆成用户可见、端到端的最小能力，每个任务尽量包含所需的数据、逻辑、接口和验证。显式记录 `Blocked by`，只表示真实依赖，不表示建议顺序。

如果是无法垂直切片的大范围重构，使用：

1. expand：引入向后兼容的新结构；
2. migrate：逐个迁移调用方并验证；
3. contract：删除旧结构和兼容层。

### 6. 每次会话结束时维护地图

至少更新：

- 本次解决了什么决定；
- 新增了什么证据；
- 哪些任务现在 ready；
- 当前 frontier；
- 仍在 Fog 中的内容；
- 下一会话从哪里开始。

必要时从 `docs/templates/handoff-template.md` 生成 handoff，并只引用现有工件。

## 状态语义

建议使用：

- `pending`：已知，但当前尚未 ready；
- `ready`：无未解决 blocker；
- `in_progress`：有明确 owner 正在推进；
- `blocked`：存在具体 blocker；
- `completed`：验收和验证均完成；
- `cancelled`：明确退出范围，并记录原因。

同一时刻每个 owner 只保留一个 `in_progress` 项。Decision item 和 implementation item 必须明确区分。

## 完成条件

- Destination 的验收全部有证据；
- Fog 和 Not yet specified 已清空、转入后续计划或明确接受；
- 所有 decision 都有 durable artifact；
- 所有 implementation item 已验证或取消；
- active plan 被归档到 `docs/plans/completed/`。

## 方法来源

本 runbook 提炼自 `mattpocock/skills` v1.1.0 的 `wayfinder` 和 `to-tickets`，并把 issue-first 工作流改为 repo-first control plane。上游许可证：MIT。
