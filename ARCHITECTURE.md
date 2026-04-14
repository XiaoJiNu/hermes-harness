# Architecture

## 目标

本仓库的架构目标不是组织业务代码，而是组织“可持续维护的 harness 方法”。

## 三层结构

### 1. Entry Layer

面向人和 agent 的最小入口：
- `README.md`
- `AGENTS.md`
- `docs/README.md`

这层负责导航，不负责承载全部细节。

### 2. Control Plane Layer

本仓库真正的 source of truth 位于 `docs/`：
- `docs/specs/`：仓库目标、范围、方法边界
- `docs/catalog/`：项目类型目录与选择规则
- `docs/playbooks/`：特定项目类型的方法
- `docs/runbooks/`：维护与扩展流程
- `docs/decisions/`：稳定决策
- `docs/audits/`：阶段性审计
- `docs/plans/`：执行计划
- `docs/QUALITY_SCORE.md` / `docs/tech-debt-tracker.md`：质量与债务

### 3. Mechanical Enforcement Layer

把“方法仓库不能漂移”的要求转成机器检查：
- `tests/structure/`
- `scripts/check_control_plane.py`
- `Makefile`
- `.github/workflows/ci.yml`

## 方法与 runtime 的关系

- harness = 仓库级方法、约束、流程、验证
- runtime = Hermes、Claude Code、Codex、OpenCode 等执行层
- 本仓库优先沉淀 harness，不把单个 runtime 当成方法本身

## 扩展原则

当出现新的项目类型时：
1. 先补 `docs/catalog/project-types.md` 的分类判断
2. 再补对应 playbook
3. 再补验证与维护路径
4. 不要只在聊天里说“下次这样做”
