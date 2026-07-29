# mattpocock/skills 方法映射

## 目的

本文记录 `https://github.com/mattpocock/skills` 到 `hermes-harness` 的方法映射。它是 source-specific crosswalk，不是上游 skill 的镜像，也不是运行时安装清单。

## 来源基线

- 上游：`https://github.com/mattpocock/skills`
- 首轮 intake 基线：release `v1.1.0`
- 基线 commit：`d574778f94cf620fcc8ce741584093bc650a61d3`
- 许可证：MIT
- 基线检查结果：38 个 `SKILL.md`，其中 plugin manifest promoted 21 个；bucket 为 engineering 17、productivity 5、in-progress 6、misc 4、personal 2、deprecated 4
- promoted 集合以基线 `.claude-plugin/plugin.json` 的 `skills` 列表为准；目录中存在但未进入 manifest 的 skill 不自动进入 intake
- 后续 `main` 可能改变 promoted 集合、调用 metadata 或 package/plugin 版本，因此同步必须锁定 tag 或 commit，不能把浮动 `main` 当作稳定基线

## 吸收原则

1. 本仓库保持 source of truth；外部仓库只提供候选方法。
2. 优先提炼方法差异，落到 playbook、runbook、template 和检查器，不复制完整提示词。
3. `disable-model-invocation`、`agents/openai.yaml`、Claude plugin、slash command 和 hook 都是上游 runtime packaging，不直接进入本仓库控制面。
4. 只有长期稳定、无现有等价能力、需要 runtime 自动触发的方法，才考虑包装成 `skills/` 下的 Hermes skill。
5. 复制实质性文本时必须保留 MIT 来源说明；仅提炼方法时仍应在对应文档的来源段引用上游。

## v1.1.0 promoted skills crosswalk

| 上游 skill | 决策 | 当前/目标落点 | 说明 |
| --- | --- | --- | --- |
| `ask-matt` | merge | `docs/catalog/project-types.md`、通用 playbook | 当前已有项目级和任务级 router，不新增平行入口。 |
| `diagnosing-bugs` | covered | Hermes `systematic-debugging`；通用 playbook 的诊断门 | 不重复创建 skill。 |
| `grill-with-docs` | adopt | `docs/runbooks/requirements-discovery-and-domain-modeling.md` | 吸收“澄清与文档同步进行”，但工件路径改为本仓库约定。 |
| `triage` | adopt | multi-agent playbook 的 canonical Intake 与 routing、agent brief 模板 | 吸收先验证 claim、状态机、side-effect confirmation 和 agent-ready brief。 |
| `improve-codebase-architecture` | merge | APOSD skill、领域建模和 diff review runbook | 吸收先读领域语言、寻找 deepening opportunity、保留证据；不采用强制 HTML/CDN 报告。 |
| `setup-matt-pocock-skills` | reject direct | `AGENTS.md`、catalog、project playbook | 不让外部 setup 改写控制面或创建平行 `CONTEXT.md` / `docs/agents/` 体系。 |
| `tdd` | covered | Hermes `test-driven-development` | 不重复创建 skill。 |
| `to-spec` | merge | `docs/hermes-harness-general-playbook.md` | 吸收“已有讨论时做 synthesis，不重新采访”。 |
| `to-tickets` | adopt | dependency-aware delivery planning runbook、active plan 模板 | 吸收 tracer bullet、依赖边、tracker 映射和 expand–migrate–contract 例外。 |
| `wayfinder` | adopt | long-horizon decision mapping runbook | 吸收 destination、frontier、fog 和 decision-first 工作流。 |
| `implement` | merge | 通用 playbook 的执行与验证闭环 | 保留 spec/plan 驱动，不采用上游命令入口。 |
| `prototype` | adopt delta | 软件产品 playbook 的 canonical prototype procedure | 吸收“先声明问题、throwaway、单命令运行、verdict/cleanup gate、结论进入正式工件”。 |
| `research` | covered | Hermes research/delegation 能力、工程设计评审 | 不重复创建 skill。 |
| `domain-modeling` | adopt | 需求与领域建模 runbook、领域术语模板 | 吸收 shared language、terms-only glossary 和决策同步。 |
| `codebase-design` | merge | `skills/software-development/a-philosophy-of-software-design/` | 当前已有 deep module / complexity 方法，不重复。 |
| `code-review` | adopt delta | diff review runbook、multi-agent review gate | 吸收固定 review base、Standards/Spec 两轴独立评审和 fixed point。 |
| `grill-me` | merge | 需求与领域建模 runbook | 它只是显式触发 grilling 的薄入口，本仓库保留 runbook 入口而不复制 command。 |
| `grilling` | adopt | 需求与领域建模 runbook | 吸收“事实由 agent 查、决策由人做、一次一个问题”。 |
| `handoff` | adopt | multi-agent playbook 的 canonical Handoff artifact、handoff 模板 | 吸收 durable references、精确下一步和脱敏边界；OS 临时 envelope 只能引用仓库 checkpoint。 |
| `teach` | defer | 无 | 仅在新增教育/课程项目类型后评估，当前不创建其独立工作区体系。 |
| `writing-great-skills` | adopt delta | `docs/runbooks/harness-skill-authoring.md` | 吸收 invocation 边界、progressive disclosure、leading words 和 pruning，并改写为 Hermes 格式。 |

## 非 promoted 与 post-release 内容

基线中的 `in-progress/`、`personal/`、`misc/`、`deprecated/`，以及目录中未被 plugin manifest 引用的 skill（例如基线的 `resolving-merge-conflicts`），只作为探索线索。

后续 `main` 曾出现不同的 promoted 组合，例如 `setup-pre-commit`、`migrate-to-shoehorn`、`scaffold-exercises`、`edit-article`、`obsidian-vault`、`pre-commit` 等。它们在进入正式 release 并完成独立 crosswalk 更新前，默认状态为 defer；不能混入 v1.1.0 基线结论。

非 promoted 内容只有满足以下全部条件才可进入正式方法面：

- 有独立需求或项目类型支撑；
- 明确优于当前能力；
- 经安全、许可证和调用语义评审；
- 有目标文档、验证入口和维护 owner；
- 不依赖作者个人工作流。

## 更新规则

1. 使用 `scripts/check_method_update_sources.py --workflow-pack-root <path> --workflow-pack-id mattpocock-skills` 检查本地 snapshot。
2. 对比上次基线的 tag/commit、promoted manifest、调用策略、版本和 docs 覆盖。
3. 新增或变化的 skill 先更新本 crosswalk，再决定是否修改正式方法。
4. 不允许自动覆盖本地改写内容；同步必须经过人工 review。

## 来源

- `mattpocock/skills`, MIT License, release `v1.1.0`, commit `d574778f94cf620fcc8ce741584093bc650a61d3`
- 本仓库 `docs/decisions/0002-agent-skills-external-method-source.md`
- 本仓库 `docs/runbooks/agent-skills-method-intake.md`
