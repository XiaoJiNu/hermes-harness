# Plan: AI Paper Reproduction Method

日期：2026-04-29
状态：completed

## 目标

为算法工程师新增一个可复用的 AI 论文复现 harness 方法：以后给定 paper 和相关数据时，能系统性完成源码查找、方法还原、实验执行、差距定位和复现报告。

## 范围

- 调研论文复现相关开源仓库、平台和方法来源
- 新增专门的论文复现 playbook
- 新增可维护的外部来源参考清单
- 新增具体论文复现项目控制面模板，便于以后给定 paper 和数据时直接落地 spec / survey / claim matrix / audit / registry / report
- 同步更新 docs index、project type catalog、算法工程 playbook 和结构检查
- 运行验证

## 非目标

- 不为某一篇具体论文写实现代码
- 不承诺在论文信息缺失、数据不可得或算力不足时强行得到同等指标
- 不把任何外部仓库变成本仓库 source of truth

## Done 定义

- `docs/playbooks/ai-paper-reproduction.md` 落地
- `docs/references/ai-paper-reproduction-sources.md` 落地
- `docs/templates/ai-paper-reproduction-project-template.md` 落地
- 目录和控制面检查包含新增 surface
- 验证命令通过
- 本计划归档到 `docs/plans/completed/`

## 2026-04-29 追加记录

使用 GitHub API 抽样核验了关键开源来源的描述、许可证、重定向和 archive 状态，并补充了可复制到具体项目的论文复现控制面模板。该模板把 reproduction spec、source survey、paper-claim-matrix、paper-vs-code audit、data/environment manifest、smoke gates、run registry、gap log 和 reproduction report 收敛为同一套启动工件。
