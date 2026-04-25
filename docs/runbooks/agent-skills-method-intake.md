# Runbook: agent-skills Method Intake

日期：2026-04-25

## 目的

把 `git@github.com:addyosmani/agent-skills.git` 这类外部 agent workflow pack 的方法同步，变成一个可重复、可验证、runtime-agnostic 的 harness 流程。

核心目标不是复制外部仓库，而是：

1. 检查外部来源的真实状态、许可和结构
2. 区分可复用方法与 runtime/plugin 包装
3. 把有长期价值的方法映射到本仓库 source-of-truth surfaces
4. 运行验证后再提交

## 输入来源

默认外部仓库：

```bash
git clone git@github.com:addyosmani/agent-skills.git /tmp/agent-skills
```

如果 SSH 不可用，可只读改用 HTTPS：

```bash
git clone https://github.com/addyosmani/agent-skills.git /tmp/agent-skills
```

## 标准流程

### 1. 只读检查来源状态

如果已有本地 clone：

```bash
python3 scripts/check_method_update_sources.py \
  --agent-skills-root /path/to/agent-skills \
  --json
```

需要拉取远端状态时：

```bash
python3 scripts/check_method_update_sources.py \
  --agent-skills-root /path/to/agent-skills \
  --fetch \
  --json
```

检查重点：

- git HEAD / ahead / behind / dirty
- license，当前应为 MIT
- skill 数量与 frontmatter 有效性
- command / persona / hook 数量
- 是否新增 runtime-specific 包装

### 2. 分类外部内容

按下面五层分类，不要混在一起：

| 层 | 示例 | 处理方式 |
|---|---|---|
| task workflow / skill | `skills/*/SKILL.md` | 提炼流程、触发条件、red flags、verification |
| persona / role | `agents/code-reviewer.md` | 映射到 multi-agent role map |
| command / entrypoint | `.claude/commands/*.md` | 改写为 runbook entrypoint；不直接采用路径 |
| hook / plugin | `.claude-plugin/`、`hooks/*.sh` | 默认不直接采用；需要单独 runtime adapter 决策 |
| references | `references/*.md` | 可改写为 `docs/references/` 或 playbook checklist |

### 3. 过滤可采用的方法

优先采用：

- 能增强 spec / plan / build / verify / review / ship 阶段纪律的方法
- anti-rationalization / red flags / verification 这类能约束 agent 跳步的结构
- task-level workflow selection
- progressive disclosure 和 context hygiene
- multi-agent fan-out + merge 的边界规则
- 可映射为脚本、测试、模板或 runbook 的检查

不直接采用：

- Claude plugin 安装说明作为本仓库必需流程
- `.claude/commands` 作为 canonical command paths
- session-start hook 自动注入整段 skill 内容
- 外部 `AGENTS.md` / `CLAUDE.md` 覆盖本仓库入口
- `SPEC.md`、`tasks/plan.md`、`tasks/todo.md` 等平行控制面路径
- 自动 commit / push 规则，除非本仓库 runbook 明确授权

### 4. 映射到本仓库 surface

| 外部变化 | 应更新 surface |
|---|---|
| 新 workflow skill | `docs/references/agent-skills-crosswalk.md`，必要时相关 playbook / runbook |
| skill anatomy 改变 | `docs/templates/`、general playbook、structure tests |
| 新 persona / orchestration 模式 | `docs/playbooks/multi-agent-product-ops.md` |
| 新 command | runbook entrypoint；不要复制 slash command 路径 |
| 新 hook / plugin 能力 | 操作模型；只有可验证时新增 runtime adapter runbook |
| 新 checklist | `docs/references/` 或相关 playbook verification section |
| 新 license / packaging 变化 | ADR / runbook / debt tracker |

### 5. 许可要求

`agent-skills` 当前 license 为 MIT。若复制实质性原文或脚本，必须保留版权和 license notice。

默认做法是“提炼并改写方法”，避免不必要 vendoring。若未来需要 vendor 某个文件，必须：

1. 在目标文件或 `docs/references/` 中标明来源
2. 保留 MIT license notice
3. 说明本仓库如何维护该副本
4. 加入结构检查或更新脚本，避免副本漂移

### 6. 验证

完成同步后运行：

```bash
python3 scripts/check_control_plane.py
python3 -m pytest tests/structure -q
python3 -m pytest tests/test_check_method_update_sources.py -q
make test-structure
```

如果修改了 `scripts/check_method_update_sources.py`，还要至少跑：

```bash
python3 scripts/check_method_update_sources.py --json
```

如本地有 agent-skills clone，再跑：

```bash
python3 scripts/check_method_update_sources.py \
  --agent-skills-root /path/to/agent-skills \
  --json
```

## Done 定义

一次 agent-skills intake 只有满足下面条件才算 done：

- 已检查外部仓库状态、license 和结构
- 已更新 crosswalk 或明确说明无需更新
- 有长期价值的方法已落到本仓库 playbook / runbook / template / test
- runtime-specific 内容未被直接混入 source of truth
- companion surfaces 已同步：docs index、operating model、quality/debt、检查脚本
- 验证已运行并通过
