# Tech Debt Tracker

日期：2026-04-14
更新：2026-07-29

## Active Debt

1. 目前已显式覆盖通用、软件、算法工程、数据管道、benchmark/eval、deployment/platform、multi-agent product ops 七类方法
   - 仍需后续补齐更多类型，如 dataset curation repo、research survey repo、developer tooling repo

2. 当前结构检查仍偏轻量
   - 后续可增加对目录交叉引用、模板使用、质量分更新的更强校验

3. ~~尚未建立外部来源索引和结构检查能力~~ **部分解决 2026-07-29**
   - 已新增 `docs/runbooks/agent-skills-method-intake.md`
   - 已新增 `docs/references/agent-skills-crosswalk.md`
   - `scripts/check_method_update_sources.py` 已能检测 flat/nested skills、bucket、promoted manifest、调用策略、package/plugin 版本以及原有 command / persona / hook / license surface
   - 已登记第二个来源和 crosswalk：`docs/references/mattpocock-skills-crosswalk.md`
   - 剩余缺口：还没有自动把外部 release notes 或前后两个 pinned manifest 的 tag diff 提炼成候选方法变化；单个 snapshot 不能可靠推断 manifest 遗漏的是 intentional non-promoted 还是发布错误；source snapshot 仍需由维护者自行 clone/pin

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

7. Hermes skill 的 user-invoked / model-invoked portability 仍缺少跨 runtime 标准
   - 2026-07-29 已在 `docs/runbooks/harness-skill-authoring.md` 和 external intake 中明确禁止假定 metadata 等价
   - 剩余缺口：当前只能检测已知 Claude/Codex metadata 漂移，不能自动证明 Hermes 的实际触发行为
