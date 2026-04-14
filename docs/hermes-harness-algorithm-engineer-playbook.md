# Hermes Harness 算法工程任务方法

日期：2026-04-14

## 目标

给出面向算法工程、模型调研、论文复现、训练与自有数据适配的 harness 方法。

## 适用场景

- 调研候选模型
- 比较论文与开源实现
- 复现官方训练或评测
- 在自有数据上继续训练或微调
- 做对比实验、消融和 baseline 选择

## 核心原则

算法工程任务里，最需要的不是“多写代码”，而是稳定证据链：
- 论文怎么说
- 代码怎么做
- 你实际跑了什么
- 与 baseline 差了多少
- 下一轮为什么值得继续

## 推荐阶段

1. 任务定义
2. 候选模型调研
3. paper-vs-code audit
4. smoke inference / smoke train / smoke eval
5. 官方数据 reproduction
6. 自有数据 adaptation
7. baseline comparison 与 checkpoint

## 最小控制面

- spec
- active plan
- model survey
- paper-vs-code audit
- dataset contract
- train/eval runbook
- run registry
- manifest / comparison surface

## Hermes 的默认工作方式

- 先做 survey 和 audit，再做 full run
- 先做 smoke，再做正式 run
- 报告结果时必须带 comparison 语境
- 把关键结论沉淀到仓库，而不是停留在训练日志或会话中

## 可替换 runtime

Hermes 是默认选择，但算法工程任务同样可以由其他 agent runtime 执行。
不应改变的是：
- run governance
- comparison discipline
- dataset / environment contracts
- done 定义

## 常见反模式

- 只跑实验，不建 registry
- 只记录最好的数字，不记录比较对象
- 论文复现和业务适配混成一次大实验
- 跳过 smoke 直接 full training
