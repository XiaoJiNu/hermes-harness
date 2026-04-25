# Docs Index

## 先读

- `docs/hermes-harness-operating-model.md`
- `docs/catalog/project-types.md`
- `docs/hermes-harness-general-playbook.md`
- `docs/hermes-harness-algorithm-engineer-playbook.md`

## 目录

### 核心说明
- `docs/hermes使用harness.md`：中文入口说明
- `docs/hermes-harness-operating-model.md`：本仓库的正式操作模型
- `docs/hermes-harness-general-playbook.md`：通用新项目启动方法
- `docs/hermes-harness-algorithm-engineer-playbook.md`：算法工程 / 模型训练方法

### 项目类型目录与特定方法
- `docs/catalog/project-types.md`：选择哪个 harness 方法
- `docs/playbooks/software-product.md`：软件产品项目
- `docs/playbooks/data-pipeline.md`：数据管道 / ETL / 数据平台项目
- `docs/playbooks/benchmark-eval-repo.md`：benchmark / eval / leaderboard 项目
- `docs/playbooks/deployment-platform.md`：部署 / 平台 / 推理服务项目
- `docs/playbooks/multi-agent-product-ops.md`：多 agent 产品运营与协作项目

### 规格、计划、审计与决策
- `docs/specs/repo-charter.md`
- `docs/plans/active/2026-04-14-repo-bootstrap.md`
- `docs/plans/active/2026-04-24-hermes-codex-runtime-recovery.md`
- `docs/plans/active/2026-04-25-hermes-harness-method-sync.md`
- `docs/audits/2026-04-14-initial-state.md`
- `docs/audits/2026-04-15-hermes-codex-tun-instability.md`
- `docs/decisions/0001-hermes-default-runtime-not-exclusive.md`

### 运行手册与模板
- `docs/runbooks/add-project-type-playbook.md`
- `docs/runbooks/maintenance-review.md`
- `docs/runbooks/hermes-codex-runtime-recovery.md`：Hermes + Codex 统一恢复入口
- `docs/runbooks/hermes-codex-proxy-setup.md`：Hermes + Codex system proxy 配置与重启后失效修复
- `scripts/hermes_codex_runtime_recovery.py`：Hermes + Codex 诊断 / apply 脚本
- `docs/runbooks/hermes-method-update-sync.md`：Hermes / harness 方法更新同步流程
- `scripts/check_method_update_sources.py`：Hermes / harness 更新源只读检查脚本
- `docs/templates/project-type-playbook-template.md`

### 健康度
- `docs/tech-debt-tracker.md`
- `docs/QUALITY_SCORE.md`
