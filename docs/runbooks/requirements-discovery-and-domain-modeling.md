# 需求澄清与领域建模 Runbook

## 适用场景

在以下任一条件成立时使用：

- 用户描述了目标，但边界、术语或关键决策仍模糊；
- 同一个词在代码、产品和业务中含义不同；
- 已有讨论需要固化成 spec，而不是重新采访；
- 一个决定会影响后续任务拆分、接口或数据模型。

如果当前问题只是可检索事实、简单参数或低风险偏好，不启动完整流程；先自行查证，再采用合理默认值。

## 核心规则

1. 事实由 agent 检索：能从仓库、文档、运行结果或外部来源确认的内容，不反问用户。
2. 决策由人做：涉及产品取舍、不可逆边界或真实意图时，明确提出决策问题。
3. 一次只解决一个决策：不要一次抛出问卷。
4. 每个已确认决定立即进入 canonical artifact，不把聊天记录当 source of truth。
5. glossary 只描述领域术语；任务状态、实现细节和临时 TODO 不进入 glossary。

## Canonical artifacts

按项目实际需要使用以下工件：

- 需求/spec：`docs/specs/`
- 领域术语：`docs/domains/<domain>/glossary.md`，从 `docs/templates/domain-glossary-template.md` 创建；不要另建平行的 `docs/domain/`
- 架构决策：`docs/decisions/`
- 执行计划：`docs/plans/active/`

不要因为上游方法使用 `CONTEXT.md` 或 `docs/agents/`，就在项目根新增平行控制面。

## 流程

### 1. 建立现状

先读取相关 spec、playbook、代码、issue 和历史决策。记录：

- 已知事实及证据；
- 已经决定的事项；
- 尚未决定且会改变方案的事项；
- 仅影响实现、可以延后处理的细节。

### 2. 选择当前决策问题

优先级依次为：

1. 会改变项目边界的决策；
2. 会改变领域语言或数据含义的决策；
3. 会阻塞多个后续任务的决策；
4. 局部实现偏好。

向用户提问时应给出必要上下文、候选方案和推荐，但不要把可查事实包装成选择题。

### 3. 同步 shared language

每当出现新术语、歧义或术语关系时，更新 glossary：

- 一个术语一个 canonical 定义；
- 明确同义词、禁用词或容易混淆的词；
- 给出正例和非例；
- 链接产生该定义的 spec 或 decision。

术语定义应描述领域含义，不绑定某个类名或数据库表名，除非二者本来就是领域概念。

### 4. 判断是否需要 ADR

仅当决策同时具有较高影响时创建 ADR，典型判断条件：

- 难以回滚或迁移成本高；
- 对后来者并不显然；
- 存在真实 trade-off；
- 会约束多个模块、团队或阶段。

普通命名、局部库选择和可轻易撤销的实现细节留在 spec 或 plan，不制造 ADR 噪声。

### 5. 形成 spec

有两种入口：

- discovery：关键决策未完成，继续逐个澄清；
- synthesis：当前对话和证据已经充分，直接整理，不重新询问已回答的问题。

spec 至少写清：目标、用户可见行为、范围、非目标、约束、验收标准、未决问题和引用的 glossary/ADR。

### 6. 退出条件

满足以下条件后才进入任务拆分：

- 关键术语没有未标记歧义；
- 会改变范围或架构的决策已解决或显式列入 frontier；
- spec 有可观察的验收标准；
- 未决问题有 owner 或阻塞关系；
- canonical artifacts 已更新。

随后使用 `docs/templates/active-plan-template.md` 建立执行计划；若路线本身仍未知，转入 `docs/runbooks/long-horizon-decision-mapping.md`。

## 反模式

- 把十几个问题一次发给用户；
- 问用户可以通过读取仓库得到的事实；
- 会后才批量补文档，导致决定与文档漂移；
- 把 glossary 写成状态周报；
- 为每个小决定创建 ADR；
- 已有完整讨论仍从头采访。

## 验证

- glossary 中每个 term 都有唯一含义和来源；
- spec、ADR、plan 不相互复制，而是引用；
- 未决问题与 blocker 可以追踪；
- 下一执行者不需要依赖聊天记录恢复意图。

## 方法来源

本 runbook 提炼自 `mattpocock/skills` v1.1.0 的 `grilling`、`grill-with-docs`、`domain-modeling` 和 `to-spec`，并按本仓库控制面改写。上游许可证：MIT。
