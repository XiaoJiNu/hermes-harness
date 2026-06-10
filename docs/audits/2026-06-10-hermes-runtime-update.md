# Hermes runtime update audit

日期：2026-06-10

## 目的

按用户要求把本机 Hermes 更新到最新，同时保护 `hermes-harness` 仓库已有内容、本地 Hermes dev source 和 live install 中已有内容不丢失，并在更新后提交、推送本仓库状态。

本次是 runtime update 批次，不是 harness 方法论升级批次。仓库内新增本审计记录；同时保留并准备提交更新前已经存在的 Understand-Anything bootstrap 控制面变更。

## 更新前状态

### hermes-harness 仓库

- 路径：`/home/yr/yr/code/harness-engineering-all/hermes-harness`
- 分支状态：`main...origin/main`
- `HEAD...origin/main = 0/0`
- 更新前已有未提交内容：
  - `README.md`
  - `docs/README.md`
  - `scripts/check_control_plane.py`
  - `tests/structure/test_harness_repo.py`
  - `docs/runbooks/understand-anything-hermes-bootstrap.md`
  - `scripts/bootstrap_understand_anything.py`

这些内容在本次 runtime 更新前已经存在；本次没有 reset、clean、checkout 或覆盖它们。

### Hermes runtime/source

- Hermes CLI 更新前：`Hermes Agent v0.15.1 (2026.5.29)`
- `hermes --version` 更新前报告：`Update available: 979 commits behind`
- dev source：`/home/yr/yr/code/harness-engineering-all/hermes-agent`
  - 更新前 HEAD：`162c7856ca14078ac0b0b15dcd1e54b2e38b2645`
  - `HEAD...origin/main = 0/981`
  - 工作区有 1 个本地修改：`hermes_cli/auth.py`
  - 修改内容：Codex device-code polling 在本地代理空闲连接被关闭时，每次 poll 重新创建 `httpx.Client` 并忽略 transient `httpx.HTTPError` 后继续轮询。
- live install：`~/.hermes/hermes-agent`
  - 更新前 HEAD：`162c7856ca14078ac0b0b15dcd1e54b2e38b2645`
  - 工作区 clean；fetch 后同样落后 `origin/main` 981 commits。

## 保护措施

更新前已保存两个快照目录：

- `~/.hermes/update-backups/hermes-harness-20260610_091217`
- `~/.hermes/update-backups/hermes-runtime-20260610_091345`

快照包含各自的：

- `status-before.txt`
- `head-before.txt`
- tracked diff patch
- untracked file list
- 如有 untracked 文件，还包含 untracked tarball

因为 dev source 有本地修改，更新前曾创建临时保护 stash：

```text
pre-hermes-update-20260610_091440
```

更新后发现 upstream 最新 `ab5f1a1f1` 仍未包含这段本地代理 polling 修复，因此把该修复重新套回 dev source 和 live install。确认修复已在工作区保留后，已删除本次临时 stash，避免把本次保护副本留成隐藏状态；旧的历史 stash 没有改动。

## 执行的更新

1. 在 `hermes-harness` 中执行 `git fetch --all --prune`，确认本仓库与 `origin/main` 一致但工作区有既有未提交内容。
2. 在 dev source 中保存保护 stash 后执行：

```bash
git merge --ff-only origin/main
```

3. 在 live install 中执行同样的 fast-forward merge。
4. 在 dev source 中重新安装 live venv editable package：

```bash
uv pip install --python ~/.hermes/hermes-agent/venv/bin/python -e '.[all]'
```

5. 删除 stale update cache：

```bash
rm -f ~/.hermes/.update_check ~/.hermes/update_check
```

6. 重新套回 `hermes_cli/auth.py` 的本地 Codex device-code polling 代理兼容修复，并同步到 dev source 与 live install。
7. `check_method_update_sources.py --fetch` 发现 upstream 又前进 1 commit 后，再次在 dev source 和 live install 中 stash 本地 polling 修复、fast-forward 到 `258d24039`、pop 回本地修复，并重新执行 editable reinstall。

## 更新后状态

- Hermes CLI：`Hermes Agent v0.16.0 (2026.6.5) · upstream 258d2403`
- `hermes --version`：`Up to date`
- dev source HEAD：`258d24039fe5edc7f90ff7580562f966c4702c22`
  - `HEAD...origin/main = 0/0`
  - 工作区保留 1 个本地修改：`hermes_cli/auth.py`
- live install HEAD：`258d24039fe5edc7f90ff7580562f966c4702c22`
  - `HEAD...origin/main = 0/0`
  - 工作区保留 1 个本地修改：`hermes_cli/auth.py`
- 本地 runtime patch diffstat：`hermes_cli/auth.py | 42 ++++++++++++++++++++++++------------------`

说明：这两个 Hermes source tree 已 fast-forward 到最新 upstream main；保留的 `hermes_cli/auth.py` 修改是更新前已有的本机代理兼容修复，为满足“不丢失以前内容”的要求没有丢弃。

## 验证

已运行：

```bash
~/.hermes/hermes-agent/venv/bin/python -m py_compile hermes_cli/auth.py
hermes --version
python3 scripts/hermes_codex_runtime_recovery.py --json
hermes chat -Q -q '请只回复：ok'
python3 -m py_compile scripts/bootstrap_understand_anything.py
python3 scripts/bootstrap_understand_anything.py --dry-run --skip-build
python3 scripts/check_control_plane.py
python3 -m pytest tests/structure -q
make test-structure
python3 scripts/check_method_update_sources.py --fetch --json
```

结果：

- `hermes --version` 显示 `Hermes Agent v0.16.0 (2026.6.5) · upstream 258d2403` 且 `Up to date`
- runtime `py_compile` 通过
- recovery 诊断 `ok: true`
- Hermes smoke test 返回 `ok`
- Understand-Anything bootstrap 脚本 `py_compile` 通过，`--dry-run --skip-build` 成功
- `python3 scripts/check_control_plane.py`：`PASS: control plane checks succeeded`
- `python3 -m pytest tests/structure -q`：`10 passed`
- `make test-structure`：通过，内部结构测试同样 `10 passed`
- method update source 检查：harness repo 只有本次待提交改动；Hermes dev source 与 CLI 均最新；唯一 runtime dirty path 是已说明的 `hermes_cli/auth.py` 本地 polling 修复
- recovery 诊断仍提示非阻塞 warning：Codex base_url unset，delegation settings 不是该脚本推荐的稳定值；这些 warning 与本次 runtime 更新成功与否无关，本次未擅自改动用户模型配置。

## 备注

本次没有执行 destructive git 操作，没有 reset、clean、force checkout 或强制推送。Hermes runtime 更新采用可审计的 fast-forward merge + editable reinstall；harness 仓库更新采用普通提交和推送。
