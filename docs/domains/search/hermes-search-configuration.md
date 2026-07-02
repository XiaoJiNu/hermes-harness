# Hermes 搜索栈配置指南

按用户选择的搜索栈分层，逐一配置。

## 架构总览

```
Hermes Agent
  ├─ 默认 Web Provider：Firecrawl
  ├─ 免费/隐私搜索补充：SearXNG 或 open-webSearch
  ├─ 轻量网页读取：Jina Reader skill
  ├─ 动态网页：Browser Use，只给低权限沙箱
  ├─ 记忆层：Graphiti / Mem0 / Qdrant
  └─ 编程层：Aider skill + Cline/OpenCode 外部调用
```

---

## Layer 1: Firecrawl（默认 Web Provider）

### 2.1 获取 API Key
```bash
# 注册获取 API Key
# https://firecrawl.dev/
```

### 2.2 配置环境变量
```bash
# 编辑 ~/.hermes/profiles/deepseek/.env
FIRECRAWL_API_KEY=fc-xxxxxxxxxxxxxxxxxxxxxxxx
```

### 2.3 自部署（可选，替代付费 API）
```bash
git clone https://github.com/mendableai/firecrawl.git
cd firecrawl
# 需要 Redis + Python 环境
docker compose up -d
# 自部署后设置
FIRECRAWL_API_URL=http://localhost:3002
```

### 2.4 配置 Hermes 使用 Firecrawl
```yaml
# ~/.hermes/profiles/deepseek/config.yaml
web:
  search_provider: firecrawl
  firecrawl:
    api_url: "${FIRECRAWL_API_URL:-https://api.firecrawl.dev}"
```

### 2.5 验证
```bash
curl -X POST https://api.firecrawl.dev/v1/search \
  -H "Authorization: Bearer $FIRECRAWL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "latest AI agent research 2026", "limit": 3}'
```

---

## Layer 2: SearXNG / open-webSearch（免费搜索补充）

### SearXNG 部署
```bash
# Docker 部署
docker run -d --name searxng \
  -p 127.0.0.1:8080:8080 \
  -v ~/.searxng:/etc/searxng \
  searxng/searxng

# 配置 Hermes 搜索后端
# 在 config.yaml 中设置
web:
  fallback_search_url: "http://127.0.0.1:8080/search?q={query}&format=json"
```

### open-webSearch MCP 集成
```bash
# 安装
pip install open-websearch

# 作为 MCP server 运行
open-websearch serve --mcp

# 在 Hermes 中注册 MCP server
hermes mcp add open-websearch --command "open-websearch serve --mcp"
```

### 验证 SearXNG
```bash
curl "http://127.0.0.1:8080/search?q=test&format=json" | python3 -m json.tool | head -30
```

---

## Layer 3: Jina Reader（轻量网页读取）

### 使用方式
无需 API Key（有免费额度），直接 URL 前缀转换：

```bash
# 任意 URL 前加 https://r.jina.ai/
curl https://r.jina.ai/https://en.wikipedia.org/wiki/Large_language_model
```

### 创建 Hermes Skill
见 `~/.hermes/profiles/deepseek/skills/jina-reader/SKILL.md`

### API Key（可选，提升额度）
```bash
# ~/.hermes/profiles/deepseek/.env
JINA_API_KEY=jina_xxxxxxxxxxxxxxxx
```

---

## Layer 4: Browser Use（低权限沙箱）

### 安装
```bash
pip install browser-use
playwright install chromium
```

### 低权限沙箱配置
```bash
# 创建隔离用户
sudo useradd -m -s /bin/bash agent-browser
# 或使用 Docker 沙箱
docker run -d --name browser-sandbox \
  --cap-drop=ALL \
  --security-opt=no-new-privileges \
  browserless/chrome
```

### 创建 Hermes Skill
见 `~/.hermes/profiles/deepseek/skills/browser-use-sandbox/SKILL.md`

### 安全原则
- 只用低权限用户/容器运行浏览器
- 禁止访问 localhost 和内部网络
- 限制文件系统访问
- 设置超时自动终止

---

## Layer 5: 记忆层

### 选项 A：Mem0（优先推荐）
Hermes 原生支持：
```bash
hermes memory setup
# 选择 mem0 provider
# 配置 API Key
# ~/.hermes/profiles/deepseek/.env
MEM0_API_KEY=m0-xxxxxxxxxxxxxxxx
```

### 选项 B：Graphiti（知识图谱）
```bash
# 自部署
git clone https://github.com/getzep/graphiti.git
cd graphiti
docker compose up -d

# 配置 Hermes memory provider（自定义）
# 见 docs/domains/search/memory-layer-guide.md
```

### 选项 C：Qdrant（向量数据库）
```bash
# Docker 部署
docker run -d --name qdrant \
  -p 127.0.0.1:6333:6333 \
  qdrant/qdrant

# Python 客户端
pip install qdrant-client
```

---

## Layer 6: 编程层

### Aider Skill
```bash
# 安装 Aider
pip install aider-chat

# 配置 API Key（复用现有 provider）
# ~/.hermes/profiles/deepseek/.env
# Aider 会自动使用 OPENAI_API_KEY / ANTHROPIC_API_KEY 等
```

创建 skill 后使用 `hermes -s aider` 或在会话中 `/skill aider`。

### Cline / OpenCode 外部调用
```bash
# 通过 tmux 或 subprocess 调用
# 详见 hermes-agent skill 中的 spawning 部分

# CLI 一行调用
hermes chat -q "用 aider 重构 src/search.py 的搜索逻辑"
```

---

## 快速验证脚本

```bash
#!/bin/bash
# scripts/verify_search_stack.sh
echo "=== 搜索栈验证 ==="

# 1. Firecrawl
echo -n "Firecrawl: "
curl -s -o /dev/null -w "%{http_code}" \
  -H "Authorization: Bearer $FIRECRAWL_API_KEY" \
  "https://api.firecrawl.dev/v1/search?query=test&limit=1"
echo ""

# 2. SearXNG
echo -n "SearXNG: "
curl -s -o /dev/null -w "%{http_code}" \
  "http://127.0.0.1:8080/search?q=test&format=json"
echo ""

# 3. Jina Reader
echo -n "Jina Reader: "
curl -s -o /dev/null -w "%{http_code}" \
  "https://r.jina.ai/https://example.com"
echo ""

# 4. Mem0
echo -n "Mem0: "
hermes memory status 2>/dev/null || echo "not configured"

echo "=== 验证完成 ==="
```

---

## 分层降级策略

当某层不可用时，Hermes 应自动降级：

```
Firecrawl API 不可用
  → 降级到 SearXNG / open-webSearch
     → 降级到 Jina Reader（单页读取）
        → 降级到 Browser Use（兜底）
```

配置在 config.yaml 中：
```yaml
web:
  search_provider: firecrawl
  fallback_chain:
    - searxng
    - open-websearch
    - jina-reader
  fallback_timeout: 10  # 每层尝试超时（秒）
```

---

## 相关文档

- `docs/domains/search/README.md`：知识库索引
- `docs/domains/search/search-stack-architecture.md`：架构设计
- `docs/domains/search/tool-survey.md`：工具调研
