# Deployment / Platform Repository Harness Playbook

## 适用范围

适用于：
- 模型或服务部署仓库
- 推理服务平台
- GPU / 容器 / 调度 / 伸缩 / 路由平台
- 平台工程与运行时治理项目

## 核心目标

让 agent 在“可部署、可观察、可回滚、可验证”的平台控制面内工作，而不是只会改 deploy 脚本。

## 最小控制面

至少应有：
- environment / infra contract
- deploy runbook
- rollback runbook
- service SLO / health gate
- config / secret boundary rules
- observability surface
- release / incident registry
- smoke / canary / production promotion rules

## 标准启动流程

1. 明确部署对象与环境层级
   - local / dev / staging / prod

2. 定义发布门
   - build 成功
   - smoke success
   - health checks
   - rollback readiness

3. 建立运行手册
   - deploy
   - rollback
   - incident triage
   - capacity / scaling notes

4. 先打通最小 smoke deploy
   - 不直接以 full production 变更作为第一步

5. 再扩展到 canary / staged rollout
   - 报告变更效果、性能和错误率

## Hermes 的默认工作方式

- 先读 deploy / rollback / environment contracts
- 先做低风险环境验证
- 任何影响生产的改动都要附带可回滚路径
- 汇报时要包含 health、latency、error rate、resource usage 等核心信号

## 可替换 runtime

Hermes 不是唯一选择；任何能读取基础设施代码、执行发布命令、读取日志和更新运行文档的 runtime 都可以。

## 常见反模式

- 只有 deploy 命令，没有 rollback 路径
- 把 secret、config、环境差异写进隐式知识
- 没有 health gate 就推进发布
- 发布结果只有原始日志，没有结构化结论
