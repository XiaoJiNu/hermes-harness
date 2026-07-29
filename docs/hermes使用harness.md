# Hermes 使用 Harness 说明

本文件保留为中文入口说明。

正式文档请阅读：
- `docs/hermes-harness-operating-model.md`：本仓库的正式操作模型
- `docs/hermes-harness-general-playbook.md`：所有新项目的通用启动方法
- `docs/hermes-harness-algorithm-engineer-playbook.md`：算法工程 / 模型训练方法
- `docs/playbooks/ai-paper-reproduction.md`：AI 论文系统复现方法
- `docs/templates/ai-paper-reproduction-project-template.md`：具体论文复现项目控制面模板
- `docs/catalog/project-types.md`：如何为新项目选择最佳 harness 方法
- `docs/playbooks/software-product.md`
- `docs/playbooks/data-pipeline.md`
- `docs/playbooks/benchmark-eval-repo.md`
- `docs/playbooks/deployment-platform.md`
- `docs/playbooks/multi-agent-product-ops.md`
- `docs/runbooks/hermes-method-update-sync.md`：检查 Hermes / harness 方法更新并同步有价值增量
- `docs/runbooks/requirements-discovery-and-domain-modeling.md`：需求澄清、领域术语和 spec synthesis
- `docs/runbooks/long-horizon-decision-mapping.md`：长周期任务的 destination / frontier / fog 管理
- `docs/runbooks/diff-review.md`：固定 review base 的 Standards / Spec 两轴评审
- `docs/templates/active-plan-template.md`：dependency-aware active plan 起点

使用原则：
- 先按项目类型选择方法
- 先建立控制面，再让 agent 做大块执行
- 如果当前仓库缺少该项目类型，就新增该项目类型的 playbook 并持续维护
- Hermes 是默认运行时之一，但方法不应被限制在 Hermes
