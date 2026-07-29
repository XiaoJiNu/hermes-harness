# Hermes Harness Reference Repository

本仓库是一个“harness 方法参考仓库”，目标不是承载某一个业务项目，而是承载：
- 如何为新项目建立 harness
- 如何让 Hermes 在 harness 内高质量工作
- 如何在需要时切换到 Claude Code、Codex、OpenCode 或其他 agent runtime
- 如何把软件开发、模型训练、算法工程、数据工程等项目纳入统一的控制面
- 如何持续跟踪 harness engineering 的方法更新，并把它们沉淀为可复用 playbook

一句话：

把这里当作“新项目启动前先看的方法仓库”，而不是只看一次的说明文档。

## 这个仓库解决什么问题

当你以后开始一个新项目时，你不需要从零想“该怎么用 AI 写代码”。
你只需要给出需求，然后先用本仓库完成下面几件事：

1. 判定项目类型
2. 选择最合适的 harness 方法
3. 建立该项目的控制面
4. 再让 Hermes 或其他 agent 在控制面里执行实现、训练、评测、维护

## 设计原则

- 仓库是 source of truth
- Hermes 是默认 runtime，但不是唯一 runtime
- 方法优先于工具，工具服务于方法
- 大任务先有计划，再有执行
- 每个方法都应尽量升级为可验证的仓库工件
- 缺失的项目类型不靠聊天记忆补，而是补成新 playbook
- 持续维护依赖仓库内工件和定期 review，而不是一次性说明

## 新项目启动时的推荐读法

最小必读顺序：

1. `AGENTS.md`
2. `docs/README.md`
3. `docs/catalog/project-types.md`
4. `docs/hermes-harness-operating-model.md`
5. 对应项目类型的 playbook

如果现有 playbook 无法覆盖你的项目：
- 按 `docs/runbooks/add-project-type-playbook.md` 新增该类型方法
- 同步更新 `docs/catalog/project-types.md` 和 `docs/README.md`
- 把新方法纳入结构校验与后续维护

## 核心文档

- `docs/hermes-harness-operating-model.md`：本仓库的正式操作模型
- `docs/hermes-harness-general-playbook.md`：所有新项目的通用启动方法
- `docs/hermes-harness-algorithm-engineer-playbook.md`：算法工程 / 训练 / 复现方法
- `docs/playbooks/ai-paper-reproduction.md`：无官方代码或弱开源条件下的 AI 论文系统复现方法
- `docs/references/ai-paper-reproduction-sources.md`：论文复现可用的开源仓库、平台和方法来源
- `docs/templates/ai-paper-reproduction-project-template.md`：具体论文复现项目的控制面模板
- `docs/catalog/project-types.md`：项目类型选择目录
- `docs/playbooks/software-product.md`：软件产品项目方法
- `docs/playbooks/data-pipeline.md`：数据管道 / ETL / 数据平台项目方法
- `docs/playbooks/benchmark-eval-repo.md`：benchmark / eval / leaderboard 项目方法
- `docs/playbooks/deployment-platform.md`：部署 / 平台 / 推理服务项目方法
- `docs/playbooks/multi-agent-product-ops.md`：多 agent 协作与产品运营项目方法
- `docs/runbooks/hermes-codex-runtime-recovery.md`：Hermes + Codex 故障恢复入口
- `docs/runbooks/vscode-remote-ssh-ubuntu.md`：Ubuntu 双机 VSCode Remote-SSH 远程开发方案
- `docs/runbooks/understand-anything-hermes-bootstrap.md`：在新电脑 / Hermes profile 上可复现安装 Understand-Anything code-reading 方法
- `scripts/bootstrap_understand_anything.py`：Understand-Anything Hermes skills bootstrap 脚本
- `scripts/hermes_codex_runtime_recovery.py`：Hermes + Codex 诊断 / apply 脚本
- `docs/runbooks/hermes-method-update-sync.md`：如何检查并同步 Hermes / harness 方法更新
- `docs/runbooks/agent-skills-method-intake.md`：如何把 agent-skills 这类外部 workflow pack 转成 harness 方法
- `docs/references/agent-skills-crosswalk.md`：agent-skills 方法到本仓库 surface 的映射
- `docs/references/mattpocock-skills-crosswalk.md`：mattpocock/skills promoted 方法的采用、合并与拒绝映射
- `docs/runbooks/requirements-discovery-and-domain-modeling.md`：需求澄清、spec synthesis、shared language 与 ADR 入口
- `docs/runbooks/dependency-aware-delivery-planning.md`：把 spec 拆成 tracer-bullet、显式依赖和 agent-ready 工作项
- `docs/runbooks/long-horizon-decision-mapping.md`：长周期任务的 decision-first 路线显影方法
- `docs/runbooks/diff-review.md`：Standards / Spec 两轴独立评审方法
- `docs/runbooks/harness-skill-authoring.md`：把稳定方法包装成仓库内 Hermes skill 的标准流程
- `docs/templates/active-plan-template.md`：dependency-aware tracer-bullet active plan 模板
- `docs/templates/handoff-template.md`：跨会话/agent 的 durable handoff 模板
- `docs/templates/agent-brief-template.md`：经过 claim 验证的 agent-ready 工作简报模板
- `scripts/check_method_update_sources.py`：Hermes / harness / external skill pack 更新源只读检查脚本
- `docs/runbooks/add-project-type-playbook.md`：新增项目类型方法的标准流程
- `docs/runbooks/maintenance-review.md`：持续维护与更新流程

## 最小机械化约束

当前仓库提供：
- `tests/structure/`：结构测试
- `scripts/check_control_plane.py`：控制面检查脚本
- `Makefile`：标准验证入口
- `.github/workflows/ci.yml`：CI 入口

常用命令：

- `python3 scripts/check_control_plane.py`
- `python3 -m pytest tests/structure -q`
- `make test-structure`

## 维护承诺

本仓库的长期维护目标是：
- 定期复核 harness 方法是否过时
- 持续补充新的项目类型 playbook
- 持续明确“方法”和“某个 agent 工具”的边界
- 让团队在未来任何新项目中，都能把这里当作方法起点
