# <Project / Change> Active Plan

日期：YYYY-MM-DD
状态：active
Owner：
Canonical spec：
相关 decisions：

## Destination

描述完成后用户可观察、系统可验证的目标状态。

## Scope

- ...

## Out of scope

- ...

## Known reality

### Verified facts

- `<fact>` — evidence: `<path/command/result>`

### Assumptions

- `<assumption>` — validation owner: `<owner>`

## Decisions so far

| Decision | Resolution | Rationale | Artifact |
| --- | --- | --- | --- |
| `<decision>` | `<resolution>` | `<trade-off>` | `<spec/ADR path>` |

## Decision Frontier

Decision item 只解决会改变路线的未知，不与 implementation item 混写。

| ID | Decision needed | Why now | Evidence needed | Blocks | Status |
| --- | --- | --- | --- | --- | --- |
| D1 | `<decision>` | `<reason>` | `<research/run>` | `<work IDs>` | pending |

## Fog / not yet specified

- `<known unknown>`

## Work items

`Blocked by` 只写真实依赖，不写建议顺序。优先使用可独立验证的 tracer bullet（tracer-bullet）垂直切片。

| ID | Type | User-visible slice / outcome | Blocked by | Status | Acceptance | Verification |
| --- | --- | --- | --- | --- | --- | --- |
| W1 | implementation | `<end-to-end outcome>` | - | ready | `<observable criterion>` | `<command/evidence>` |

对于无法垂直切分的大范围重构，显式创建 `expand`、`migrate`、`contract` 三阶段工作项。

## Risks and rollback

| Risk | Trigger | Mitigation / rollback |
| --- | --- | --- |
| `<risk>` | `<signal>` | `<action>` |

## Verification log

| Date | Command / evidence | Result |
| --- | --- | --- |
| YYYY-MM-DD | `<command>` | `<pass/fail and key output>` |

## Handoff

- 当前 frontier：
- 下一 ready item：
- 当前 blocker：
- 继续工作前必须读取：
