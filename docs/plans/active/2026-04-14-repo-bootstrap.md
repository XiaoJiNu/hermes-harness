# Harness 方法参考仓库 Bootstrap Plan

> 目标：把当前仓库建立为“新项目启动时的 harness 方法参考库”，让 Hermes 作为默认运行时之一来使用 harness，但不把方法论绑定死在 Hermes 上。

日期：2026-04-14
状态：bootstrap-done / maintenance-active

## 背景

用户希望把本仓库作为长期维护的 harness 方法参考库，用于：

- 跟踪最新 harness engineering 方法
- 面向团队统一软件开发、模型训练、算法工程的工作方式
- 在开始新项目时，根据需求选择最合适的 harness 方法
- 当现有文档缺少某类项目时，补齐该项目类型的 playbook 并持续维护

## 本批次目标

1. 建立仓库根入口与控制面
2. 重写当前错误绑定到 Flux4D 的文档
3. 建立项目类型目录、选择规则、扩展流程与模板
4. 建立最小 mechanical enforcement（结构测试 + 检查脚本 + Makefile + CI）
5. 建立持续维护机制（runbook + 定期维护任务）

## 计划批次

### Batch 1

- 建立根入口：`README.md`、`AGENTS.md`、`ARCHITECTURE.md`、`CONTRIBUTING.md`
- 建立 docs 索引与核心控制面文档
- 重写 `docs/hermes-harness-operating-model.md`

### Batch 2

- 建立项目类型目录与 playbook 扩展机制
- 新增缺失的项目类型 playbook
- 新增模板与 runbook

### Batch 3

- 建立结构测试、检查脚本、Makefile、CI
- 运行验证并修复

### Batch 4

- 建立持续维护规则与自动化维护任务
- 更新计划状态与仓库总结

## 当前进度

- Batch 1：已完成
- Batch 2：已完成
- Batch 3：已完成
- Batch 4：已完成（已创建每 7 天运行一次的维护任务：`weekly-harness-reference-maintenance`）

## 当前结果

- 已建立根入口与 docs 控制面
- 已建立项目类型目录、模板与 runbook
- 已增加软件项目、数据管道、benchmark/eval、deployment/platform、multi-agent product ops playbook
- 已建立结构测试、检查脚本、Makefile 与 CI
- 已重写 repo-specific 操作模型，移除错误的 Flux4D 绑定

## 下一步

- 根据未来项目需求继续补充剩余项目类型 playbook
- 增强控制面检查强度
- 扩展更多 runtime-agnostic 说明

## 验证

- `python3 -m pytest tests/structure -q`
- `python3 scripts/check_control_plane.py`
- `make test-structure`

## Done 定义

- 仓库具备可读入口、项目类型选择方法、扩展机制、最小验证闭环和维护流程
- 当前顶层文档不再错误绑定到 Flux4D
- 新项目启动时可以直接把本仓库当作方法参考
