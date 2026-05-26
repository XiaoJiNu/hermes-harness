# VSCode Remote SSH Ubuntu 双机开发 Runbook Plan

日期：2026-05-26
状态：completed

## 背景

用户有两台 Ubuntu 笔记本：
- 当前工作机：Ubuntu 24.04，运行 VSCode UI 与 SSH client
- 远程执行机：Ubuntu 20.04，承载代码、环境、终端、调试与运行进程

用户希望以后统一按同一方案，用当前电脑的 VSCode 远程连接另一台电脑并在远程机器上运行代码。

## 本批次目标

1. 新增一份可复用 runbook，定义 Ubuntu 24.04 -> Ubuntu 20.04 的 VSCode Remote-SSH 标准方案。
2. 把 runbook 链接到仓库入口与 docs 索引，避免方案只停留在聊天记录里。
3. 更新结构检查，把该 runbook 作为长期可发现的仓库工件。
4. 运行控制面验证。

## 已完成变更面

- `docs/runbooks/vscode-remote-ssh-ubuntu.md`
- `docs/README.md`
- `README.md`
- `scripts/check_control_plane.py`
- `tests/structure/test_harness_repo.py`

## 验证

- `python3 -m pytest tests/structure/test_harness_repo.py::test_vscode_remote_ssh_ubuntu_runbook_is_actionable -q`：通过
- `python3 scripts/check_control_plane.py`：通过
- `python3 -m pytest tests/structure -q`：通过
- `make test-structure`：通过

## Done 定义结果

- runbook 覆盖远程机 SSH 服务、密钥、`~/.ssh/config`、VSCode Remote-SSH、项目环境、验证、安全与排障。
- docs 索引和根 README 都能找到该 runbook。
- 结构检查通过。
