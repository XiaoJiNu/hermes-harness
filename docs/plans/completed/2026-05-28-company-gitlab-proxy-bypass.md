# 公司 GitLab 代理绕过方法记录 Plan

日期：2026-05-28
状态：completed

## 背景

为修复 Hermes / Codex 本地代理配置导致公司内网 GitLab clone 失败的问题，确认根因是 shell 中的
`HTTP_PROXY` / `HTTPS_PROXY` / `ALL_PROXY` 会让 `git clone http://192.168.15.143/...`
错误走 `127.0.0.1:7890` 本地代理，而原 `NO_PROXY` 只包含 localhost。

SSH clone 的 `192.168.15.143:22` timeout 属于当前网络或 GitLab SSH 端口可达性问题；HTTP clone 的
`Failed to connect to 127.0.0.1 port 7890` 属于内网地址未绕过代理的问题。

## 本批次目标

1. 记录公司内网 GitLab 必须绕过 Hermes / Codex 本地代理的方法。
2. 更新自动化恢复脚本，避免后续运行脚本时覆盖回不完整的 `NO_PROXY`。
3. 保留 Hermes / Codex 访问外网所需代理，不通过删除代理变量解决 Git 问题。
4. 增加测试，确保默认 `NO_PROXY` 包含公司 GitLab 地址。

## 已完成变更面

- `scripts/hermes_codex_runtime_recovery.py`
- `tests/test_hermes_codex_runtime_recovery.py`
- `docs/runbooks/hermes-codex-proxy-setup.md`
- `docs/runbooks/hermes-codex-runtime-recovery.md`
- 用户本机 `~/.bashrc` 的 `# >>> Hermes Codex Recovery >>>` 托管块
- 用户本机 `~/.gitconfig` 的 `http://192.168.15.143` / `https://192.168.15.143` 空代理覆盖

## 方法结论

- 不要删除 `HTTP_PROXY` / `HTTPS_PROXY` / `ALL_PROXY`，这些是 Hermes / Codex 访问外网所需配置。
- 将公司 GitLab 和常见 RFC1918 内网段加入 `NO_PROXY` / `no_proxy`：
  - `192.168.15.143`
  - `192.168.15.0/24`
  - `192.168.0.0/16`
  - `10.0.0.0/8`
  - `172.16.0.0/12`
- 对 Git 再加一层 per-host 空代理覆盖，可避免当前 shell 未重新加载 profile 时仍走代理：

```bash
git config --global http.http://192.168.15.143.proxy ""
git config --global http.https://192.168.15.143.proxy ""
```

## 验证

- `git ls-remote http://192.168.15.143/lc_zns/open_mow_ros2.git` 在非公司网络下显示直连 `192.168.15.143:80`，不再访问 `127.0.0.1:7890`。
- `hermes chat -Q --provider openai-codex -m gpt-5.5 -q '请只回复：ok'`：通过，返回 `ok`。
- `python3 -m pytest tests/test_hermes_codex_runtime_recovery.py -q`：通过。
- `python3 scripts/check_control_plane.py`：通过。
- `python3 -m pytest tests/structure -q`：通过。
- `make test-structure`：通过。

## Done 定义结果

- 方法已经写入 runbook，而不是只保留在聊天记录中。
- 自动化脚本默认不会再生成缺少内网绕过的 `NO_PROXY`。
- Hermes / Codex 代理配置保留且验证可用。
- 公司网络下下一步只需用户手动连接公司网络后重新执行 HTTP clone 验证。
