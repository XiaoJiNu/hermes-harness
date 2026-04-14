# ADR 0001: Hermes is the default runtime, not the only runtime

日期：2026-04-14
状态：accepted

## 背景

用户希望当前仓库优先说明如何用 Hermes 使用 harness 方法，但又明确要求：不要把方法完全限制在 Hermes 上；如果有更好的 runtime 或组合方法，也应该能采用。

## 决策

- 本仓库以 Hermes 作为默认 runtime 举例
- 本仓库的方法设计保持 runtime-agnostic
- 任何真正属于 harness 的内容，应优先沉淀为仓库工件，而不是沉淀为某个 CLI 的私有技巧

## 结果

这意味着：
- 选择方法时先问“项目类型是什么”，再问“用哪个 agent runtime 最合适”
- Hermes、Claude Code、Codex、OpenCode 等都可以作为执行层
- 如果切换 runtime，项目的 control plane、plan、runbook、registry、done 定义不应随之消失
