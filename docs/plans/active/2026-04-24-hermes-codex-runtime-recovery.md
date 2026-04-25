# Hermes + Codex Runtime Recovery Plan

> 目标：把“这台电脑上 Hermes 使用 Codex 又出现 bug”的一次性排障，升级为本仓库内可检索、可执行、可验证的 harness 工件。

日期：2026-04-24
状态：done

## 背景

仓库内已经有：
- `docs/audits/2026-04-15-hermes-codex-tun-instability.md`
- `docs/runbooks/hermes-codex-proxy-setup.md`

但它们仍偏向“分析结论”和“单点代理修复”。

缺口在于：
1. 没有一个统一的恢复入口
2. 没有一个能让 agent 直接执行的诊断 / apply 脚本
3. 没有把该方法纳入 control-plane 检查

## 本批次目标

1. 新增一个面向未来重复故障的正式 recovery runbook
2. 新增一个可执行脚本，支持 check / apply
3. 让 docs index 能稳定找到该方法
4. 让 control-plane 检查覆盖该方法，避免后续被移除或遗忘

## 计划批次

### Batch 1
- 复核已有 audit 和 proxy runbook
- 抽取真正可复用的恢复步骤

### Batch 2
- 新增 recovery runbook
- 新增 `scripts/hermes_codex_runtime_recovery.py`

### Batch 3
- 更新 `README.md`、`docs/README.md`
- 更新 `docs/tech-debt-tracker.md`、`docs/QUALITY_SCORE.md`
- 更新结构测试与 control-plane 检查

### Batch 4
- 运行验证
- 确认脚本能作为未来 agent 的默认恢复入口

## 当前结果

- 已新增统一恢复入口：`docs/runbooks/hermes-codex-runtime-recovery.md`
- 已新增自动化脚本：`scripts/hermes_codex_runtime_recovery.py`
- 已把新方法接入 docs index 和 control-plane 检查
- 已把“只修代理不够”的经验正式升级为仓库工件

## 验证

- `python3 scripts/check_control_plane.py`
- `python3 -m pytest tests/structure -q`
- `python3 -m pytest tests/test_hermes_codex_runtime_recovery.py -q`

## Done 定义

- 新 runbook 和脚本都已落地
- docs index 可以直接找到该方法
- control-plane 检查能防止该方法丢失
- 方法既能被人读，也能被 agent 直接执行
