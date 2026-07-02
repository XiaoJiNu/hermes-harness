# Search Domain Knowledge Base

Agent 搜索领域知识库 — 让 Hermes 和其他 agent runtime 获得准确、最新、全面的信息检索能力。

## 核心问题

Agent 的搜索能力和人类不同：agent 需要的不是"搜索引擎"，而是一条从**意图 → 查询 → 检索 → 提取 → 理解 → 记忆 → 复用**的完整管线。

本知识库解决以下问题：
- Agent 搜索不准：API 搜索 vs 网页搜索的语义鸿沟
- 信息过时：如何获取最新内容而非训练截止日前的知识
- 覆盖不全：如何同时搜网页、学术论文、代码、文档
- 权限控制：让 agent 安全地访问网络，避免越权操作

## 文档地图

| 文档 | 用途 |
|------|------|
| `search-stack-architecture.md` | Hermes 搜索栈整体架构设计 |
| `tool-survey.md` | 开源搜索工具/代码调研（2026年6月数据） |
| `hermes-search-configuration.md` | 各层具体配置指南 |

## 搜索栈分层

```
Layer 0: 意图路由        → Hermes 内部判断用哪种搜索
Layer 1: 默认搜索 Provider → Firecrawl（结构化搜索+爬取）
Layer 2: 免费/隐私补充    → SearXNG / open-webSearch（无 API Key）
Layer 3: 轻量网页读取    → Jina Reader（URL → LLM 可读文本）
Layer 4: 动态网页交互    → Browser Use（低权限沙箱）
Layer 5: 记忆/知识持久化  → Graphiti / Mem0 / Qdrant（搜索记忆）
Layer 6: 编程层          → Aider skill + Cline/OpenCode 外部调用
```

## 设计原则

1. **逐层降级**：API 搜索优先，自建搜索兜底，浏览器最后
2. **权限最小化**：动态浏览器只用低权限沙箱
3. **记忆可复用**：搜索结果持久化，避免重复搜索
4. **Provider 可替换**：不绑定单一搜索服务
5. **Runtime 无关**：方法适用于 Hermes / OpenClaw / Claude Code 等

## 更新日志

- 2026-06-11：初始化知识库，建立搜索栈架构和工具调研
