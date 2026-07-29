# Multi-Agent Product Ops Harness Playbook

## 适用范围

适用于：
- 多 agent 协作产品开发
- 长任务编排、planner / executor / reviewer 分工
- 持续运营型 agent workflow 仓库
- 需要稳定 handoff、backpressure、review loop 的项目

## 核心目标

让多个 agent 围绕仓库工件协作，而不是围绕隐藏聊天上下文协作。

## 最小控制面

至少应有：
- role map（planner / implementer / reviewer / maintainer）
- task intake 规则
- handoff artifact 规范
- review / verification loop
- failure / escalation policy
- run / job registry
- context refresh rule
- garbage collection / entropy management 规则

## 标准启动流程

1. 先定义角色与责任边界
2. 先定义 handoff artifact
3. 先定义什么必须回写仓库
4. 先定义 review 和 backpressure 规则
5. 再放大 agent autonomy

## Intake 与 routing

本节是 issue triage 到 agent-ready brief 的 canonical procedure owner。

进入 agent 执行前先验证 claim，而不是把未经确认的 issue 描述直接交给 worker：

1. 复现问题或收集可重复证据；
2. 补齐相关代码、spec、decision 和最近变更；
3. 写清 scope、out of scope、acceptance 和验证命令；
4. 使用 `docs/templates/agent-brief-template.md` 标记为 `agent-ready`、`needs-info` 或 `human-required`；
5. 只有不再依赖产品/权限/安全决策的工作才进入 agent queue。

状态映射：

| Triage 状态 | 仓库工件动作 | 是否可路由 |
| --- | --- | --- |
| `needs-info` | 在 brief 中写明缺失的人类决策/权限/证据 | 否 |
| `human-required` | 记录必须由人执行的产品、安全或外部系统动作 | 否 |
| `agent-ready` | scope、acceptance、verification、依赖和副作用范围完整 | 是 |
| `in-progress` | 记录唯一 owner/claim，防止重复执行 | 否 |
| `done` | 验证通过并回写 plan/issue 链接 | 不适用 |

创建/关闭外部 issue、修改 assignee/label/milestone、发送通知或写入第三方系统都属于副作用；只有任务授权明确覆盖目标系统与操作范围时才能执行，否则停在 brief/plan 阶段请求确认。

issue tracker 可以保存状态和引用。仓库内 spec、plan 和 decision 是 canonical artifacts；brief 与 handoff 是从这些事实投影出的执行工件，只能链接 canonical 内容，不能成为平行事实源。

默认把活动期工件和所属 plan 放在一起：

- brief：`docs/plans/active/<plan-id>-brief-<work-id>.md`；
- handoff：`docs/plans/active/<plan-id>-handoff-<YYYY-MM-DD>.md`。

计划完成时，把仍有长期价值的证据和决定归并进 completed plan；删除已被取代的 brief/handoff。只有具备独立审计价值的工件才随计划移动到 `docs/plans/completed/`，并保留同一 `<plan-id>` 前缀。

## 长周期任务地图

当目标会跨多个会话且路线未知时，使用 `docs/runbooks/long-horizon-decision-mapping.md`：

- active plan 写清 Destination、Known reality、Decisions so far、Frontier、Fog 和 Out of scope；
- decision item 与 implementation item 分开；
- 默认一个会话只推进一个 frontier decision，独立 research 可以并行；
- 每个决定都必须产出 spec/ADR/plan 更新，再展开实现任务；
- `Blocked by` 只表示真实依赖。

## Hermes 的默认工作方式

- Hermes 可以作为 orchestrator 或某一个角色 agent
- 大任务应拆成边界清晰的批次或子任务
- 子任务完成后必须回写 plan、summary、registry 或 review surface
- 不允许把关键状态只留在会话里

## skill / persona / command 分层

吸收 `agent-skills` 的分层，但保持 runtime-agnostic：

| 层 | 作用 | 本仓库约束 |
|---|---|---|
| skill | 定义 how：流程、步骤、验证、red flags | 写入 playbook / runbook / template，不依赖某个 runtime |
| persona | 定义 who：reviewer、security-auditor、test-engineer 等单一视角 | persona 只产出自己的报告，不调用其他 persona |
| command | 定义 when：用户或 runbook 触发某个组合流程 | 不复制 Claude slash command；改写成 runbook entrypoint |

组合规则：

1. 用户、Hermes 主会话或 runbook 是 orchestrator
2. persona 不做 router，也不调用另一个 persona
3. 只有子任务相互独立、无共享可变状态时，才做 parallel fan-out
4. fan-out 后由主会话 merge 报告，产出统一结论和 verification story
5. `router persona`、深层 persona tree、纯转述型 sequential orchestrator 都是反模式

### 推荐 fan-out review 模式

发布或合并前，先固定 review base，并始终保留两个独立基础轴：

- standards-reviewer：检查 repo instructions、正确性、安全、可维护性和验证纪律；
- spec-reviewer：逐条核对目标、范围、非目标和 acceptance evidence。

如果变更有非平凡风险，再并发增加独立风险视角：

- code-reviewer：correctness / readability / architecture / performance
- security-auditor：secrets / auth / input validation / dependency risk
- test-engineer：coverage gaps / regression risk / missing edge cases

主会话负责合并：

- 去重 blocker
- 标注哪些是必须修复，哪些是建议
- 记录运行了哪些测试
- 给出 go/no-go 和 rollback plan

不同轴不得压成一个模糊分数。修复后重跑受影响的轴，直到没有 actionable blocker/major，或剩余 debt 已被显式接受。完整流程见 `docs/runbooks/diff-review.md`。

### Handoff artifact

本节是 session handoff 的 canonical procedure owner。

handoff 使用 `docs/templates/handoff-template.md`，至少包含：

- objective 和 canonical artifact 链接；
- completed/current/remaining 状态；
- decisions、blockers 和已运行验证；
- exact next action；
- 敏感信息脱敏。

handoff 只引用 spec、plan 和 ADR，不复制全文；否则不同副本会迅速漂移。

仓库内 handoff 是 durable checkpoint。需要把上下文交给临时 runtime/session 时，可以生成 OS 临时目录中的可丢弃 resumption envelope，但它只能引用仓库工件，不能承载唯一决定或状态；恢复后应删除，不进入版本控制。

### 子代理编排约束

当 Hermes 使用 subagent / delegation 时，必须先写清：

| 维度 | 要求 |
|---|---|
| role | orchestrator / worker / reviewer / researcher 等角色不能混淆 |
| context | 子任务 prompt 必须自足，不能假设子代理知道当前聊天 |
| toolsets | 只开启任务需要的工具集，避免无关工具扩大上下文和风险 |
| concurrency | 并发数服务于边界清晰的独立任务，不用并发掩盖需求不清 |
| spawn depth | 默认保持扁平；只有明确需要二级编排时才允许 worker 再分派 |
| file coordination | 多个子代理可能写同一仓库时，要指定文件边界或先产出建议再由主代理合并 |
| verification | 每个子任务都要说明验证入口或审查标准 |
| handoff | 长任务必须产出仓库内 handoff artifact，而不是只返回聊天摘要 |

如果中途用 `/steer` 或其他方式纠偏，且纠偏改变需求或验收标准，必须同步更新 active plan / spec / runbook。

## 可替换 runtime

本方法天然 runtime-agnostic：
- Hermes
- Claude Code
- Codex
- 其他有任务分派与仓库读写能力的 agent runtime

需要保持不变的是：
- 角色分工
- handoff artifact
- review / verification gates
- escalation 规则

## 常见反模式

- 每个 agent 都拿到整个任务，没有角色拆分
- handoff 只靠聊天摘要，不回写仓库
- review 没有明确 gate，只凭主观“看起来可以”
- 任务并行很多，但没有统一 registry 或 checkpoint
- 未验证 claim 就标为 agent-ready
- 把尚未解决的产品决策伪装成实现任务
- reviewer 没有固定 base，或 Standards/Spec 两条轴互相代替
