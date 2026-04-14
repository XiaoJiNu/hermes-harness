# Benchmark / Eval Repository Harness Playbook

## 适用范围

适用于：
- 模型 benchmark 仓库
- 统一评测框架
- leaderboard / regression tracking
- prompt、模型、配置、数据切片的可比较评测项目

## 核心目标

让 agent 不只是“跑一堆 benchmark”，而是围绕可比较、可回归、可解释的 eval 控制面工作。

## 最小控制面

至少应有：
- benchmark spec
- task / metric catalog
- dataset slice contract
- model / prompt / config registry
- run manifest 与 eval registry
- comparison rules
- regression gate
- case-study 或 error-analysis surface

## 标准启动流程

1. 明确评测目标
   - 是做模型选型、回归检测、上线门控，还是研究对比

2. 固定比较单位
   - 模型版本
   - prompt / system prompt
   - sampling 参数
   - 数据切片
   - 指标定义

3. 建立 registry 与 manifest
   - 每次正式 eval 都必须可回溯

4. 先做 smoke eval
   - 小样本验证链路、打分脚本、缓存与输出格式

5. 再做正式 benchmark
   - 输出 summary、diff、错误分布与重要样例

## Hermes 的默认工作方式

- 先写 benchmark spec，再跑大规模 eval
- 先固定 comparison scope，再解读结果
- 汇报时必须带 baseline diff，而不是只报孤立分数
- 如果结果会影响后续决策，必须写入 registry / summary 文档

## 可替换 runtime

Hermes 之外，Claude Code、Codex 或其他 agent runtime 都可以执行；但必须保留：
- 比较对象定义
- run/eval registry
- regression gate
- 误差分析与结论沉淀

## 常见反模式

- benchmark 很多，但没有统一 registry
- 数据切片和 prompt 变了，却拿结果直接横向比较
- 只看平均分，不看失败分布
- 没有 baseline diff 就宣布模型更强
