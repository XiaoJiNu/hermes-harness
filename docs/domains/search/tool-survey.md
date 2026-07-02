# Agent 搜索工具/代码调研

> 数据采集时间：2026-06-11，来源：GitHub API + 社区整理

## 一、搜索引擎层

### 1.1 SearXNG ⭐31,845
- 仓库：github.com/searxng/searxng
- 类型：自部署元搜索引擎（Python）
- 特点：聚合 Google/Bing/DuckDuckGo 等 80+ 搜索引擎，无广告无追踪
- 适合：作为 agent 的免费/隐私搜索后端
- 已有 Meilisearch MCP server 可直接接入
- 部署：`docker run -d -p 8080:8080 searxng/searxng`

### 1.2 open-webSearch ⭐1,398
- 仓库：github.com/Aas-ee/open-webSearch
- 类型：多引擎 MCP server + CLI（Python）
- 特点：2025年6月创建，专为 agent 设计，skill-guided 工作流
- 无需 API key，同时搜多个引擎
- 部署：pip install + MCP config

### 1.3 Perplexica
- 仓库：github.com/ItzCrazyKns/Perplexica
- 类型：开源 AI 搜索引擎（TypeScript）
- 特点：Perplexity AI 的开源替代，支持本地 LLM
- 包含 SearXNG 作为搜索后端

### 1.4 agenticSeek ⭐26,499
- 仓库：github.com/Fosowl/agenticSeek
- 类型：全本地自主 agent（Python）
- 特点：无需 API，完全本地运行，支持搜索+浏览+编码
- 适合离线/隐私场景

---

## 二、内容提取层

### 2.1 Firecrawl
- 仓库：github.com/mendableai/firecrawl
- 类型：Web 爬取 API + 开源引擎（TypeScript/Python）
- 特点：网页→Markdown，结构化数据提取，LLM 就绪
- 提供 API（付费）和自部署（开源）两种模式
- API Key 配置：`FIRECRAWL_API_KEY`
- 自部署：`docker compose up`

### 2.2 Crawl4AI ⭐68,234
- 仓库：github.com/unclecode/crawl4ai
- 类型：LLM 友好爬虫（Python）
- 特点：多浏览器并发、智能内容提取、反反爬
- 纯 Python，比 Firecrawl 轻量
- 安装：`pip install crawl4ai`

### 2.3 Jina Reader ⭐11,162
- 仓库：github.com/jina-ai/reader
- 类型：URL 转换服务（Python）
- 特点：任意 URL 前加 `https://r.jina.ai/` 即可转 LLM 可读文本
- 零配置，适合快速读取单个网页
- 免费额度可用

### 2.4 MarkItDown ⭐150,370
- 仓库：github.com/microsoft/markitdown
- 类型：文件格式转换（Python）
- 特点：Office/PDF/图片等→Markdown
- Microsoft 出品，适合处理本地文档
- 安装：`pip install markitdown`

---

## 三、动态交互层

### 3.1 Browser Use ⭐98,163
- 仓库：github.com/browser-use/browser-use
- 类型：AI Agent 浏览器自动化（Python）
- 特点：让 agent 操控真实浏览器，支持复杂交互
- 适合：需要登录、表单填写、动态加载的页面
- 安全注意：必须在低权限沙箱中运行

### 3.2 Playwright MCP Server
- 仓库：github.com/microsoft/playwright-mcp
- 类型：MCP server（TypeScript）
- 特点：Microsoft 官方，通过 MCP 协议控制浏览器
- 适合：作为 Hermes MCP tool 集成

### 3.3 Browserbase
- 类型：云端浏览器服务（付费）
- 特点：远程浏览器执行，隔离安全
- Hermes 原生支持（`browser` toolset）

---

## 四、深度研究层

### 4.1 GPT Researcher ⭐27,624
- 仓库：github.com/assafelovic/gpt-researcher
- 类型：自主深度研究 agent（Python）
- 特点：自动搜索+爬取+综合，生成研究报告
- 支持多种 LLM
- 可作为独立 agent 或嵌入工具

### 4.2 STORM (Stanford)
- 仓库：github.com/stanford-oval/storm
- 类型：研究写作 agent（Python）
- 特点：自动生成 Wikipedia 式文章
- 包含多角度提问、信息综合等策略

---

## 五、API 搜索服务

### 5.1 Tavily
- 网站：tavily.com
- 类型：AI Agent 专用搜索 API（付费）
- 特点：专为 AI agent 设计，返回结构化结果
- SDK：`pip install tavily-python`

### 5.2 Exa
- 网站：exa.ai
- 类型：语义搜索 API（付费）
- 特点：基于嵌入的语义搜索，适合找相似内容
- SDK：`pip install exa-py`

### 5.3 Apify MCP Server ⭐1,321
- 仓库：github.com/apify/apify-mcp-server
- 类型：2000+ API 聚合（TypeScript）
- 特点：从社交媒体、搜索引擎、电商等提取数据
- 通过 MCP 协议接入 agent

---

## 六、记忆/知识持久化

### 6.1 Graphiti
- 仓库：github.com/getzep/graphiti
- 类型：知识图谱记忆（Python）
- 特点：基于时间线的知识图谱，自动构建实体关系
- 适合：长期 agent 记忆

### 6.2 Mem0
- 仓库：github.com/mem0ai/mem0
- 类型：智能记忆层（Python）
- 特点：自动记忆管理和检索
- Hermes 原生支持（memory provider）

### 6.3 Qdrant
- 仓库：github.com/qdrant/qdrant
- 类型：向量数据库（Rust）
- 特点：高性能向量搜索，适合 RAG 场景
- 部署：Docker 或 cloud

---

## 七、编程层

### 7.1 Aider
- 仓库：github.com/paul-gauthier/aider
- 类型：AI 结对编程 CLI（Python）
- 特点：git 原生、地图式编辑、多文件重构
- 作为 Hermes 编程序能力补充

### 7.2 Cline ⭐63,028
- 仓库：github.com/cline/cline
- 类型：AI 编程 agent（TypeScript）
- 特点：VS Code 插件 + CLI + SDK，模型无关
- 通过外部调用集成

### 7.3 OpenCode / Codex CLI
- 类型：终端 AI 编程工具
- 特点：作为备选 runtime，通过 subprocess 调用

---

## 工具选择决策树

```
需要搜索什么？
├─ 公开网页内容
│  ├─ 结构化搜索 → Firecrawl Search API
│  ├─ 免费/隐私 → SearXNG / open-webSearch
│  └─ 单个页面 → Jina Reader
├─ 动态页面（需登录/交互）
│  └─ Browser Use（沙箱）
├─ 学术论文
│  └─ arXiv API / Semantic Scholar
├─ 代码
│  └─ GitHub Code Search / Sourcegraph
├─ 本地文档
│  └─ MarkItDown + Qdrant/RAG
└─ 深度研究报告
   └─ GPT Researcher / STORM
```

## 更新记录

- 2026-06-11：初始调研，收录 20+ 工具
