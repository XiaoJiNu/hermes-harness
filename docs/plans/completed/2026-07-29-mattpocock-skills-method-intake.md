# mattpocock/skills 方法吸收完成记录

日期：2026-07-29
状态：completed

## 目标

把 `https://github.com/mattpocock/skills` 作为第二个 external method source 纳入 `hermes-harness`，选择性吸收长期有效的方法，同时保持本仓库为 source of truth、保持 runtime-agnostic，并补齐可重复的来源检查。

## 来源基线

- Release：`v1.1.0`
- Commit：`d574778f94cf620fcc8ce741584093bc650a61d3`
- License：MIT
- 实际检查：38 个 `SKILL.md`、21 个 manifest-promoted skill
- Bucket：engineering 17、productivity 5、in-progress 6、misc 4、personal 2、deprecated 4
- 验证结果：无无效 frontmatter、无缺失 promoted skill、无缺失 promoted docs、无 manifest error

## 已交付

### Source governance

- 新增 `docs/references/mattpocock-skills-crosswalk.md`，覆盖 v1.1.0 全部 21 个 promoted skill。
- 把 `docs/runbooks/agent-skills-method-intake.md` 泛化为 external skill pack intake，同时保留 addyosmani 兼容入口。
- 明确 tag/commit pin、许可证、promoted manifest、调用语义和 runtime packaging 边界。

### Method surfaces

- 新增需求澄清与领域建模 runbook。
- 新增 dependency-aware delivery planning runbook，作为 `to-tickets` 方法的 canonical owner。
- 新增长周期决策映射 runbook。
- 新增固定 review base 的 Standards / Spec 两轴 diff review runbook。
- 新增 Hermes skill authoring runbook。
- 新增 active plan、domain glossary、handoff、agent brief 模板。
- 把 tracer bullet、expand–migrate–contract、prototype、triage、handoff 和 fixed-point review 增量写入通用、软件产品与 multi-agent playbook。
- 明确 prototype、triage 和 handoff 的 canonical procedure owner、状态/副作用边界及生命周期。

### Mechanical enforcement

- `scripts/check_method_update_sources.py` 已兼容 flat 与 nested skill pack。
- 新增 source adapter、bucket、promoted manifest、docs coverage、OpenAI metadata all-or-none coverage、Claude/Codex invocation policy、package/plugin version status、duplicate/path/symlink safety 和 1 MiB 读取上限检查。
- 外部 skill/command/persona/hook/reference 目录不可读或为 symlink 时返回诊断，不因 `PermissionError` 崩溃。
- Git 状态比较改为解析 `@{upstream}`；detached HEAD 优先使用精确 pinned tag、再回退 `origin/HEAD`，支持真实 tag clone、`origin/master` 和自定义 remote，不再硬编码 `origin/main`。
- 保留 `--agent-skills-root` 和 JSON `agent_skills` key，新增 `--workflow-pack-root` / `--workflow-pack-id`。
- 增加回归测试，包括嵌套布局、版本状态、调用漂移与注释解析、metadata partial coverage、flat 布局兼容、duplicate 和 unsafe/symlink manifest path。
- 更新 control-plane 和 structure tests，保护新增正式 surface。

## 关键决策

1. 不 vendor 上游仓库，不安装其 Claude plugin、slash command、hook 或 OpenAI metadata。
2. 第一轮不新增 runtime skill；先把稳定方法吸收进 playbook/runbook/template。
3. 以 `.claude-plugin/plugin.json` 定义的 21 个 promoted skill 作为 v1.1.0 正式清单；非 promoted 内容默认 defer。
4. 后续 `main` 的 skill 组合变化不能混入 v1.1.0 结论，必须单独 pin、检查和更新 crosswalk。
5. issue tracker 可以作为执行镜像，但 active plan/spec/decision 仍是仓库控制面。

## 验证

实际运行并通过：

```text
uv tool run pytest tests/test_check_method_update_sources.py tests/structure -q
36 passed

python3 scripts/check_control_plane.py
PASS: control plane checks succeeded

make test-structure PYTHON='uv run --with pytest python'
PASS: control plane checks succeeded
11 passed

python3 scripts/check_method_update_sources.py \
  --workflow-pack-root /tmp/mattpocock-skills-v1.1.0 \
  --workflow-pack-id mattpocock-skills \
  --json
verified pinned Git ref=v1.1.0 ahead/behind=0/0; adapter=mattpocock skills=38 promoted=21 version_status=partial license=MIT

python3 scripts/install_harness_skills.py --dry-run
dry-run install software-development/a-philosophy-of-software-design -> <destination>

git diff --check
python3 -m py_compile scripts/check_method_update_sources.py scripts/check_control_plane.py
```

本机系统 Python 没有 pytest module，因此 pytest 与 Makefile 验证通过 `uv` 提供隔离的 pytest 环境；没有修改项目依赖。

## 未执行

- 没有安装或 vendor 上游 skill。
- 没有修改其他 Hermes profile。
- 没有 commit、push 或创建 PR。

## 独立评审处置

独立 pre-commit review 提出的 3 个 major 已全部关闭：

1. diff review 已显式纳入 untracked files；
2. active plan 已移除，只保留本 completed 记录；
3. generic Git comparison 已改为 upstream-aware。

同时处理了 metadata 人类输出、symlink/超大文件边界、domain glossary 路径、active-plan `ready` 状态，以及 brief/handoff 的保存与归档生命周期。

## 后续维护

- 新 release 出现后，先 clone/pin snapshot 并运行通用 source checker。
- 先更新 source-specific crosswalk，再决定是否更新正式方法面。
- 如果未来把某个方法包装为 Hermes skill，必须遵循 `docs/runbooks/harness-skill-authoring.md` 并在临时安装目录验证。
