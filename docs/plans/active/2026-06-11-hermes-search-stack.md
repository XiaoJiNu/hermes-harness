# Plan: Hermes Agent 搜索栈搭建

> 创建日期：2026-06-11 | 状态：active

## 目标

为 Hermes Agent 建立分层搜索栈，让 agent 获得准确、最新、全面的信息检索能力。

## 范围

- 知识库建设：在 hermes-harness 中建立 `docs/domains/search/` 知识库
- 搜索 Provider 选择和配置：Firecrawl（默认）+ SearXNG/open-webSearch（免费补充）
- 内容提取层：Jina Reader（轻量）+ Browser Use（动态页面，低权限沙箱）
- 记忆层：Mem0 / Graphiti / Qdrant
- 编程层：Aider skill + Cline/OpenCode 外部调用
- 创建可复用 Hermes skills

## 搜索栈分层

```
Layer 0: 意图路由
Layer 1: Firecrawl（默认搜索 Provider）
Layer 2: SearXNG / open-webSearch（免费/隐私补充）
Layer 3: Jina Reader（轻量网页读取）
Layer 4: Browser Use（动态网页，低权限沙箱）
Layer 5: Graphiti / Mem0 / Qdrant（记忆/知识持久化）
Layer 6: Aider + Cline/OpenCode（编程层）
```

## 已完成

- [x] 创建 `docs/domains/search/` 知识库（README, 架构, 工具调研, 配置指南）
- [x] 创建 Hermes skills：firecrawl-search, jina-reader, browser-use-sandbox, search-memory-layer, aider-search-coding
- [x] 更新 `docs/README.md` 和 `AGENTS.md` 索引

## 待完成

- [ ] 实际部署 SearXNG 实例
- [ ] 配置 Firecrawl API Key
- [ ] 搭建 Browser Use Docker 沙箱
- [ ] 配置 Mem0 记忆层
- [ ] 验证全栈降级可用

## 关联文档

- `docs/domains/search/README.md`
- `docs/domains/search/search-stack-architecture.md`
- `docs/domains/search/tool-survey.md`
- `docs/domains/search/hermes-search-configuration.md`

## 关联 Skills

- `firecrawl-search`
- `jina-reader`
- `browser-use-sandbox`
- `search-memory-layer`
- `aider-search-coding`
