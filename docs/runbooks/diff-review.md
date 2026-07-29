# Diff Review Runbook

## 目的

对一次变更同时回答两个不能互相替代的问题：

1. Standards：实现是否符合仓库规范、工程质量和安全要求？
2. Spec：实现是否完整、准确地满足目标和验收标准？

两条轴必须独立评审，不能因为代码质量高就推断功能完整，也不能因为测试通过就忽略仓库规范。

## 1. 固定 review base

评审前显式记录目标分支和 base commit。优先使用三点 diff：

```bash
git merge-base <target-branch> HEAD
git diff <target-branch>...HEAD
```

如果工作区尚未提交，同时检查：

```bash
git diff
git diff --cached
git status --short
git ls-files --others --exclude-standard
```

`git diff` 和 `git diff --cached` 都不包含未跟踪文件。必须逐个读取 `git ls-files --others --exclude-standard` 返回的文件；需要统一 diff 视图时，对单个文件使用 `git diff --no-index -- /dev/null <file>`。只有 tracked、staged、untracked 三类输入都纳入 review，才能称为完整工作区评审。

不要默认 `main` 一定是目标分支，不要只看最后一个 commit，也不要在评审过程中悄悄改变 base。

## 2. 收集 canonical inputs

至少读取：

- `AGENTS.md` 和相关 repo instructions；
- spec、ADR、active plan 和验收标准；
- 受影响代码及相邻调用路径；
- 测试、构建和静态检查入口；
- review base 的完整 diff。

如果没有足够 spec，只能完成 Standards review；必须把 Spec review 标记为 blocked，而不是猜测需求。

## 3. Standards 轴

检查：

- repo instructions 和项目约定；
- 正确性、边界条件和错误处理；
- 安全、隐私、凭据和权限边界；
- 可维护性、复杂度和信息泄漏；
- 测试质量、可观察性和回滚；
- 是否引入无关重构或未声明依赖。

每个 finding 必须包含文件/行、风险、证据和最小修复方向。

## 4. Spec 轴

逐条对照目标、范围、非目标和 acceptance criteria：

- 是否存在漏实现；
- 行为是否与 spec 精确一致；
- 每条验收是否有自动化或可重复验证证据；
- 是否偷偷扩大范围；
- 文档、迁移、兼容性和回滚承诺是否完成。

使用 requirement-to-evidence 列表，不用“总体看起来符合”代替逐项核对。

## 5. 可选风险轴

只有风险值得时才增加独立 reviewer，例如：

- security/privacy；
- performance/cost；
- migration/data integrity；
- test strategy；
- deployment/operations。

这些轴是 Standards/Spec 的补充，不取代两条基础轴。

## 6. 汇总与 fixed-point loop

汇总者负责去重和排序，但不得把独立轴压成一个模糊分数。建议严重度：

- blocker：无法安全合并或验收；
- major：高概率造成错误、遗漏或不可接受债务；
- minor：应修复但不阻塞；
- note：非强制改进。

修复后只重跑受影响轴及其验证；如果改动跨越多个轴，则全部重跑。循环直到：

- 没有 actionable blocker/major；
- 剩余 debt 被明确接受并进入 tracker；
- 验证结果与 review base 一致。

## Review 输出模板

```text
Review base: <target>...<head>
Canonical spec: <path>

Standards findings:
- [severity] path:line — evidence — required change

Spec findings:
- [severity] requirement — evidence/missing evidence — required change

Optional risk findings:
- ...

Verification run:
- <command> -> <result>

Decision:
- ready / changes required / blocked
```

## 反模式

- 未固定 base 就开始评审；
- 只审查测试是否通过；
- 把 style review 当 spec review；
- 多 reviewer 复读同一维度；
- finding 没有文件、证据或可执行修复；
- 修复后不重跑相关轴。

## 方法来源

本 runbook 提炼自 `mattpocock/skills` v1.1.0 的 `code-review`，并与本仓库的多 agent correctness/security/test review gate 合并。上游许可证：MIT。
