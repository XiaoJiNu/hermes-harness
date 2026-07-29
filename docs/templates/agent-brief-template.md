# Agent Brief: <issue / work item>

状态：draft | needs-info | agent-ready | human-required | in-progress | done
Owner：
来源 issue / plan：
建议保存路径：`docs/plans/active/<plan-id>-brief-<work-id>.md`

## Claim

原始问题或目标的简明陈述。

## Verified reality

### Reproduction / evidence

- 环境：
- 精确步骤：
- 期望结果：
- 实际结果：
- 证据路径或命令输出：

如果 claim 无法复现，写清尝试过什么，并把状态设为 `needs-info`，不要把未验证描述交给实现 agent。

## Context

- 相关代码/文档：
- 已知调用路径：
- 相关 decision/spec：
- 最近相关变更：

## Scope

- ...

## Out of scope

- ...

## Acceptance criteria

- [ ] `<observable behavior>`
- [ ] `<regression/compatibility condition>`

## Constraints

- 安全/隐私：
- 性能/成本：
- 兼容性：
- 禁止事项：

## Validation

```text
<exact command>
```

预期：`<specific pass signal>`

## Routing decision

- `agent-ready`：claim 已验证，范围和 acceptance 完整，无必须由人做的产品决策。
- `human-required`：仍有产品/安全/权限决策；在这里写明具体问题。
- `needs-info`：缺失可复现证据或关键上下文；写明需要谁补什么。

理由：

## Handoff result

完成后必须更新 canonical plan/spec、附验证结果，并链接 diff；不要只在聊天中宣称完成。
