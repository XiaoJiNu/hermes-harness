# Runbook: Maintenance Review

本 runbook 定义如何持续维护本仓库，而不是把它做成一次性文档集。

## 维护频率

建议每周或每两周执行一次 review。

## Review 目标

- 检查现有 playbook 是否过时
- 检查是否出现新的项目类型需求
- 检查方法是否过度绑定某个 runtime
- 检查入口、目录、模板和 runbook 是否一致
- 检查质量分和技术债是否需要更新

## 每次 review 的步骤

1. 读取：
   - `README.md`
   - `docs/README.md`
   - `docs/catalog/project-types.md`
   - `docs/tech-debt-tracker.md`
   - `docs/QUALITY_SCORE.md`

2. 复核方法源
   - 用户本地参考资料
   - 已归档的 harness 相关文章与 notes
   - 最近值得采纳的 agent / harness 实践
   - 最新或热门的外部 SOTA 方法来源；方法论升级批次必须先整理候选更新并让用户审核
   - Hermes runtime / source repo 更新状态：`python3 scripts/check_method_update_sources.py --json`
   - 需要最新远端状态时按 `docs/runbooks/hermes-method-update-sync.md` 执行 `--fetch`

3. 识别变化
   - 有没有新的项目类型需要覆盖
   - 有没有已有 playbook 需要增加新的控制面
   - 有没有能从 prose 升级为 check 的规则

4. 更新仓库
   - 改 playbook / catalog / runbook / decision / audit
   - 必要时新增该项目类型的 playbook
   - 更新质量分与技术债

5. 运行验证
   - `python3 scripts/check_control_plane.py`
   - `python3 -m pytest tests/structure -q`
   - `make test-structure`

## 维护原则

- 方法优先，工具其次
- 先补仓库工件，再依赖会话记忆
- Hermes 是默认执行者，但持续保持 runtime-agnostic
