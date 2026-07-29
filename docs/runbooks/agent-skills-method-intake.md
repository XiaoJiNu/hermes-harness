# Runbook: External Skill Pack Method Intake

日期：2026-07-29

## 目的

把 `git@github.com:addyosmani/agent-skills.git`、`git@github.com:mattpocock/skills.git` 这类外部 agent workflow pack 的方法同步，变成一个可重复、可验证、runtime-agnostic 的 harness 流程。

核心目标不是复制外部仓库，而是：

1. 检查外部来源的真实状态、许可、版本和结构；
2. 区分可复用方法与 runtime/plugin 包装；
3. 把有长期价值的方法映射到本仓库 source-of-truth surfaces；
4. 运行验证后再提交。

## 已登记来源

```bash
git clone git@github.com:addyosmani/agent-skills.git /tmp/agent-skills
git clone --branch v1.1.0 git@github.com:mattpocock/skills.git /tmp/mattpocock-skills
```

如果 SSH 不可用，可只读改用 HTTPS：

```bash
git clone https://github.com/addyosmani/agent-skills.git /tmp/agent-skills
git clone --branch v1.1.0 https://github.com/mattpocock/skills.git /tmp/mattpocock-skills
```

每次 intake 必须记录 source ID、URL、tag 或 commit 和 license。优先使用正式 release；浮动 `main` 只用于发现变化，不能作为未记录的稳定基线。

## 标准流程

### 1. 只读检查来源状态

兼容入口：

```bash
python3 scripts/check_method_update_sources.py \
  --agent-skills-root /path/to/agent-skills \
  --json
```

通用 skill pack 或 `mattpocock/skills` 使用：

```bash
python3 scripts/check_method_update_sources.py \
  --workflow-pack-root /path/to/mattpocock-skills \
  --workflow-pack-id mattpocock-skills \
  --json
```

需要拉取远端状态时增加 `--fetch`。检查重点：

- git HEAD / ahead / behind / dirty；
- license；
- flat `skills/<name>` 与 nested `skills/<bucket>/<name>` 数量和 frontmatter；
- command / persona / hook 数量；
- plugin manifest 的 promoted 集合、重复项、缺失路径和越界路径；
- 自动识别 source adapter；Matt-specific docs 约束不施加给 generic pack；
- `disable-model-invocation` 与 `agents/openai.yaml` 的调用策略漂移；OpenAI metadata 采用 `0/N` 兼容、`0 < count < N` 报 partial coverage、`N/N` 逐项比对；
- package/plugin 版本状态（`absent / partial / match / mismatch`）和 promoted docs 覆盖；
- Git 比较优先使用当前分支的 `@{upstream}`；detached HEAD 先使用 HEAD 精确匹配的 pinned tag，再回退 `origin/HEAD`，不假设默认分支一定是 `main`；tag clone 的 `0/0` 表示 checkout 与记录基线一致，不表示上游没有新 release；
- 外部 metadata 只读取 pack root 内、非 symlink、大小不超过 1 MiB 的常规文件；外部 surface 目录也必须位于 root 内、不是 symlink 且可读；
- 是否新增 runtime-specific 包装。

### 2. 分类外部内容

按下面层次分类，不要混在一起：

| 层 | 示例 | 处理方式 |
| --- | --- | --- |
| task workflow / skill | `skills/*/SKILL.md`、`skills/*/*/SKILL.md` | 提炼流程、触发条件、red flags、verification |
| persona / role | `agents/code-reviewer.md` | 映射到 multi-agent role map |
| command / entrypoint | `.claude/commands/*.md` | 改写为 runbook entrypoint；不直接采用路径 |
| invocation metadata | `disable-model-invocation`、`agents/openai.yaml` | 只作为调用边界证据；不假定与 Hermes 等价 |
| hook / plugin | `.claude-plugin/`、`hooks/*.sh` | 默认不直接采用；需要单独 runtime adapter 决策 |
| references / docs | `references/*.md`、`docs/<bucket>/*.md` | 可改写为 `docs/references/` 或 playbook checklist |

如果上游有 promoted / in-progress / personal / deprecated 等层级，只把正式 manifest 或 release 标记为 promoted 的内容纳入主 crosswalk；其他 bucket 默认 defer。

单个 snapshot 中的 manifest 是 promoted 集合的 canonical 声明。检查器可以发现重复、悬空和不安全路径，但不能凭目录位置推断一个未列出的 skill 是否“本应 promoted”；这类遗漏必须通过上一次 pinned manifest 与本次 manifest 的 tag/commit diff 发现并由人工判断。

### 3. 过滤可采用的方法

优先采用：

- 能增强 spec / plan / build / verify / review / ship 阶段纪律的方法；
- anti-rationalization / red flags / verification 这类能约束 agent 跳步的结构；
- task-level workflow selection；
- progressive disclosure 和 context hygiene；
- multi-agent fan-out + merge 的边界规则；
- 可映射为脚本、测试、模板或 runbook 的检查。

不直接采用：

- Claude plugin 安装说明作为本仓库必需流程；
- `.claude/commands` 作为 canonical command paths；
- session-start hook 自动注入整段 skill 内容；
- 外部 `AGENTS.md` / `CLAUDE.md` 覆盖本仓库入口；
- `SPEC.md`、`tasks/plan.md`、`CONTEXT.md`、`docs/agents/` 等平行控制面路径；
- 自动 commit / push 规则，除非本仓库 runbook 明确授权；
- 外部调用 metadata 被假定为 Hermes 等价策略。

### 4. 更新 source-specific crosswalk

每个 promoted skill 必须写明：

- `adopt`：存在独特、长期有效的方法，进入正式 surface；
- `merge`：只吸收差异，合入现有方法；
- `covered`：当前能力已经覆盖，不重复；
- `defer`：需要项目类型或真实需求后再评估；
- `reject direct`：runtime-specific、个人化或与控制面冲突。

已登记 crosswalk：

- `docs/references/agent-skills-crosswalk.md`
- `docs/references/mattpocock-skills-crosswalk.md`

### 5. 映射到本仓库 surface

| 外部变化 | 应更新 surface |
| --- | --- |
| 新 workflow skill | 对应 source-specific crosswalk，必要时相关 playbook / runbook |
| skill anatomy 改变 | `docs/templates/`、general playbook、structure tests |
| 新 persona / orchestration 模式 | `docs/playbooks/multi-agent-product-ops.md` |
| 新 command | runbook entrypoint；不要复制 slash command 路径 |
| 新 hook / plugin 能力 | 操作模型；只有可验证时新增 runtime adapter runbook |
| 新 checklist | `docs/references/` 或相关 playbook verification section |
| 新 license / packaging 变化 | ADR / runbook / debt tracker |

### 6. 许可要求

已登记的 `addyosmani/agent-skills` 与首轮 `mattpocock/skills` 基线均为 MIT。每次仍必须从锁定 tag/commit 重新核实。

默认做法是“提炼并改写方法”，避免不必要 vendoring。若复制实质性原文、脚本或模板，必须：

1. 在目标文件或 `docs/references/` 中标明来源；
2. 保留 license notice；
3. 说明本仓库如何维护该副本；
4. 加入结构检查或更新脚本，避免副本漂移。

### 7. 验证

```bash
python3 scripts/check_control_plane.py
python3 -m pytest tests/structure -q
python3 -m pytest tests/test_check_method_update_sources.py -q
make test-structure
python3 scripts/check_method_update_sources.py --json
```

如本地有 workflow pack，再跑：

```bash
python3 scripts/check_method_update_sources.py \
  --workflow-pack-root /path/to/workflow-pack \
  --workflow-pack-id <stable-source-id> \
  --json
```

## Done 定义

一次 external skill pack intake 只有满足下面条件才算 done：

- 已检查外部仓库状态、tag/commit、license 和结构；
- promoted skills 都有 adopt / merge / covered / defer / reject 结论；
- 已更新对应 source-specific crosswalk 或明确说明无需更新；
- 有长期价值的方法已落到本仓库 playbook / runbook / template / test；
- runtime-specific 内容未被直接混入 source of truth；
- companion surfaces 已同步：docs index、operating model、quality/debt、检查脚本；
- 验证已运行并通过。
