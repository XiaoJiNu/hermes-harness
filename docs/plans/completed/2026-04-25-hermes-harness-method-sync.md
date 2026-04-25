# Hermes / Harness Method Update Sync Plan

日期：2026-04-25
状态：done

## 背景

用户要求分析本仓库，确认 Hermes 和 harness 是否有更新，并把最新且有价值的方法同步到仓库中，让 Hermes 使用 harness 的方式更好用。

## 本批次目标

1. 检查本仓库与 Hermes runtime/source 的真实更新状态
2. 抽取 Hermes v0.9.0 之后对 harness 方法有长期价值的变化
3. 新增一个可重复执行的 method update sync runbook
4. 新增只读检查脚本，让未来 agent 不必从零判断更新状态
5. 更新操作模型、通用方法、多 agent 方法、维护流程、quality/debt 与结构检查
6. 运行验证

## 发现

- `hermes-harness`：`HEAD...origin/main = 0/0`，远端 main 无新增需要合并
- 本机 Hermes CLI：`Hermes Agent v0.9.0 (2026.4.13)`，提示有 update available
- 本地 `hermes-agent` source：`HEAD...origin/main = 0/1778`，远端已有 v2026.4.23 / v0.11.0
- `hermes-agent` 本地有未提交 runtime 修复，因此不适合直接自动升级

## 已同步的方法增量

- Hermes runtime update 不再靠记忆判断，新增 `docs/runbooks/hermes-method-update-sync.md`
- 新增 `scripts/check_method_update_sources.py` 作为只读入口
- 将最新 Hermes 能力转成 harness 方法规则：
  - subagent orchestrator / worker / reviewer 角色化
  - 并发、spawn depth、toolsets、成本显式约束
  - `/steer` 类 mid-run nudge 必须回写仓库工件
  - focused compression 前先写仓库摘要，避免只依赖会话压缩
  - provider / timeout / fallback 属于 runtime 决策，但项目要记录约束
  - cron / webhook / background 默认最小 toolsets 和 watch_patterns
  - plugins / shell hooks 只在规则稳定且可验证后固化

## Companion surfaces

已更新：
- `README.md`
- `docs/README.md`
- `docs/hermes-harness-operating-model.md`
- `docs/hermes-harness-general-playbook.md`
- `docs/playbooks/multi-agent-product-ops.md`
- `docs/runbooks/maintenance-review.md`
- `docs/tech-debt-tracker.md`
- `docs/QUALITY_SCORE.md`
- `scripts/check_control_plane.py`
- `tests/structure/test_harness_repo.py`

## 验证

- `python3 scripts/check_control_plane.py`
- `python3 -m pytest tests/structure -q`
- `python3 -m pytest tests/test_hermes_codex_runtime_recovery.py -q`
- `python3 -m pytest tests/test_check_method_update_sources.py -q`
- `make test-structure`

## Done 定义

- 更新状态已检查并记录
- 方法增量已落地为仓库工件
- 新 runbook 和脚本已进入结构检查
- 相关 companion surfaces 已同步
- 验证通过
