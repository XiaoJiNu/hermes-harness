# Hermes Harness 操作模型

日期：2026-04-14

## 目标

定义 Hermes 在本仓库中的工作方式，使本仓库成为“harness 方法参考仓库”的控制面，而不是某个具体业务仓库的私有笔记。

## 作用范围

本文件适用于：
- 维护本仓库自身
- 用本仓库指导未来新项目启动
- 为团队统一 harness 方法
- 让 Hermes 作为默认执行层来读取、选择和扩展方法

## Hermes 与 Harness 的关系

- harness 是仓库级控制系统
- Hermes 是默认执行 runtime
- Hermes 不是 source of truth
- 本仓库才是 source of truth

同时要明确：
- Hermes 不是唯一 runtime
- 如果未来某类任务更适合 Claude Code、Codex 或其他 runtime，方法仍应复用本仓库的控制面

## 本仓库的核心定位

请把本仓库理解为：
- 一个“方法目录”
- 一个“项目类型选择器”
- 一个“新增项目类型方法的工厂”
- 一个“持续维护 harness 方法的控制面”

## Hermes 在本仓库中的标准工作流

### 第 1 步：先判断任务属于哪类

通常分为：
- 维护本仓库
- 为新项目选择方法
- 补充新的项目类型方法
- 更新已有方法
- 增强机械化约束
- 同步 Hermes / harness 方法更新
- intake agent-skills 或其他外部 workflow pack
- 为论文复现项目选择 `docs/playbooks/ai-paper-reproduction.md`，复制 `docs/templates/ai-paper-reproduction-project-template.md`，并建立 claim matrix / source survey / gap log

如果用户明确要求“看看 Hermes 或 harness 有没有更新”，先执行：

```bash
python3 scripts/check_method_update_sources.py --json
```

需要最新远端状态时再执行：

```bash
python3 scripts/check_method_update_sources.py --fetch --json
```

然后按 `docs/runbooks/hermes-method-update-sync.md` 过滤“有方法价值”的更新。

如果用户明确要求集成外部 skill pack，先按对应入口检查。例如 `agent-skills`：

```bash
python3 scripts/check_method_update_sources.py \
  --agent-skills-root /path/to/agent-skills \
  --json
```

通用或 nested skill pack 使用 `--workflow-pack-root` 和稳定的 `--workflow-pack-id`。然后按 `docs/runbooks/agent-skills-method-intake.md` 和对应 source-specific crosswalk 做 intake。外部仓库只能作为 external method source，不能绕过本仓库 source of truth。

### 第 2 步：重建仓库上下文

开始非平凡任务前，至少阅读：
1. `README.md`
2. `AGENTS.md`
3. `docs/README.md`
4. `docs/catalog/project-types.md`
5. 相关 playbook / runbook / spec / active plan

### 第 3 步：大任务先计划

如果任务会改多个 surface，应先更新：
- `docs/plans/active/`

完成后应把状态为 `done` / `completed` 的一次性计划移动到：
- `docs/plans/completed/`

仍承担持续维护职责的计划可以留在 `docs/plans/active/`，但必须在文件头说明原因。

### 第 4 步：执行一个边界清晰的批次

例如：
- 新增一个项目类型 playbook
- 更新一个已有方法
- 新增一个控制面检查
- 重写一个过时入口文档

不要把多个无关主题混成一个批次。

### 第 5 步：立即验证

最小验证入口：
- `python3 scripts/check_control_plane.py`
- `python3 -m pytest tests/structure -q`
- `make test-structure`

### 第 6 步：同步更新 companion surfaces

如果发生以下变化，要一起更新：
- 新项目类型方法 -> 更新 `docs/catalog/project-types.md` 与 `docs/README.md`
- 方法边界变化 -> 更新相关 playbook / decision
- 发现缺口 -> 更新 `docs/tech-debt-tracker.md`
- 仓库成熟度变化 -> 更新 `docs/QUALITY_SCORE.md`

## 本仓库对未来新项目的使用规则

当用户输入一个新需求时，Hermes 应：
1. 先根据 `docs/catalog/project-types.md` 判断项目类型
2. 选择最匹配的 playbook
3. 如果缺少该类型方法，按 runbook 新增该项目类型的 playbook
4. 再用该方法指导新项目的控制面创建与执行

## 团队使用规则

- 团队可以默认用 Hermes 读取和应用本仓库方法
- 但方法本身必须足够清晰，使其他 runtime 也能使用
- 未来协作时，优先提交仓库工件，而不是只保留聊天解释

## Backpressure 规则

好的结果应是紧凑、可执行的：
- 选择了哪个项目类型方法
- 为什么这么选
- 还缺什么控制面
- 运行了哪些验证
- 哪些缺口已记录为 debt

## Hermes runtime 能力采用规则

Hermes 的新功能只有在能稳定提升 harness 方法时才进入本仓库。

当前默认采用的规则：
- subagent：先定义角色、输入、输出、验证命令，再并发；必要时限制 toolsets、并发数、spawn depth 和成本
- `/steer` 或其他 mid-run nudge：只能作为过程纠偏；如果改变需求，必须回写 spec / plan / runbook
- context / compression：先把关键状态写入仓库工件，再做 focused compression；不要把 source of truth 放在压缩摘要里
- provider / model / timeout：属于 runtime 决策，不写死到方法层；但项目可记录推荐档位、fallback、timeout 和成本约束
- cron / webhook / background：长期任务 prompt 必须自足，默认最小 toolsets，background 任务优先设置 watch_patterns
- plugin / shell hook：只有稳定、重复、可验证的规则才固化；必须有 runbook、回滚说明和测试
- 外部 workflow pack：先做 license / structure / runtime-assumption intake；只把有长期价值的方法改写进本仓库 surface，不直接采用外部 hook、plugin、AGENTS 或 slash command 路径

## 外部方法来源采用规则

`agent-skills`、`mattpocock/skills` 这类仓库属于 external method source。采用时必须遵守：

1. 本仓库仍是 source of truth
2. 先读 `docs/runbooks/agent-skills-method-intake.md`
3. 先更新对应 source-specific crosswalk，例如 `docs/references/agent-skills-crosswalk.md` 或 `docs/references/mattpocock-skills-crosswalk.md`
4. 区分 `skill / persona / command` 与 hook / plugin runtime packaging
5. 外部路径必须适配成本仓库路径：`docs/specs/`、`docs/plans/active/`、`docs/runbooks/`、`docs/playbooks/`
6. copied content 必须满足 license 要求；默认优先提炼和改写方法而不是 vendoring
7. 完成后运行结构验证和 source checker 测试
8. 外部 user-invoked / model-invoked metadata 只作为 intake 证据，不假定与 Hermes 调用语义等价

坏的结果包括：
- 只给泛泛建议，不落到具体文档
- 只说“可以这样做”，却不更新仓库
- 发现新项目类型缺口，却不补 playbook

## Done 定义

一个针对本仓库的批次，只有在以下条件都满足时才算 done：
1. 目标文档或检查已落地
2. 相关 companion surfaces 已同步
3. 验证已运行
4. 剩余缺口已记录到 plan 或 debt
