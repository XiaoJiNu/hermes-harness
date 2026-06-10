# Runbook: Understand-Anything Hermes Bootstrap

日期：2026-06-02

## 目的

在新电脑或新 Hermes profile 上，可重复地把 `git@github.com:Lum1104/Understand-Anything.git` 接入 Hermes，而不是依赖某次会话记忆或某台机器上的 `~/.understand-anything/repo`。

本 runbook 的边界是：Understand-Anything 是 code-reading / source-understanding 的 external method source and runtime adapter；它是有用的外部方法来源，但 is not source of truth for this repository。`hermes-harness` 的 source of truth 仍然是本仓库的 README、AGENTS、docs、runbooks、tests 和 scripts。

## 为什么不 vendor 到本仓库

默认不 vendor Understand-Anything 源码，原因：

1. 本仓库是 harness 方法参考仓库，不是外部插件镜像。
2. 直接复制源码会制造第二个 source of truth：上游更新、本地修改、license notice、依赖锁和测试都会漂移。
3. Understand-Anything 包含 Node / pnpm workspace、dashboard、Claude/Cursor/Copilot/OpenCode 等多 runtime 包装；这些不应污染本仓库的 runtime-agnostic 方法层。
4. 真正需要长期保存的是“如何恢复安装”和“如何验证可用”，不是把外部项目的实现复制进来。

所以采用“不 vendor + 可复现 bootstrap”的方式：本仓库保留安装脚本、验证命令和边界说明；外部代码仍安装到用户级工具目录。

## 标准安装

在本仓库根目录运行：

```bash
python3 scripts/bootstrap_understand_anything.py --update
```

默认行为：

- clone / update `git@github.com:Lum1104/Understand-Anything.git`
- checkout path: `~/.understand-anything/repo`
- universal plugin symlink: `~/.understand-anything-plugin`
- Hermes skills symlink: `~/.hermes/skills/understand-anything`
- run readiness checks:
  - `pnpm install --frozen-lockfile`
  - `pnpm --filter @understand-anything/core build`
  - `pnpm --filter @understand-anything/core test`

如果 SSH 不可用，可改用 HTTPS：

```bash
python3 scripts/bootstrap_understand_anything.py \
  --repo-url https://github.com/Lum1104/Understand-Anything.git \
  --update
```

如果只想恢复 symlink、暂时跳过 Node 构建：

```bash
python3 scripts/bootstrap_understand_anything.py --skip-build
```

如果要跑 build 但跳过测试：

```bash
python3 scripts/bootstrap_understand_anything.py --skip-tests
```

如果要先看会做什么：

```bash
python3 scripts/bootstrap_understand_anything.py --dry-run --update
```

## Hermes profile / HERMES_HOME

脚本默认写入 `$HERMES_HOME/skills/understand-anything`；如果未设置 `HERMES_HOME`，则使用 `~/.hermes/skills/understand-anything`。

为特定 profile 安装时显式传入：

```bash
python3 scripts/bootstrap_understand_anything.py \
  --hermes-home ~/.hermes/profiles/<profile-name> \
  --update
```

## 版本固定

如果需要在一台新机器上复现某个已验证版本，先在旧机器记录：

```bash
git -C ~/.understand-anything/repo rev-parse HEAD
```

然后在新机器安装指定 commit：

```bash
python3 scripts/bootstrap_understand_anything.py \
  --revision <commit-sha> \
  --update
```

如果使用 `--revision`，脚本会在 clone/fetch 后执行 `git checkout <commit-sha>`。

## 验证

安装后开启新的 Hermes 会话，或者重启 CLI / gateway。然后验证：

```bash
ls -ld ~/.understand-anything/repo
ls -ld ~/.understand-anything-plugin
ls -ld ~/.hermes/skills/understand-anything
hermes skills list | grep -i understand
```

外部仓库内部 readiness 检查：

```bash
cd ~/.understand-anything/repo
pnpm install --frozen-lockfile
pnpm --filter @understand-anything/core build
pnpm --filter @understand-anything/core test
```

期望 Hermes skills 包含：

- `understand`
- `understand-chat`
- `understand-dashboard`
- `understand-diff`
- `understand-domain`
- `understand-explain`
- `understand-knowledge`
- `understand-onboard`

## 后续代码阅读默认规则

非平凡 code-reading / source-understanding 任务默认加载本机 Hermes skill：

```text
understand-anything-code-reading
```

然后按任务类型加载 Understand-Anything upstream skills：

- whole repo / architecture: `understand`
- graph-backed question answering: `understand-chat`
- specific file / function / module: `understand-explain`
- local diff / PR blast radius: `understand-diff`
- graph visualization: `understand-dashboard`

注意：graph-backed output 是定位和理解辅助；高风险结论仍必须回读源文件、测试、配置和 CI。

## 更新

更新到上游最新版本：

```bash
python3 scripts/bootstrap_understand_anything.py --update
```

如果 checkout 有本地未提交修改，脚本默认拒绝更新。先处理本地修改，或者明确使用：

```bash
python3 scripts/bootstrap_understand_anything.py --update --allow-dirty
```

## 回滚 / 卸载

只移除 Hermes 接入，不删除外部 checkout：

```bash
rm -f ~/.hermes/skills/understand-anything
rm -f ~/.understand-anything-plugin
```

完全删除外部 checkout：

```bash
rm -rf ~/.understand-anything/repo
```

如果是特定 profile，替换为对应 profile 的 `skills/understand-anything` 路径。

## 本仓库变更验证

维护本 runbook 或 bootstrap 脚本后运行：

```bash
python3 scripts/check_control_plane.py
python3 -m pytest tests/structure -q
make test-structure
```

如果修改了脚本行为，至少额外运行：

```bash
python3 scripts/bootstrap_understand_anything.py --dry-run --skip-build
```
