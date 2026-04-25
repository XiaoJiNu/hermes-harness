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

## Hermes 的默认工作方式

- Hermes 可以作为 orchestrator 或某一个角色 agent
- 大任务应拆成边界清晰的批次或子任务
- 子任务完成后必须回写 plan、summary、registry 或 review surface
- 不允许把关键状态只留在会话里

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
