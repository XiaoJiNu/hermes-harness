# Runbook：Hermes + Codex 代理配置（system proxy 模式）

日期：2026-04-15

## 适用场景

- VPN 客户端已切换为 **system proxy / global mode**（非 tun mode）
- Hermes / Codex 进程在重启后无法访问网络，报 timeout 或 SSL 错误
- shell 中没有 `HTTP_PROXY` / `HTTPS_PROXY` / `ALL_PROXY` 环境变量
- 即使代理变量已经存在，Codex subagent 仍频繁 timeout 或上下文膨胀

## 根本原因

VPN 客户端在 system proxy 模式下只设置了操作系统级别的代理（GUI 层），
不会自动向 shell 进程注入环境变量。
Hermes / Codex 等命令行进程依赖环境变量感知代理，重启后变量消失，链路断开。

但 2026-04-23 的后续排障又确认：

1. 仅修复代理变量并不能覆盖全部问题
2. `hermes-agent` 的 Codex Responses 流式路径若未带显式 timeout，也会更早暴露 `APITimeoutError`
3. 若 `delegation.*` 为空，subagent 会继承主代理的 `gpt-5.4 high`，长任务更容易变脆

## 一次性修复（写入 shell profile，重启永久生效）

### 第一步：确认代理端口

查看 VPN 客户端的 "系统代理" 设置，记录 HTTP 代理端口。

常见默认值：
- Clash / Clash Verge：`7890`（HTTP）、`7891`（SOCKS5）
- Surge：`6152`
- Shadowrocket：`1087`

### 第二步：写入 shell profile

根据你使用的 shell 选择对应文件（`~/.bashrc` 或 `~/.zshrc`），
在文件末尾追加以下内容（将 `PORT` 替换为实际端口，通常是 `7890`）：

```bash
# Hermes / Codex proxy — system proxy mode
export HTTP_PROXY="http://127.0.0.1:PORT"
export HTTPS_PROXY="http://127.0.0.1:PORT"
export ALL_PROXY="socks5://127.0.0.1:PORT"
export NO_PROXY="localhost,127.0.0.1,::1"
```

示例（本机实际配置，端口 7897）：

```bash
# Proxy — system proxy mode (port 7897), auto-enabled on startup
export http_proxy="http://127.0.0.1:7897"
export https_proxy="http://127.0.0.1:7897"
export all_proxy="socks5://127.0.0.1:7897"
export NO_PROXY="localhost,127.0.0.1,::1"
```

### 第三步：当前 session 立即生效

```bash
source ~/.zshrc   # 或 source ~/.bashrc
```

### 第四步：验证

```bash
echo $HTTPS_PROXY
curl -s https://chatgpt.com -o /dev/null -w "%{http_code}\n"
```

预期：`HTTPS_PROXY` 非空，curl 返回非 403。

## 重启后验证清单

重启后打开终端，依次确认：

1. `echo $HTTPS_PROXY` → 非空
2. VPN 客户端已启动且处于 global / system proxy 模式
3. `curl -s https://chatgpt.com -o /dev/null -w "%{http_code}\n"` → 非 403

如果 `HTTPS_PROXY` 为空，说明 shell profile 没有正确加载，检查：
- 终端是否以 login shell 启动（`bash -l` / `zsh -l`）
- profile 文件路径是否正确（`~/.zshrc` vs `~/.bashrc` vs `~/.profile`）

## 2026-04-23 追加稳定性修复

当代理变量已经存在，但 Hermes + Codex 仍不稳定时，再检查下面两项。

### 1. 确认 live Hermes 已包含 Codex timeout 修复

检查当前全局 `hermes` 是否实际指向本地源码安装：

```bash
head -n 1 ~/.local/bin/hermes
source ~/.hermes/hermes-agent/venv/bin/activate
python -c "import hermes_cli, hermes_constants, inspect; print(inspect.getfile(hermes_cli)); print(inspect.getfile(hermes_constants))"
```

如果 live install 没有指到你正在维护的源码，先 repoint：

```bash
cd ~/yr/code/harness-engineering-all/hermes-agent
bash scripts/repoint_live_install.sh
```

### 2. 给 subagent 单独配一个更稳的默认档位

建议不要让子代理默认继承主代理的 `gpt-5.4 high`。
本机稳定配置可直接设为：

```bash
hermes config set delegation.model gpt-5.4-mini
hermes config set delegation.reasoning_effort low
hermes config set delegation.max_iterations 24
```

这组配置的目的不是替换主模型，而是避免：
- 多个 subagent 同时压到最慢的 Codex 档位
- 长任务把子代理上下文堆到数万 tokens
- 子代理在弱链路上反复超时重试

## 为什么不用 tun mode

| 模式 | 优点 | 缺点 |
|------|------|------|
| tun mode | 全局透明，无需配置 | MTU/分片问题导致长连接/流式请求不稳定，SSL record 错误 |
| system proxy | 应用层显式代理，链路稳定 | 需要手动配置 shell 环境变量 |

对 Hermes + Codex 的流式长连接，system proxy 更可靠。

## 相关文件

- `docs/runbooks/hermes-codex-runtime-recovery.md`：Hermes + Codex 统一恢复入口
- `docs/audits/2026-04-15-hermes-codex-tun-instability.md`：问题背景与诊断
