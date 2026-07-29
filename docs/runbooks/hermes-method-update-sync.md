# Runbook: Hermes Method Update Sync

日期：2026-04-25

## 目的

本 runbook 把“Hermes / harness 方法有没有更新”变成一个可重复执行的仓库流程。

核心目标不是盲目升级 runtime，而是：
1. 先确认本仓库、Hermes runtime 和外部方法来源的真实更新状态
2. 只提炼对 harness 方法有长期价值的变化
3. 把变化同步为仓库工件、检查脚本、playbook 或 debt
4. 让未来 Hermes 使用本仓库时能自动走同一套方法

## 当前 2026-04-25 快照

本次审计得到的事实：

- `hermes-harness` 本仓库：`HEAD...origin/main = 0/0`
  - 说明远端 main 没有新提交需要合并
  - 但工作区已有未提交的 runtime recovery 方法工件，需要完成 companion surface 和验证后再提交

- 本机 Hermes CLI：`Hermes Agent v0.9.0 (2026.4.13)`
  - `hermes --version` 报告有 update available

- 本地 `hermes-agent` source repo：`HEAD...origin/main = 0/1778`
  - 远端已有大量更新，最新 tag 可见 `v2026.4.23`
  - 本地 source repo 仍有未提交改动，包含 Codex timeout / model fallback / env sanitize 等本机修复
  - 因此不应直接运行 `hermes update` 或强行 rebase；应先保护本地改动，再做升级评估

这个快照的含义：
- harness 参考仓库本身没有远端更新压力
- Hermes runtime 有显著新能力和稳定性更新
- 需要同步的是“有方法价值的 runtime 能力”，不是无差别复制 changelog

## 入口命令

默认先运行只读检查：

```bash
python3 scripts/check_method_update_sources.py --json
```

如果需要拉取最新远端状态：

```bash
python3 scripts/check_method_update_sources.py --fetch --json
```

如果 Hermes source repo 不在默认位置：

```bash
python3 scripts/check_method_update_sources.py \
  --hermes-agent-root /path/to/hermes-agent \
  --fetch \
  --json
```

## 标准同步流程

### 0. 先做外部 SOTA / 热点方法扫描，并让用户审核

当目标是升级 `hermes-harness` 本仓库的方法时，不只看本地 Hermes changelog。
还必须扫描最新或最热门的外部 agent / harness / context engineering / eval / workflow 方法来源。

推荐来源：
- OpenAI / Anthropic / Google / DeepMind / LangChain / HumanLayer 等一手工程博客或文档
- 近期高热 GitHub agent 框架、workflow 框架、eval harness、context engineering 实践
- 近期论文、技术报告、benchmark / eval 方法
- 用户指定的本地 reference repo 或文章

执行要求：
1. 先列出候选来源、采用理由和可能影响的 repo surface
2. 明确区分“可立即采纳”“需要试验后采纳”“暂不采纳”
3. 在真正修改本仓库方法前，把候选更新发给用户审核
4. 用户审核通过后，才进入文档、脚本、测试更新

注意：如果只是修复拼写、补链接、运行验证这类低风险维护，可以不做完整外部扫描；但任何“升级方法论”的批次都必须做。

### 1. 先确认更新状态

检查三件事：

1. harness repo 是否落后远端
2. Hermes runtime / source repo 是否落后远端
3. Hermes source repo 是否有未提交本地改动

如果 Hermes source repo 有未提交改动：
- 不要直接 `hermes update`
- 不要直接 `git pull --rebase`
- 先把本地改动整理成 branch / patch / commit
- 再单独做 runtime upgrade 批次

### 2. 过滤“值得同步”的变化

只同步会改变 harness 方法的 runtime 能力，例如：

- 影响任务拆分、子代理编排、并发安全的变化
- 影响 context / compression / memory 的变化
- 影响验证、审批、工具执行安全的变化
- 影响 cron / webhook / background process 的长期运行能力
- 影响 provider / model / fallback / timeout 的可靠性变化
- 能从 prose 升级为脚本、测试或 runbook 的变化

不要同步：
- 纯 UI 文案
- 单个 provider 的临时模型名，除非影响选择规则
- 与本仓库方法无关的平台细节
- 还没有稳定验证的实验性功能

### 3. 把 runtime 变化映射为 harness surface

| runtime 变化类型 | 应更新的 harness surface |
|---|---|
| 新的子代理能力 | `docs/playbooks/multi-agent-product-ops.md`、操作模型、必要时新增 handoff 模板 |
| 新的 context / compression 能力 | `docs/hermes-harness-general-playbook.md`、相关项目 playbook |
| 新的 provider / fallback / timeout 能力 | runtime recovery runbook、tech debt、必要时新增通用 provider recovery |
| 新的 cron / webhook / background 能力 | maintenance runbook、run registry 规则、长期任务 handoff 规则 |
| 新的工具安全 / approval 能力 | CONTRIBUTING、操作模型、相关验证规则 |
| 新的可机械化检查 | `scripts/check_control_plane.py`、`tests/structure/`、必要时新增脚本测试 |
| 外部 workflow pack 方法 | `docs/runbooks/agent-skills-method-intake.md`、对应 source-specific crosswalk、相关 playbook / template / structure tests |

### 4. 同步 companion surfaces

任何一次 method update 都至少检查：

- `README.md`
- `docs/README.md`
- `docs/catalog/project-types.md`
- `docs/hermes-harness-operating-model.md`
- 受影响 playbook / runbook
- `docs/tech-debt-tracker.md`
- `docs/QUALITY_SCORE.md`
- 对应 source-specific crosswalk（当变化来自外部 workflow pack 时）
- `scripts/check_control_plane.py`
- `tests/structure/test_harness_repo.py`

### 5. 验证

每次完成同步后运行：

```bash
python3 scripts/check_control_plane.py
python3 -m pytest tests/structure -q
make test-structure
```

如果新增了脚本，还要运行对应脚本测试。

## 本次应采纳的 Hermes runtime 方法增量

从 v0.9.0 到 v0.11.0，最值得进入本仓库方法层的是下面这些，不是完整 changelog。

### 1. 子代理编排更像工程系统

新能力要转成方法要求：
- 子代理不再只是“并行问几个问题”，而应有角色边界
- 需要显式限制并发、spawn depth、toolsets 和成本
- 多子代理写同一仓库时必须有文件协调和 checkpoint 规则
- 对长任务，要有 handoff artifact，而不是只等最终回复

对应采纳：
- `multi-agent-product-ops` playbook 中加入 orchestrator / worker / reviewer 角色约束
- 非平凡任务默认先计划，再考虑 subagent
- 子任务 prompt 必须包含自足上下文、期望产物和验证命令

### 2. 中途纠偏与 backpressure 应成为标准能力

Hermes 新增 `/steer` 一类 mid-run nudge 后，方法层要明确：
- 中途纠偏不等于改 source of truth
- 如果纠偏改变需求，最后必须回写 plan / spec / runbook
- 长任务输出要保持紧凑：事实、改动、验证、剩余风险

对应采纳：
- 操作模型加入“mid-run steering 必须回写仓库工件”的规则
- 长任务要求维护 active plan 或 handoff artifact

### 3. Context / compression 不只是省 token，而是证据链治理

有价值的能力：
- focused compression
- context engine / context references
- compression summary 语言一致性
- 防止 compression thrash / stale session resume

对应采纳：
- 大任务在接近 context 压力时先写仓库摘要，再做 focused compression
- 不把关键状态只留在压缩摘要中
- 交接时优先写 plan / audit / registry，而不是依赖会话恢复

### 4. Provider / model / timeout 要进入可靠性控制面

有价值的能力：
- transport abstraction
- per-provider / per-model timeout
- fallback provider activation
- live model discovery
- GPT-5.5 / newer Codex model availability

对应采纳：
- 模型选择是 runtime 决策，不能写死进 harness 方法
- 但每个项目应记录推荐模型档位、fallback、timeout 和成本约束
- 运行时恢复 runbook 应逐步从 Hermes + Codex 专项升级为 provider-agnostic recovery 框架

### 5. Cron / webhook / background process 要最小化上下文成本

有价值的能力：
- cron job 可配置 enabled_toolsets
- per-job workdir
- background process watch_patterns
- webhook direct-delivery mode

对应采纳：
- 长期任务必须写自足 prompt
- cron 默认只启用必要 toolsets
- background 任务用 watch_patterns 触发错误/完成信号
- 事件通知优先零 LLM direct delivery，只有需要判断时才进 agent

### 6. Plugins / shell hooks 是机械化入口，不是随意扩展

有价值的能力：
- plugins 可注册 command / tool / hook
- `pre_tool_call` 可拦截工具
- shell hooks 可接入生命周期

对应采纳：
- 只有当规则稳定、重复、可验证时才升级为 plugin / hook
- hook 必须有 runbook、回滚说明和测试
- 不把临时个人习惯直接固化成全局 hook

## Hermes 使用本仓库时的新默认行为

当用户要求“分析 Hermes / harness 是否有更新”时，Hermes 应：

1. 先执行 `python3 scripts/check_method_update_sources.py --json`
2. 如果需要最新远端状态，再执行 `--fetch --json`
3. 对方法论升级批次，搜索最新或最热门的外部 SOTA agent / harness / context engineering / eval 方法
4. 先整理候选来源、采用理由、影响 surface 和风险，交给用户审核
5. 用户审核通过后，读取本 runbook 和 maintenance runbook
6. 把 runtime changelog 与外部方法过滤成“方法增量”
7. 只更新有长期价值的仓库工件
8. 同步更新 docs index、quality、debt 和结构检查
9. 运行验证后再宣称完成

## 升级 Hermes runtime 的安全门槛

只有满足下面条件时，才考虑真正升级本机 Hermes：

1. `hermes-agent` source repo 没有未处理本地改动，或本地改动已提交 / stash / patch
2. 已记录当前 `hermes --version`
3. 已确认用户愿意承担 runtime 升级风险
4. 升级后运行：
   - `hermes --version`
   - `python3 scripts/hermes_codex_runtime_recovery.py --json`
   - 最小 `hermes chat` smoke test
5. 如果 live install 指向错误 source，再按 `docs/runbooks/hermes-codex-runtime-recovery.md` repoint

## Done 定义

一次 method update sync 只有满足下面条件才算 done：

- 检查了 harness repo 和 Hermes runtime/source 的真实状态
- 方法论升级批次已完成外部 SOTA / 热点来源扫描，并已让用户审核候选更新
- 明确哪些更新被采纳、哪些暂不采纳
- 有价值的方法已落地到 runbook / playbook / 操作模型 / 检查脚本
- companion surfaces 已同步
- 验证已运行
- 剩余缺口已记录到 tech debt 或 active plan
