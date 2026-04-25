# agent-skills Method Intake Completion Record

日期：2026-04-25
状态：completed

## 背景

用户要求将 `git@github.com:addyosmani/agent-skills.git` 的方法集成到 `hermes-harness` 仓库中，并提交代码。

本记录说明该批次完成了什么、记录落在哪些 source-of-truth 文档中，以及后续如何复查。

## 外部来源检查

已检查外部仓库：

```bash
git clone git@github.com:addyosmani/agent-skills.git /tmp/agent-skills
python3 scripts/check_method_update_sources.py \
  --agent-skills-root /tmp/agent-skills \
  --json
```

当次检查结论：

- 外部来源：`git@github.com:addyosmani/agent-skills.git`
- 本地检查路径：`/tmp/agent-skills`
- license：MIT
- skill 数量：21
- command 数量：7
- persona 数量：3
- hook 文件数量：8
- reference 数量：5
- invalid skill metadata：0

## 已落地的仓库工件

主要完成记录不只放在本 plan 中，而是分散落到正式 source-of-truth surfaces：

1. `docs/decisions/0002-agent-skills-external-method-source.md`
   - 记录采用决策：`agent-skills` 是 external method source，不是 source of truth
   - 明确不直接采用 Claude plugin、slash command、session hook 或外部 AGENTS/CLAUDE 入口

2. `docs/references/agent-skills-crosswalk.md`
   - 记录从 agent-skills skill / persona / command / hook / reference 到本仓库 surface 的映射
   - 明确 `SPEC.md`、`tasks/plan.md`、`.claude/commands/*.md` 等路径如何适配到 `docs/specs/`、`docs/plans/`、`docs/runbooks/`、`docs/playbooks/`

3. `docs/runbooks/agent-skills-method-intake.md`
   - 记录未来重复 intake 外部 workflow pack 的流程
   - 包含 clone、source check、license、runtime packaging、verification 规则

4. `docs/hermes-harness-operating-model.md`
   - 增加外部 workflow pack 采用规则
   - 强调本仓库仍是 source of truth

5. `docs/hermes-harness-general-playbook.md`
   - 增加 task-level workflow selection

6. `docs/playbooks/multi-agent-product-ops.md`
   - 增加 skill / persona / command 分层
   - 增加 parallel fan-out + merge，避免 router persona

7. `scripts/check_method_update_sources.py`
   - 增加 `--agent-skills-root` 只读检查能力

8. `tests/test_check_method_update_sources.py` 与 `tests/structure/test_harness_repo.py`
   - 增加 agent-skills intake 的脚本与结构保护

## 提交记录

集成提交：

```text
3ba22f9 feat: add external method source intake
```

该提交包含 ADR、crosswalk、runbook、operating model、general playbook、multi-agent playbook、检查脚本和测试更新。

## 验证

完成时运行并通过：

```bash
python3 scripts/check_control_plane.py
python3 -m pytest tests/structure -q
python3 -m pytest tests/test_check_method_update_sources.py -q
make test-structure
python3 scripts/check_method_update_sources.py --agent-skills-root /tmp/agent-skills --json
```

## Done 定义

- 外部来源状态、license 和结构已检查
- 采用边界已通过 ADR 记录
- crosswalk 已记录外部方法到本仓库 surface 的映射
- intake runbook 已记录未来重复流程
- runtime-specific packaging 未直接成为 source of truth
- 结构测试和 source checker 已覆盖关键工件
- 代码已提交
