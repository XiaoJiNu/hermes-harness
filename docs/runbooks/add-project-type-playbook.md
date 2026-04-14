# Runbook: Add Project Type Playbook

当一个新项目无法被现有文档覆盖时，按本流程扩展仓库。

## 触发条件

满足任意一条即触发：
- `docs/catalog/project-types.md` 无法明确归类
- 现有 playbook 只能给出很泛的建议，缺少该类项目专属控制面
- 团队开始重复做某类项目，但每次都要重新解释方法

## 步骤

1. 先做 intake
   - 项目目标是什么
   - 主要产出是代码、模型、数据管道、知识库，还是混合体
   - 该类项目的验证和 done 定义是什么

2. 与现有项目类型比较
   - 说明为什么软件项目 / 算法工程 / 数据管道方法不够
   - 明确新增类型的边界

3. 用模板创建新 playbook
   - 复制 `docs/templates/project-type-playbook-template.md`
   - 写清最小控制面、验证入口、常见反模式

4. 同步更新目录
   - 更新 `docs/catalog/project-types.md`
   - 更新 `docs/README.md`
   - 如有必要，更新 `README.md`

5. 同步维护治理面
   - 如果新增类型需要新的检查，补充 `tests/structure/` 或 `scripts/check_control_plane.py`
   - 如果还有未解决缺口，记录到 `docs/tech-debt-tracker.md`

6. 运行验证
   - `python3 scripts/check_control_plane.py`
   - `python3 -m pytest tests/structure -q`
   - `make test-structure`

## 产出要求

新增的方法不能只是“说明一下”。
它必须成为可查找、可链接、可维护、可验证的仓库工件。
