# AGENTS.md

本仓库是 harness 方法参考仓库，不是某个具体产品代码仓库。

## 先读什么

开始任何非平凡工作前，按顺序阅读：
1. `README.md`
2. `docs/README.md`
3. `docs/catalog/project-types.md`
4. `docs/hermes-harness-operating-model.md`
5. 与任务最相关的 playbook / runbook / spec / plan

## 仓库地图

- `docs/hermes-harness-operating-model.md`：本仓库里 Hermes 如何工作
- `docs/hermes-harness-general-playbook.md`：通用新项目启动方法
- `docs/hermes-harness-algorithm-engineer-playbook.md`：算法工程 / 模型训练方法
- `docs/playbooks/`：特定项目类型方法
- `docs/catalog/project-types.md`：如何选择哪个 harness 方法
- `docs/runbooks/`：如何新增、维护和扩展方法
- `docs/runbooks/hermes-method-update-sync.md`：如何检查并同步 Hermes / harness 方法更新
- `docs/runbooks/agent-skills-method-intake.md`：如何 intake agent-skills 这类外部方法来源
- `docs/references/agent-skills-crosswalk.md`：外部 skill 方法到本仓库 surface 的映射
- `docs/plans/active/`：当前正在推进的计划

## 核心规则

- 仓库是 source of truth
- AGENTS.md 是地图，不是百科全书
- Hermes 是默认 runtime，但不要把方法绑定死在 Hermes 上
- 如果现有文档不能覆盖某个新项目类型，就新增该项目类型的 playbook
- 非平凡变更必须同时更新受影响的 docs surface
- 宣称完成前必须运行验证

## 验证入口

- `python3 scripts/check_control_plane.py`
- `python3 -m pytest tests/structure -q`
- `make test-structure`
