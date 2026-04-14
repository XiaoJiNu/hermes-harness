# Contributing

## 贡献目标

任何贡献都应让本仓库更适合回答两个问题：
- 遇到一个新项目时，应该选择哪个 harness 方法？
- 当现有方法不够时，如何把缺失方法升级成可维护仓库工件？

## 允许的高价值贡献

- 新增项目类型 playbook
- 更新已有 playbook 的过时部分
- 增加新的选择规则、模板或 runbook
- 增强结构测试和控制面检查
- 补充来源映射、维护流程、质量与技术债记录

## 提交流程

1. 先阅读 `AGENTS.md` 与 `docs/README.md`
2. 确认本次改动影响哪些 docs surface
3. 如果是新项目类型，遵循 `docs/runbooks/add-project-type-playbook.md`
4. 如果是方法更新，记录到相应 playbook / decision / audit
5. 运行验证：
   - `python3 scripts/check_control_plane.py`
   - `python3 -m pytest tests/structure -q`
   - `make test-structure`

## 质量标准

- 文档必须面向未来 session 可读
- 文档必须优先强调仓库工件，而不是依赖聊天记忆
- 方法必须尽量 runtime-agnostic
- 如果规则会反复重要，应升级为测试或检查脚本
