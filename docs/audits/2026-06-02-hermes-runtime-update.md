# Hermes runtime update audit

日期：2026-06-02

## 目的

按用户要求把本机 Hermes 更新到最新，同时保护当前 harness 仓库和本地 Hermes source / live install 中已有内容不丢失，并在更新后提交、推送本仓库状态。

本次主要是 runtime update 批次，不是 harness 方法论升级批次。仓库内只做了两类低风险可追溯维护：
1. 记录本次 runtime 更新事实与保护措施。
2. 更新 Hermes + Codex recovery 诊断脚本，使它能识别 Hermes v0.15.1+ 的 raw event stream null-output 修复形态，避免把已修复 runtime 误报为缺失修复。

## 更新前状态

### hermes-harness 仓库

- 路径：`/home/yr/yr/code/harness-engineering-all/hermes-harness`
- 初始状态：`main...origin/main`，工作区 clean
- 执行 `git fetch --all --prune` 后发现本地落后远端 2 commits：
  - `45eaa76 docs: cover Codex null-output recovery`
  - `6bfcaae fix: bypass proxy for company GitLab`
- 处理方式：先 `git merge --ff-only origin/main`，只做 fast-forward，不 reset / clean / checkout 旧内容。

### Hermes runtime/source

- Hermes CLI 更新前：`Hermes Agent v0.14.0 (2026.5.16)`
- 初始更新检查：报告有 update available
- 开发源码树：`/home/yr/yr/code/harness-engineering-all/hermes-agent`
  - 更新前 HEAD：`e2fd462eb`
  - 初始工作区有 2 个本地修改：
    - `agent/codex_runtime.py`
    - `tests/run_agent/test_streaming.py`
  - 修改内容是本地 Codex null-output stream recovery 相关补丁。
- live install 树：`~/.hermes/hermes-agent`
  - 更新前 HEAD：`e2fd462eb`
  - 工作区 clean

## 保护措施

更新前已把 harness、dev source、live install 的状态和 patch 快照保存到：

`~/.hermes/update-backups/hermes-runtime-20260602_092624`

快照包含：

- `harness/status-before.txt`
- `harness/head-before.txt`
- `harness/local-tracked-changes.patch`
- `harness/untracked-before.txt`
- `dev-source/status-before.txt`
- `dev-source/head-before.txt`
- `dev-source/local-changes.patch`
- `dev-source/untracked-before.txt`
- `live-install/status-before.txt`
- `live-install/head-before.txt`
- `live-install/local-changes.patch`
- `live-install/untracked-before.txt`

因为 Hermes dev source 有本地修改，更新前已创建保护 stash：

```text
stash@{0}: On main: pre-hermes-update-20260602_092835
```

该 stash 保留在 `/home/yr/yr/code/harness-engineering-all/hermes-agent`，没有自动删除。更新后的 upstream 已包含更结构化的 raw event stream null-output 修复，因此本次没有把旧本地补丁重新套回 runtime 主线。

## 执行的更新

1. 在 `hermes-harness` 仓库执行 `git fetch --all --prune` 和 `git merge --ff-only origin/main`，先同步远端已有内容。
2. 在 Hermes dev source 里 stash 本地改动后，执行 `git merge --ff-only origin/main`。
3. 在 Hermes live install 里执行 `git merge --ff-only origin/main`。
4. 由于更新过程中远端 main 又前进 1 commit，再次 fast-forward dev source 和 live install 到最新 `origin/main`。
5. 在 dev source 中重新安装 live venv editable package：

```bash
uv pip install --python ~/.hermes/hermes-agent/venv/bin/python -e '.[all]'
```

6. 删除 stale update cache：

```bash
rm -f ~/.hermes/.update_check
```

7. 同步本仓库 recovery 诊断脚本与测试：
   - `scripts/hermes_codex_runtime_recovery.py`
   - `tests/test_hermes_codex_runtime_recovery.py`
   - `docs/runbooks/hermes-codex-runtime-recovery.md`

## 更新后状态

- Hermes CLI：`Hermes Agent v0.15.1 (2026.5.29)`
- `hermes --version`：`Up to date`
- Hermes dev source HEAD：`162c7856c`
  - `HEAD...origin/main = 0/0`
  - 工作区 clean
- Hermes live install HEAD：`162c7856c`
  - `HEAD...origin/main = 0/0`
  - 工作区 clean
- 最新 runtime 关键提交：
  - `162c7856c fix(file-safety): add sandbox-mirror soft guard for writes to per-task .hermes mirrors (#32213)`

## 验证

已运行：

```bash
hermes --version
python3 scripts/hermes_codex_runtime_recovery.py --json
hermes chat -Q -q '请只回复：ok'
python3 -m pytest tests/test_hermes_codex_runtime_recovery.py -q
~/.hermes/hermes-agent/venv/bin/python -m pytest tests/run_agent/test_streaming.py -q -o addopts=''
python3 scripts/check_control_plane.py
python3 -m pytest tests/structure -q
make test-structure
python3 scripts/check_method_update_sources.py --fetch --json
```

结果：

- `hermes --version` 显示 `Hermes Agent v0.15.1 (2026.5.29)` 且 `Up to date`
- recovery 诊断 `ok: true`
- `codex_timeout_fix: ok`
- `codex_null_output_fix: ok`
- smoke test 返回 `ok`
- recovery 脚本测试：`8 passed`
- Hermes runtime streaming 测试：`36 passed, 1 warning`
- control plane 检查：`PASS: control plane checks succeeded`
- structure 测试：`9 passed`
- `make test-structure`：通过
- method update source 检查：Hermes dev source 与 live CLI 已最新；harness 仓库只有本次待提交改动

说明：曾用系统 Python 直接运行 Hermes runtime streaming 测试，因该解释器缺少 `openai` 依赖失败；随后按 live Hermes venv 重新运行同一测试并通过。

## 备注

本次没有执行 destructive git 操作，没有 reset、clean 或强制 checkout。所有更新均通过 fast-forward merge 完成；已有本地 Hermes dev source 改动同时保存在 patch 快照和 stash 中。
