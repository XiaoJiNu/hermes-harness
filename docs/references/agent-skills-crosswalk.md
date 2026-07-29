# addyosmani/agent-skills Crosswalk

日期：2026-04-25

## 目的

本文件把 `git@github.com:addyosmani/agent-skills.git` 的方法映射到本仓库的 harness source-of-truth surfaces。

其他来源使用独立 crosswalk；`mattpocock/skills` 见 `docs/references/mattpocock-skills-crosswalk.md`，不要把不同上游的版本、skill 名和采用决定混在同一张表里。

原则：先把外部仓库当作参考来源审查，再把有长期价值的方法改写进本仓库。不要让外部仓库、Claude plugin、slash command 或 session hook 直接成为本仓库的 source of truth。

## 层次映射

| agent-skills 层 | 含义 | 在 hermes-harness 中的对应位置 |
|---|---|---|
| skills | 任务级工作流，定义 how | playbook / runbook / template 中的步骤、反模式、验证门槛 |
| personas | 角色视角，定义 who | `docs/playbooks/multi-agent-product-ops.md` 的 role map / reviewer roles |
| commands | 用户入口，定义 when | 本仓库不复制 slash command；改写为 runbook entrypoint 或 Hermes 操作规则 |
| hooks / plugin | runtime 包装与自动注入 | 默认不直接采用；只有稳定、可回滚、可测试时才作为 runtime adapter |
| references | 检查清单和补充材料 | `docs/references/`、相关 playbook 的 checklist、结构测试 |

## Skill 到 harness surface 的映射

| agent-skills skill | 可复用方法 | 本仓库落点 |
|---|---|---|
| `using-agent-skills` | 任务到工作流的选择器；先判断当前动作属于 spec / plan / build / verify / review / ship | `docs/hermes-harness-general-playbook.md` 的 task-level workflow selection；本文件 |
| `idea-refine` | 模糊需求先发散/收敛再进入 spec | `docs/specs/` 模板或未来需求澄清 runbook |
| `spec-driven-development` | spec before code；success criteria；Always / Ask first / Never boundaries | `docs/specs/`、`docs/hermes-harness-general-playbook.md`、项目类型 playbook |
| `planning-and-task-breakdown` | 小任务、依赖顺序、验收标准、verification checkpoint | `docs/plans/active/`、`docs/templates/project-type-playbook-template.md` |
| `context-engineering` | rules / specs / relevant source / error output 的上下文层级；progressive disclosure | `AGENTS.md` map-not-manual、`docs/hermes-harness-operating-model.md`、active plan handoff |
| `source-driven-development` | 重要框架/API 决策要回到官方文档和当前源码 | 相关 runbook；算法工程和部署 playbook 中的 source verification |
| `incremental-implementation` | thin vertical slices；每个 slice 保持可验证 | `docs/hermes-harness-general-playbook.md`、`docs/playbooks/software-product.md` |
| `test-driven-development` | 行为变更先有测试；bug 先复现再修 | `tests/`、Makefile、相关 playbook 的 verification gates |
| `browser-testing-with-devtools` | 浏览器运行态验证、console/network/DOM/screenshot | 软件产品 playbook 的 UI 验证段；browser QA runbook（如未来新增） |
| `debugging-and-error-recovery` | reproduce / localize / reduce / fix / guard | runtime recovery runbook、systematic debugging 方法 |
| `code-review-and-quality` | correctness / readability / architecture / security / performance 五轴 review | pre-commit review、PR workflow、`docs/playbooks/multi-agent-product-ops.md` |
| `code-simplification` | Chesterton's Fence；不要无根据删改；降低复杂度 | refactor runbook / tech debt grooming |
| `security-and-hardening` | OWASP、secrets、input validation、boundary validation | deployment / software product playbook 的 security gate |
| `performance-optimization` | measure first；只优化有证据的问题 | deployment / benchmark / software product playbook 的性能门槛 |
| `git-workflow-and-versioning` | 小提交、清晰描述、变更可回滚 | GitHub workflow skill；CONTRIBUTING / PR runbook |
| `ci-cd-and-automation` | shift-left quality gates；CI 反馈循环 | `.github/workflows/ci.yml`、`scripts/check_control_plane.py`、structure tests |
| `deprecation-and-migration` | 迁移/废弃需要计划、兼容窗口、回滚 | deployment-platform playbook；ADR / migration runbook |
| `documentation-and-adrs` | 记录 why；ADR 保存长期决策 | `docs/decisions/`、docs index |
| `shipping-and-launch` | 发布前 fan-out review、go/no-go、rollback plan | deployment-platform playbook；multi-agent product ops 的 ship review gate |
| `api-and-interface-design` | contract-first、Hyrum's Law、边界验证 | software product / deployment platform playbook |
| `frontend-ui-engineering` | 组件、设计系统、WCAG、响应式 | software product playbook |

## 路径适配规则

不要引入平行控制面；外部路径必须改写到本仓库的 `docs/specs/`、`docs/plans/active/`、`docs/runbooks/`、`docs/playbooks/` 等 source-of-truth surfaces：

| agent-skills 默认 | 在本仓库应改写为 |
|---|---|
| `SPEC.md` | `docs/specs/<name>.md` |
| `tasks/plan.md` | `docs/plans/active/<date>-<slug>.md` |
| `tasks/todo.md` | active plan 的 task section，或未来受控的 `docs/tasks/` |
| `.claude/commands/*.md` | runbook / playbook entrypoint，不作为 canonical path |
| `hooks/session-start.sh` | 默认不采用；如需采用必须有 runbook、回滚说明、测试 |
| `CLAUDE.md` | 不替换；本仓库使用 `AGENTS.md` + docs index |

## 当前采用范围

P0 已采用：

1. 外部方法来源 ADR
2. 本 crosswalk
3. `agent-skills` intake runbook under `docs/runbooks/`
4. general playbook 的任务级 workflow selection
5. multi-agent playbook 的 `skill / persona / command` 分层和 anti-router 规则
6. method update source script 对 agent-skills surface 的只读检测

暂不采用：

- Claude plugin 安装方式
- slash command 文件
- session hook 自动注入
- 外部仓库原文大段 vendoring

## 验证

每次更新本 crosswalk 后运行：

```bash
python3 scripts/check_control_plane.py
python3 -m pytest tests/structure -q
python3 -m pytest tests/test_check_method_update_sources.py -q
```
