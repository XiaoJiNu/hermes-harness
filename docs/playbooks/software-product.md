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

## 标准启动流程

1. 写产品 spec
   - 目标用户
   - 核心功能
   - 非目标
   - 验收标准

2. 写 architecture
   - 模块边界
   - 依赖方向
   - 配置与运行时分离

3. 建立 mechanical enforcement
   - 测试入口
   - lint/format/type/check
   - 最小 smoke 路径

4. 执行最小功能闭环
   - 不是一次性做完整产品
   - 先做一个最小用户路径

5. 每个批次结束都闭环
   - 验证
   - 更新计划
   - 更新 runbook 或 debt
   - 准备 checkpoint

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
