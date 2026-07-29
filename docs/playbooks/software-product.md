# Software Product Harness Playbook

## 适用范围

适用于：
- Web / App / Backend / CLI 产品开发
- 以用户功能闭环、接口、服务、交互和可靠性为核心的项目

## 核心目标

让 agent 不只是“写代码”，而是在明确 spec、架构边界、测试和运行手册的前提下，持续交付可验证的软件功能。

## 最小控制面

至少应有：
- `README.md`
- `AGENTS.md`
- `ARCHITECTURE.md`
- `docs/specs/`
- `docs/plans/active/`
- `docs/runbooks/`
- `tests/`
- `Makefile`
- CI

当领域术语复杂、工作跨会话或需要可靠交接时，再增加：

- `docs/domains/<domain>/glossary.md`
- `docs/templates/active-plan-template.md` 的项目副本
- `docs/templates/handoff-template.md` 的 handoff 工件

## 标准启动流程

1. 澄清产品边界和 shared language
   - 能从仓库和用户研究中查到的事实先自行检索
   - 每次只解决一个会改变方案的决策
   - 有歧义的领域术语进入 glossary
   - 详细流程见 `docs/runbooks/requirements-discovery-and-domain-modeling.md`

2. 写产品 spec
   - 目标用户
   - 核心功能
   - 非目标
   - 验收标准

3. 写 architecture
   - 模块边界
   - 依赖方向
   - 配置与运行时分离

4. 建立 mechanical enforcement
   - 测试入口
   - lint/format/type/check
   - 最小 smoke 路径

5. 建立 dependency-aware plan
   - 优先拆成用户可见的 tracer-bullet 垂直切片
   - `Blocked by` 只记录真实依赖
   - 每个 slice 都写 acceptance 和 verification
   - 大范围重构无法垂直切片时，使用 expand → migrate → contract
   - canonical procedure 见 `docs/runbooks/dependency-aware-delivery-planning.md`

6. 必要时先做问题驱动 prototype
   - 先写清 prototype 要回答的一个问题
   - 保持 throwaway，不做生产级 polish
   - 提供一条可重复运行命令
   - 把证据和决定写回 spec/ADR/plan；默认不合并 prototype 代码
   - 结束时必须给出 adopt / reject / needs-more-evidence verdict，并删除 prototype 或记录限期 cleanup owner
   - 一旦进入 production implementation，恢复 TDD、CI、review 和完整质量门；prototype 不能作为跳过这些门槛的理由

本步骤是 question-driven prototype 的 canonical procedure owner；现有 Hermes `spike` skill 可作为执行工具，但不新增重复 runtime skill。

7. 执行最小功能闭环
   - 不是一次性做完整产品
   - 先做一个可端到端验证的最小用户路径

8. 每个批次结束都闭环
   - 验证
   - 更新计划
   - 更新 runbook 或 debt
   - 准备 checkpoint

9. 合并前做 two-axis review
   - Standards：仓库规范、正确性、安全、可维护性和测试质量
   - Spec：逐条核对目标、范围和 acceptance
   - 详细流程见 `docs/runbooks/diff-review.md`

## Hermes 的默认工作方式

- 先读仓库地图
- 先读相关 spec 和 active plan
- 大任务先计划
- 一次只做一个 bounded feature
- 先跑定向验证，再跑回归验证

## 可替换 runtime

Hermes 是默认选择，但也可以用：
- Claude Code
- Codex
- OpenCode
- 其他具备读写仓库与运行命令能力的 agent runtime

不变的部分是：
- 仓库控制面
- 计划和验证纪律
- done 定义

## 常见反模式

- 直接让 agent 生成完整系统
- 只有代码，没有 spec / runbook / tests
- 一个批次里混入多个不相关 feature
- 不跑验证就宣称完成
- 把 prototype 直接演化成生产实现，却没有重新设计和验证
- 用“先改底层、以后再接用户路径”的水平切片制造长期不可验收状态
- 已有完整讨论仍从头采访用户
