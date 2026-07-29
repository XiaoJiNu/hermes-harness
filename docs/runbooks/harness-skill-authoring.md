# Harness Skill Authoring Runbook

## 目的

把已经稳定的方法包装成可安装的 Hermes skill，同时避免把外部 runtime packaging 或尚未验证的提示词直接带入 `hermes-harness`。

## 先判断：文档还是 skill

默认先写 playbook/runbook/template。只有同时满足以下条件才新增 `skills/` 资产：

- 方法会重复使用，并且触发条件稳定；
- 需要 agent 在任务开始时主动加载，而不只是供人查阅；
- 当前 Hermes skills 没有等价能力；
- 工作流已经在真实任务中验证；
- 能写出明确的适用/不适用边界和验证步骤；
- 有长期维护价值，而不是某个项目的一次性 prompt。

用户显式触发的 orchestrator workflow 要特别谨慎。外部的 `disable-model-invocation` 或 `agents/openai.yaml` 不等同于 Hermes 调用策略，不能靠原样复制 frontmatter 保持语义。

## 创建流程

1. 搜索当前 profile、插件和仓库 `skills/`，先做重复度检查。
2. 确定 canonical method 文档；skill 应链接并执行方法，不复制整套仓库文档。
3. 选择稳定名称和类别，创建 `skills/<category>/<name>/SKILL.md`。
4. frontmatter 至少与相邻 skill 保持一致：`name`、`description`、`version`、`author`、`license`、`platforms` 和 Hermes metadata。
5. description 写清触发条件和边界，使用用户会说的 leading words；正文包括步骤、失败模式和验证。
6. 大量参考材料放入 `references/`；脚本放入 `scripts/`；模板放入 `templates/`，保持 progressive disclosure。
7. 外部方法需要记录来源、版本/commit、许可证和本地改写点。
8. 更新 `skills/README.md` 和受影响的 docs index。

## 质量门

- 不含凭据、个人路径或作者特定环境假设；
- 不要求不存在的工具、字段或 API；
- 不复制与 profile 内置 skill 相同的方法；
- 步骤能在干净环境中执行；
- 危险操作有显式范围和确认边界；
- 失败时说明诊断与退出条件；
- 正文控制在任务所需范围，参考材料按需加载。

## 验证

先安装到临时目录，不直接污染当前 profile：

```bash
python3 scripts/install_harness_skills.py \
  --source skills \
  --destination /tmp/hermes-harness-skills-test
```

然后验证：

- 目录和 linked files 完整；
- frontmatter 可被 Hermes 识别；
- description 能触发预期任务且不会误触发相邻任务；
- 示例命令真实运行；
- `python3 scripts/check_control_plane.py` 和结构测试通过。

## 维护与淘汰

- 上游变化先进入 source crosswalk，不自动覆盖本地 skill；
- 使用中发现错误时同步修复 skill 和 canonical method；
- 与新内置 skill 重复时，优先合并或删除本地重复资产；
- 删除前检查 installer、README、测试和 cron 引用。

## 方法来源

本 runbook 吸收 `mattpocock/skills` v1.1.0 `writing-great-skills` 的 invocation 边界、progressive disclosure、leading words 和 pruning 思想，并以 Hermes skill 格式及本仓库分发方式重写。上游许可证：MIT。
