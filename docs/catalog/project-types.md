# Project Types Catalog

本文件回答两个问题：
- 遇到一个新项目时，应该选择哪个 harness 方法？
- 如果现有方法不够，应该如何扩展？

## 选择哪个 harness 方法

### 1. 所有新项目都先读
- `docs/hermes-harness-general-playbook.md`

### 2. 如果项目以产品功能、API、前后端、CLI 为主
选择：
- `docs/playbooks/software-product.md`

### 3. 如果项目以模型调研、论文复现、训练、评测、自有数据适配为主
选择：
- `docs/hermes-harness-algorithm-engineer-playbook.md`

如果重点是“给定 paper 和数据，系统复现论文”，尤其是无官方代码、官方代码不可运行或需要比较多个社区实现，进一步选择：
- `docs/playbooks/ai-paper-reproduction.md`

### 4. 如果项目以数据管道、ETL、索引、批处理、数据质量治理为主
选择：
- `docs/playbooks/data-pipeline.md`

### 5. 如果项目以 benchmark、leaderboard、评测框架、回归检测为主
选择：
- `docs/playbooks/benchmark-eval-repo.md`

### 6. 如果项目以部署、平台、推理服务、发布与回滚治理为主
选择：
- `docs/playbooks/deployment-platform.md`

### 7. 如果项目需要多个 agent 长时间协作、交接、审查与任务编排
选择：
- `docs/playbooks/multi-agent-product-ops.md`

### 8. 如果项目本身是文档、知识库、方法库或规范仓库
优先参考：
- `docs/hermes-harness-operating-model.md`
- `docs/hermes-harness-general-playbook.md`

## 选择矩阵

| 项目特征 | 首选方法 | 必备控制面 |
|---|---|---|
| 软件功能闭环、接口、交互、服务 | `docs/playbooks/software-product.md` | spec, architecture, runbook, tests, CI |
| 模型训练、复现、评测、比较 | `docs/hermes-harness-algorithm-engineer-playbook.md` | dataset contract, runbook, manifest, registry, comparison |
| 无官方代码或弱开源条件下复现 AI paper | `docs/playbooks/ai-paper-reproduction.md` | paper claim matrix, source survey, paper-vs-code audit, run registry, gap log, `docs/templates/ai-paper-reproduction-project-template.md` |
| 数据抓取、清洗、调度、ETL | `docs/playbooks/data-pipeline.md` | input contract, pipeline stages, quality gates, schedule/run registry |
| benchmark、leaderboard、评测回归 | `docs/playbooks/benchmark-eval-repo.md` | benchmark spec, metric catalog, eval registry, comparison, regression gate |
| 部署、平台、推理服务、发布治理 | `docs/playbooks/deployment-platform.md` | env contract, deploy/rollback runbooks, SLO, release gate, observability |
| 多 agent 编排、协作、长期运营 | `docs/playbooks/multi-agent-product-ops.md` | role map, handoff artifacts, review loop, escalation policy, job registry |
| 方法仓库、知识库、文档治理 | `docs/hermes-harness-operating-model.md` | docs index, catalog, runbook, maintenance loop |

## 当现有方法不覆盖项目时

如果你发现当前文档无法明确回答“选择哪个 harness 方法”，不要把缺口留在聊天里。
请执行：

1. 根据 `docs/runbooks/add-project-type-playbook.md` 新增该项目类型的 playbook
2. 从 `docs/templates/project-type-playbook-template.md` 复制结构
3. 同步更新 `docs/README.md`
4. 同步更新本文件中的选择规则
5. 把新增该项目类型的 playbook 纳入后续维护与检查

这就是“新增该项目类型的 playbook”的标准要求。
