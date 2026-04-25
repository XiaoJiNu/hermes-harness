# Hermes + Codex 在 VPN TUN 模式下不稳定审计

日期：2026-04-15

> 更新：2026-04-23
>
> 后续再次排障确认：问题不只来自 `tun mode`。
> 在 shell 代理变量已经恢复、live install 已指向本地源码的前提下，
> 仍可复现两类新症状：
> - `openai-codex` / Responses API 在约 1 分钟量级报 `APITimeoutError`
> - subagent 默认继承主模型 `gpt-5.4` + `high reasoning`，上下文可膨胀到 `~51k tokens`
>
> 这说明链路问题之外，还存在 **运行时实现与本机配置叠加导致的不稳定**。

## 背景

本次问题来自本地使用 Hermes 作为运行时、`openai-codex` 作为主 provider 的实际使用过程。
用户说明当前 VPN 工作在 `tun mode`。

## 观察到的症状

1. Codex 会话在 2026-04-15 出现：
   - `ReadError`
   - `[SSL: DECRYPTION_FAILED_OR_BAD_RECORD_MAC] decryption failed or bad record mac`

2. 本地 Hermes 日志已出现过：
   - `Request timed out.`

3. 该问题不是单纯的“完全无法访问 chatgpt.com”。
   同一台机器上，直连 `chatgpt.com:443` 的 TLS 握手可以成功，但对 `https://chatgpt.com` 的 HTTP 请求会落到 Cloudflare challenge。

## 证据

### 配置面

- `~/.hermes/config.yaml` 当前主模型配置为：
  - `provider: openai-codex`
  - `base_url: https://chatgpt.com/backend-api/codex`
  - `model.default: gpt-5.4`

这说明 Hermes 主请求直接依赖 ChatGPT Codex 后端，而不是通过其他聚合 provider。

### 本地日志与历史

- `~/.codex/history.jsonl` 记录到 2026-04-15 的错误：
  - `[SSL: DECRYPTION_FAILED_OR_BAD_RECORD_MAC]`
- `~/.hermes/logs/errors.log` 记录到 2026-04-15 11:02 的错误：
  - `Request timed out.`

### 代码路径

- Hermes 当前对 Codex 走流式 Responses API。
- `hermes-agent/run_agent.py` 中 `_run_codex_stream(...)` 明确使用持续流式连接。

这意味着链路质量问题会优先表现为：
- timeout
- connection reset / closed
- TLS record 错误
- 流式结果不完整

### 当场诊断结果

1. 当前 shell 中没有显式 `HTTP_PROXY` / `HTTPS_PROXY` / `ALL_PROXY` 环境变量。
   这说明当前更可能是系统级 VPN `tun mode` 在接管流量，而不是 Hermes 进程显式走一个本地应用层代理。

2. 直连 TLS 握手可成功：
   - `TLSv1.3`
   - 证书 `commonName=chatgpt.com`

3. `curl -I https://chatgpt.com` 返回：
   - `HTTP/2 403`
   - `cf-mitigated: challenge`

这说明：
- 基础 DNS / TCP / TLS 并未完全失效
- 但当前出口路径对 ChatGPT / Cloudflare 的风控与长连接流量较敏感

## 诊断结论

本次问题更接近“链路层或传输层不稳定”，而不是 Hermes 配置语义错误。

更具体地说，问题最可能发生在下面这条链路上：

- 本机
- VPN `tun mode`
- 到 `chatgpt.com/backend-api/codex` 的长连接 / 流式请求

`DECRYPTION_FAILED_OR_BAD_RECORD_MAC` 一般意味着 TLS record 在传输过程中被截断、损坏、乱序或被中间层错误处理。
在本场景里，它比“鉴权错了”“模型名错了”“Hermes prompt 有问题”更像网络层症状。

但在 2026-04-23 的复盘中，又确认了两个独立放大器：

1. `hermes-agent/run_agent.py` 的 Codex Responses 流式路径没有显式传入 timeout
   - 普通 chat completions 流式路径已有 `httpx.Timeout`
   - Codex 的 `responses.stream()` / `responses.create(stream=True)` 当时依赖 SDK 默认 timeout
   - 在不稳定链路下，这会表现为更早的 `APITimeoutError`

2. 本机 `~/.hermes/config.yaml` 的 `delegation.*` 为空
   - subagent 默认继承主代理的 `gpt-5.4`、`openai-codex`、`high reasoning`
   - 长任务中更容易把子代理推到高 token、大等待、弱链路的组合

## 最可能原因

1. `tun mode` 下的 MTU / 分片问题
   - 长连接流式响应比短请求更容易暴露分片、重传和 record 边界问题

2. 当前 VPN 节点质量波动
   - 丢包、抖动、短时重路由会先打坏 WebSocket / SSE / 长流式连接

3. UDP / QUIC / 中间层优化干扰
   - 某些 VPN 或代理实现对 ChatGPT / Cloudflare 的实时流量兼容性较差

4. Cloudflare 风控对当前出口更敏感
   - 即使 TLS 可建立，也可能对后续请求行为施加 challenge 或更严格的连接治理

## 影响面

当前影响的不只是主对话请求。

由于 Hermes 当前主 provider 就是 `openai-codex`，辅助任务也可能跟随主 provider 走同一链路，因此一次链路抖动会放大为：
- 主回复超时
- 辅助标题生成失败
- vision / compression 等辅助调用一起变脆

## 建议措施

### 立即措施

1. 优先不要用 `tun mode` 跑 Hermes + Codex
2. 改用应用层显式代理，让 Hermes 走稳定的 `ALL_PROXY` / `HTTPS_PROXY` / `HTTP_PROXY`
3. 优先使用 `socks5://` 或稳定的本地 HTTP 代理，而不是完全依赖系统级全局接管
4. 如果必须使用 `tun mode`，优先换节点并测试更小的 MTU

### 配置侧措施

1. 保留 Codex 作为主模型时，不要让所有 auxiliary 任务也默认压到 Codex 链路
2. 为 Hermes 配置 fallback provider，避免所有请求都卡死在 `openai-codex`
3. 把代理配置显式化，减少“当前系统网络状态不透明”带来的诊断成本

### 工程侧后续

1. 增加一份运行时网络诊断 runbook
2. 为 Hermes / Codex 链路故障建立更明确的故障分类
3. 区分：
   - provider 认证问题
   - Cloudflare / challenge 问题
   - 流式连接中断问题
   - 本地 VPN / 代理路径问题

## 当前判断

本次问题的主因判断为：

- `VPN tun mode` 下到 `chatgpt.com/backend-api/codex` 的链路不稳定

但到 2026-04-23 为止，更准确的判断应为：

- 主因仍包含 `tun mode` / 不稳定出口链路
- 次因包括 Codex Responses 路径缺少显式 timeout
- 放大因子包括 subagent 默认继承 `gpt-5.4 high`，导致长任务更脆

而不是：

- 仓库文档问题
- Hermes 基本配置格式错误
- 本地 Codex token 缺失

## 实际解决过程（2026-04-15）

### 问题复现

电脑重启后 Hermes + Codex 再次无法使用。根因：`~/.bashrc` 中只有 `proxyon` alias，
没有默认 export，重启后 shell 进程拿不到代理环境变量。

### 修复操作

在 `~/.bashrc` 的 proxy 配置区域，将 alias-only 改为启动时自动 export：

```bash
# Proxy — system proxy mode (port 7897), auto-enabled on startup
export http_proxy="http://127.0.0.1:7897"
export https_proxy="http://127.0.0.1:7897"
export all_proxy="socks5://127.0.0.1:7897"
export NO_PROXY="localhost,127.0.0.1,::1"
alias proxyon='export http_proxy=http://127.0.0.1:7897; export https_proxy=http://127.0.0.1:7897; export all_proxy=socks5://127.0.0.1:7897; echo "Proxy turned ON"'
alias proxyoff='unset http_proxy; unset https_proxy; unset all_proxy; echo "Proxy turned OFF"'
```

`proxyon` / `proxyoff` alias 保留，用于临时切换。

### 验证

```bash
source ~/.bashrc
echo "https_proxy=$https_proxy"
curl -s https://chatgpt.com -o /dev/null -w "HTTP status: %{http_code}\n"
```

### 正式 runbook

完整步骤已沉淀至：`docs/runbooks/hermes-codex-proxy-setup.md`

到 2026-04-24 为止，统一恢复入口已升级为：
- `docs/runbooks/hermes-codex-runtime-recovery.md`
- `scripts/hermes_codex_runtime_recovery.py`

## 后续动作建议

下一次遇到同类问题时，优先按下面顺序排查：

1. 确认当前是否在 `tun mode`
2. `echo $https_proxy` 检查代理变量是否存在
3. 如果为空，执行 `source ~/.bashrc` 或检查 profile 是否正确加载
4. 测试 `curl -s https://chatgpt.com -o /dev/null -w "%{http_code}\n"`
5. 查看 `~/.hermes/logs/errors.log`
6. 查看 `~/.codex/history.jsonl`
7. 确认 `~/.hermes/config.yaml` 的 `delegation.model / reasoning_effort / max_iterations`
8. 确认本机 live Hermes 是否已包含 Codex timeout 修复
9. 参考 `docs/runbooks/hermes-codex-proxy-setup.md` 完整排障流程
