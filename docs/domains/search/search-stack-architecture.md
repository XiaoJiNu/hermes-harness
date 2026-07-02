# Hermes Agent 搜索栈架构

## 目标

为 Hermes Agent 建立分层搜索方案，确保：
- 搜索结果**准确**（结构化 API > 网页抓取 > 浏览器交互）
- 信息**最新**（实时搜索而非依赖训练数据）
- 覆盖**全面**（网页 + 学术 + 代码 + 文档）
- 成本**可控**（API 优先但有多层免费兜底）

## 架构图

```
用户请求
    │
    ▼
┌──────────────────────────────────────────────┐
│ Layer 0: 意图路由 (Intent Router)              │
│ Hermes 判断搜索类型：                           │
│  - 实时信息 → Layer 1                          │
│  - 学术/论文 → arXiv + Semantic Scholar       │
│  - 代码搜索 → GitHub Search + Sourcegraph     │
│  - 文档/API  → DevDocs + 官方文档              │
│  - 本地知识 → Layer 5 记忆层                   │
└──────────────┬───────────────────────────────┘
               │
    ┌──────────┼──────────┬──────────┬──────────┐
    ▼          ▼          ▼          ▼          ▼
┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐
│Layer 1│ │Layer 2│ │Layer 3│ │Layer 4│ │Layer 5│
│Fire-  │ │SearXNG│ │Jina   │ │Browser│ │Memory │
│crawl  │ │/open- │ │Reader │ │Use    │ │Layer  │
│       │ │WebSrch│ │       │ │(sand- │ │       │
│       │ │       │ │       │ │box)   │ │       │
└───┬───┘ └───┬───┘ └───┬───┘ └───┬───┘ └───┬───┘
    │         │         │         │         │
    └─────────┴─────────┴────┬────┴─────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Layer 6: 编程层  │
                    │ Aider + Cline   │
                    │ / OpenCode      │
                    └─────────────────┘
```

## 各层详解

### Layer 0: 意图路由

Hermes 在收到搜索需求时，首先判断信息类型：

| 信息类型 | 路由目标 | 触发关键词 |
|----------|---------|-----------|
| 实时新闻/事件 | Layer 1 Firecrawl | "最新""今天""这周" |
| 技术文档/API | Layer 1 + Layer 3 | "文档""API""怎么用" |
| 学术论文 | arXiv API (已集成 skill) | "论文""研究""arxiv" |
| 代码仓库 | GitHub Search + Sourcegraph | "repo""github""代码" |
| 动态网页 | Layer 4 Browser Use | "登录后""需要交互" |
| 历史搜索结果 | Layer 5 Memory | "上次搜的""之前找的" |

### Layer 1: Firecrawl (默认搜索 Provider)

**作用**：主力搜索 + 结构化爬取

- 提供 Web Search API：像搜索引擎一样返回结果列表
- 提供 Scrape API：将任意 URL 转为干净的 Markdown
- 提供 Crawl API：批量爬取整个网站
- 提供 Map API：快速列出网站所有 URL

**优点**：
- 专为 AI/LLM 设计，输出格式优化
- 自动处理反爬、JS 渲染
- 有免费额度（500 credits/月）

**配置**：
```bash
export FIRECRAWL_API_KEY="fc-..."
```

**Hermes 集成**：作为 `web_search` 和 `web_extract` 的默认 provider。

### Layer 2: SearXNG / open-webSearch (免费隐私补充)

**作用**：隐私搜索兜底，无需 API Key

**SearXNG**：
- 自建元搜索引擎，聚合 80+ 搜索引擎
- Docker 一键部署：`docker run -d -p 8080:8080 searxng/searxng`
- 本地运行，零外部 API 依赖
- 已有 MCP server：`meilisearch/meilisearch-mcp`

**open-webSearch**：
- 多引擎 MCP server + CLI
- 免 API key，同时搜 Google/Bing/DuckDuckGo
- 轻量级，适合快速接入

**使用场景**：
- Firecrawl API 额度用尽时的降级方案
- 敏感查询不希望经过第三方 API
- 离线/内网环境

### Layer 3: Jina Reader (轻量网页读取)

**作用**：将任意 URL 快速转为 LLM 可读的纯文本

**使用方式**：
```
任意 URL 前加 https://r.jina.ai/
例如：https://r.jina.ai/https://en.wikipedia.org/wiki/LLM
```

**优点**：
- 零配置，不需要 API Key（免费版有限额）
- 自动提取正文，去掉广告/导航
- 支持 PDF、图片（OCR）
- 有 Python SDK：`pip install jina`

**在 Hermes 中的用法**：
- 当需要快速读取某个网页内容时
- 当 Firecrawl 无法正常提取时作为替代
- 用 skill 封装：`skills/jina-reader/SKILL.md`

### Layer 4: Browser Use (动态网页交互)

**作用**：真实浏览器自动化，处理需要登录/交互的页面

**配置**：
```bash
export BROWSER_USE_API_KEY="..."
```

**安全限制**（关键）：
- ⚠️ 只给**低权限沙箱**：Docker 容器 / firejail
- 禁止访问 localhost 和 127.0.0.1
- 禁止文件下载到敏感目录
- 禁止执行任意 JavaScript（只允许导航和点击）
- 网络隔离：只允许出站 80/443
- 超时：单次操作 30s，总会话 5min

**使用场景**：
- 需要登录的网站（如付费文档）
- JS 重度渲染的 SPA 页面
- 需要多次点击交互的信息收集

### Layer 5: 记忆层 (Memory)

**作用**：搜索结果持久化，避免重复搜索

**候选方案**：

| 方案 | 特点 | 适用场景 |
|------|------|---------|
| **Graphiti** | 知识图谱，自动抽取实体关系 | 需要关联推理的场景 |
| **Mem0** | 轻量记忆，支持语义搜索 | 简单记忆和检索 |
| **Qdrant** | 向量数据库，高性能检索 | 大量搜索结果的语义索引 |

**推荐方案**：Mem0（轻量）+ Qdrant（大规模语义索引）

**配置**：
```bash
# Mem0
export MEM0_API_KEY="..."

# Qdrant (本地)
docker run -d -p 6333:6333 qdrant/qdrant
```

### Layer 6: 编程层

**作用**：搜索结果需要编码处理时，调用 AI 编程工具

**Aider**：终端 AI 结对编程，适合搜索后的代码实现
- Skill 封装：`skills/aider/SKILL.md`
- 支持搜索结果作为上下文输入

**Cline / OpenCode**：外部 agent 调用
- 通过 Hermes 的 `delegate_task` 或 `terminal` 工具调用
- 用于复杂的代码生成任务

## 降级策略

```
优先：Firecrawl API（Layer 1）
  ↓ API 额度用尽
备选：SearXNG 本地搜索（Layer 2）
  ↓ 需要提取内容
提取：Jina Reader（Layer 3）
  ↓ 需要动态交互
降级：Browser Use 沙箱（Layer 4）
  ↓ 搜索完成
持久化：Memory Layer（Layer 5）
```

## 成本估算

| 层级 | 月度成本 | 说明 |
|------|---------|------|
| Firecrawl | $0-$19 | Free tier 500 credits，Hobby $19/月 3000 credits |
| SearXNG | $0 | 自建，只需要服务器 |
| Jina Reader | $0 | 免费版有频率限制 |
| Browser Use | ~$10 | 按浏览器时长计费 |
| Mem0 | $0-$25 | Free tier 可用 |
| Qdrant | $0 | 自建 Docker |

总计：**$0-$54/月**（可全部使用免费方案）
