# Initial State Audit

日期：2026-04-14

## 初始观察

仓库初始状态只有四份顶层文档：
- `docs/hermes使用harness.md`
- `docs/hermes-harness-operating-model.md`
- `docs/hermes-harness-general-playbook.md`
- `docs/hermes-harness-algorithm-engineer-playbook.md`

## 已有优点

- 已经明确关注 harness engineering
- 已经有通用 playbook 和算法工程 playbook 雏形
- 已经有“用 Hermes 作为操作层”的方向

## 主要问题

1. `docs/hermes-harness-operating-model.md` 错误绑定到另一个具体仓库场景
2. 缺少根入口文件：`README.md`、`AGENTS.md`、`ARCHITECTURE.md`、`CONTRIBUTING.md`
3. 缺少 `docs/README.md` 和项目类型目录，无法直接指导新项目选型
4. 缺少新增项目类型 playbook 的标准流程和模板
5. 缺少最小 mechanical enforcement
6. 缺少持续维护 loop

## 本次改造目标

- 把仓库从“几份分散文档”升级为“可维护的 harness 方法参考仓库”
- 把错误的 repo-specific 内容改成当前仓库专用操作模型
- 为未来新增项目类型建立扩展路径
