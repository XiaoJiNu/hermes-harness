# Runbook: Hermes + Codex Runtime Recovery

日期：2026-04-24

## 目的

把“本机 Hermes 使用 Codex 又出现 bug”升级成一个正式的 harness 恢复入口。

以后遇到下面这类问题时，不要先翻聊天记录，优先执行本 runbook：
- `APITimeoutError`
- `APIConnectionError`
- `No response from provider for 300s`
- `Request timed out.`
- subagent 默认继承 `gpt-5.4 high`，上下文膨胀后变慢或卡死
- 电脑重启后 Hermes / Codex 再次不可用

## 恢复入口

默认入口不是手动排查，而是先运行仓库内脚本：

```bash
python3 scripts/hermes_codex_runtime_recovery.py --json
```

这条命令用于：
1. 检查当前 shell 是否有代理变量
2. 检查 `~/.hermes/config.yaml` 的 delegation 稳定性设置
3. 检查 live Hermes import path
4. 检查 Hermes source repo 是否包含 Codex timeout 修复

## 一键 apply 路径

如果你已经确认代理端口，推荐直接走 apply：

```bash
python3 scripts/hermes_codex_runtime_recovery.py \
  --apply \
  --apply-profile \
  --proxy-port 7897 \
  --repoint-live-install \
  --smoke-test
```

说明：
- `--apply`：把 subagent 稳定配置写入 `~/.hermes/config.yaml`
- `--apply-profile`：把代理 export block 写入 shell profile
- `--proxy-port`：用于生成 `HTTP_PROXY / HTTPS_PROXY / ALL_PROXY`
- `--repoint-live-install`：把 live Hermes 对齐到目标 source repo
- `--smoke-test`：执行最小 `hermes chat` 冒烟

如果你本机不是 `7897`，把它替换成真实系统代理端口。

## 脚本会做什么

### 1. 诊断 delegation 是否处于脆弱配置

稳定推荐值固定为：

```text
delegation.model = gpt-5.4-mini
delegation.reasoning_effort = low
delegation.max_iterations = 24
```

原因：
- 不让 subagent 默认继承主代理的 `gpt-5.4 high`
- 减少长任务把子代理上下文推到数万 tokens
- 降低弱链路下的长等待和重试放大

### 2. 诊断代理配置是否只在 GUI 层存在

脚本会先看当前进程环境中的：
- `HTTP_PROXY`
- `HTTPS_PROXY`
- `ALL_PROXY`

如果 shell 里没有这些变量，就说明“系统代理开着，但命令行没继承”。

### 3. 诊断 live install 与源码是否对齐

脚本会检查：
- `hermes` 二进制路径
- live venv 中 `hermes_cli` / `hermes_constants` 的 import path
- Hermes source repo 中是否包含 Codex timeout 修复

### 4. 在需要时自动写入 profile block

脚本写入的 block 是带 marker 的，后续重复执行会覆盖更新，而不是不断追加重复内容。

## 推荐恢复顺序

1. 先跑：

```bash
python3 scripts/hermes_codex_runtime_recovery.py --json
```

2. 如果输出里有 `proxy_env` 或 `delegation_settings` 的 `warn`，执行 apply：

```bash
python3 scripts/hermes_codex_runtime_recovery.py \
  --apply \
  --apply-profile \
  --proxy-port 7897
```

3. 如果输出里 `codex_timeout_fix` 或 `live_import` 有问题，再补：

```bash
python3 scripts/hermes_codex_runtime_recovery.py \
  --repoint-live-install \
  --smoke-test
```

## 何时回到 proxy runbook

如果问题明确来自：
- `tun mode`
- 重启后 profile 没加载
- 代理端口不确定

再去看：
- `docs/runbooks/hermes-codex-proxy-setup.md`

也就是说：
- `hermes-codex-runtime-recovery.md` 是统一恢复入口
- `hermes-codex-proxy-setup.md` 是其中一个专项子手册

## 何时回到 audit

如果你需要理解为什么会这样，而不是只恢复现场，再看：
- `docs/audits/2026-04-15-hermes-codex-tun-instability.md`

audit 负责解释背景；
recovery runbook 负责指导未来重复执行。

## 对未来 agent 的要求

未来如果用户描述：
- “Hermes 使用 Codex 又 timeout 了”
- “subagent 卡住”
- “电脑重启后 Hermes 不能用”
- “No response from provider for 300s”

默认行为应为：
1. 先搜索本仓库里的 `hermes codex runtime recovery`
2. 先运行 `python3 scripts/hermes_codex_runtime_recovery.py --json`
3. 再根据输出决定是否执行 `--apply` / `--apply-profile` / `--repoint-live-install` / `--smoke-test`

不要直接重复从零排查。

## 验证

- `python3 scripts/check_control_plane.py`
- `python3 -m pytest tests/structure -q`
- `python3 -m pytest tests/test_hermes_codex_runtime_recovery.py -q`
