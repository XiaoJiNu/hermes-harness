# Tech Debt Tracker

日期：2026-04-14

## Active Debt

1. 目前已显式覆盖通用、软件、算法工程、数据管道、benchmark/eval、deployment/platform、multi-agent product ops 七类方法
   - 仍需后续补齐更多类型，如 dataset curation repo、research survey repo、developer tooling repo

2. 当前结构检查仍偏轻量
   - 后续可增加对目录交叉引用、模板使用、质量分更新的更强校验

3. ~~尚未建立外部来源索引自动提炼能力~~ **部分解决 2026-04-25**
   - 已新增 `docs/runbooks/agent-skills-method-intake.md`
   - 已新增 `docs/references/agent-skills-crosswalk.md`
   - `scripts/check_method_update_sources.py` 已能检测 agent-skills 的 skill / command / persona / hook / license surface
   - 剩余缺口：还没有自动把外部 release notes 提炼成候选方法 diff

4. ~~当前缺少针对 runtime 网络链路问题的标准诊断 runbook~~ **已解决 2026-04-15**
   - 审计记录：`docs/audits/2026-04-15-hermes-codex-tun-instability.md`
   - 正式 runbook：`docs/runbooks/hermes-codex-proxy-setup.md`
   - 2026-04-23 补充：同类问题不只可能来自代理/VPN，也可能来自 Codex Responses timeout 配置与 subagent 继承主模型的组合

5. 运行时恢复方法此前只停留在 audit / 会话记忆中，缺少统一恢复入口和可执行脚本
   - 2026-04-24 已补：`docs/runbooks/hermes-codex-runtime-recovery.md`
   - 自动化入口：`scripts/hermes_codex_runtime_recovery.py`
   - 剩余缺口：当前自动恢复仍主要覆盖 Hermes + Codex，本仓库还没有面向更多 provider 的统一 runtime recovery 框架

6. Hermes / harness 方法更新此前缺少固定 intake 流程
   - 2026-04-25 已补：`docs/runbooks/hermes-method-update-sync.md`
   - 只读检查入口：`scripts/check_method_update_sources.py`
   - 剩余缺口：脚本只负责发现更新压力，尚未自动提炼 release notes 到候选方法 diff
