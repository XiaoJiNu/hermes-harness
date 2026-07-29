# Dependency-Aware Delivery Planning Runbook

## 适用场景

在 spec、验收标准和关键产品/架构决策已经明确，需要把工作拆成可执行、可验证的交付项时使用。

以下情况不要直接进入本 runbook：

- 目标或术语仍不清楚：先使用 `docs/runbooks/requirements-discovery-and-domain-modeling.md`；
- 目标明确但路线仍有大量未知：先使用 `docs/runbooks/long-horizon-decision-mapping.md`；
- 只是单个低风险、可立即验证的修改：直接建立一个 bounded batch 即可。

## Canonical inputs 与 owner

至少读取：

- canonical spec 和 acceptance criteria；
- 相关 ADR / decisions；
- 当前代码与测试入口；
- `docs/templates/active-plan-template.md` 创建的 active plan。

Active plan 是交付图的 canonical owner。外部 issue tracker 可以镜像状态和保存链接，但不能用根目录 `tickets.md`、固定 label 或 tracker-only issue 替代 spec、decision 和 active plan。

## 1. 把结果拆成垂直切片

每个 implementation item 优先形成一个 tracer-bullet 垂直切片：

- 有用户或调用方可观察的结果；
- 尽量贯穿必要的接口、实现和验证路径；
- 可独立运行 acceptance verification；
- 完成后不会只留下不可使用的半层组件。

不要按“先建所有模型、再建所有 API、最后补测试”机械横切。共享基础设施只有在被首个垂直切片真实需要时才建立。

## 2. 显式记录依赖边

`Blocked by` 只写真实依赖，不写偏好顺序。每条依赖边都应能回答：

1. 上游 item 必须产生什么 artifact、接口或决定？
2. 下游 item 为什么无法在它之前独立验证？
3. 是否能通过更窄的接口、fixture 或 tracer bullet 消除依赖？

如果依赖来自尚未解决的决策，创建 decision item，而不是把实现 item 长期标记为模糊的 blocked。

## 3. 状态与领取规则

| 状态 | 含义 | 可否交给执行 agent |
| --- | --- | --- |
| `pending` | 信息或依赖边尚未核实 | 否 |
| `needs-info` | 缺少必须由人提供的产品、权限或安全信息 | 否 |
| `blocked` | 存在已确认且未完成的依赖 | 否 |
| `ready` | scope、acceptance、verification 和依赖均明确 | 是 |
| `in-progress` | 已有明确 owner/claim | 不得重复领取 |
| `done` | acceptance 和 verification 已通过，工件已回写 | 不适用 |

进入 `ready` 前，必须把 claim、verified reality、scope、out of scope、acceptance、verification 和 side effects 写入 plan item；需要独立执行简报时使用 `docs/templates/agent-brief-template.md`。

## 4. 大范围重构例外

无法安全垂直切分的 wide refactor 使用三阶段：

1. `expand`：新增兼容接口、schema 或迁移通道，不破坏旧路径；
2. `migrate`：按可验证批次迁移调用方或数据；
3. `contract`：确认旧路径无调用后删除兼容层，并运行完整回归。

三阶段分别建 item，并为 contract 设置可机械检查的前置条件；不能把不可逆删除藏在 migrate 中。

## 5. Tracker 与副作用边界

把 plan item 投影到 GitHub/GitLab/Jira 等 tracker 前：

- 明确目标项目、仓库、里程碑和允许创建/修改的 issue 范围；
- 把外部 issue 写回 active plan，保持双向链接；
- 不自动创建 label、关闭 issue、改 assignee、发通知或执行其他外部副作用，除非任务授权已明确覆盖；
- tracker 状态与本地状态不一致时，以仓库 canonical artifacts 为准并人工协调。

## 6. Verification

计划发布给执行者前检查：

- 每个 item 都有 observable outcome、acceptance 和可重复命令/证据；
- 所有 dependency edge 都有理由，没有用依赖表达建议顺序；
- 没有把 decision uncertainty 伪装成 implementation task；
- 无 blocker 的 item 标记为 `ready`；
- wide refactor 明确分为 expand、migrate、contract；
- tracker issue 只引用 canonical spec/plan/decision；
- 所有外部副作用都在已授权范围内。

## 来源说明

本 runbook 提炼自 `mattpocock/skills` v1.1.0 的 `to-tickets` 方法，并按本仓库的 active-plan、decision、agent brief 和 source-of-truth 规则改写。上游许可证：MIT。
