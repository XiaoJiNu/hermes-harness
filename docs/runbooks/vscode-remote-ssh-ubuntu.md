# Runbook：VSCode Remote-SSH 连接 Ubuntu 远程笔记本运行代码

日期：2026-05-26

## 目标

用当前 Ubuntu 24.04 笔记本作为开发控制端，只运行 VSCode UI；用另一台 Ubuntu 20.04 笔记本作为远程执行端，实际承载代码目录、依赖环境、终端、调试器和运行进程。

标准链路：

```text
Ubuntu 24.04 当前电脑
  VSCode + Remote-SSH extension + SSH client + private key
        |
        | ssh
        v
Ubuntu 20.04 远程电脑
  openssh-server + project files + runtime/env + VSCode Server
```

## 适用场景

- 两台机器在同一局域网，或能通过 VPN / Tailscale / WireGuard / ZeroTier 互通。
- 希望在当前电脑上写代码、看文件、调试，但所有命令都在另一台电脑上执行。
- 远程电脑上有更合适的 CPU / GPU / 数据 / 依赖环境。

不建议的默认方案：
- 不建议把远程 22 端口直接暴露到公网。
- 不建议用 SSHFS 挂载远程目录后在本地 VSCode 里直接编辑，除非只是临时查看文件。
- 不建议把私钥、真实公网 IP、个人用户名写进共享仓库。

## 推荐决策

1. 默认使用 VSCode Remote-SSH。
2. 代码、数据、虚拟环境和运行进程都放在远程 Ubuntu 20.04 电脑上。
3. 当前 Ubuntu 24.04 电脑只保存 SSH 私钥和 `~/.ssh/config` host alias。
4. 同一局域网内优先用路由器 DHCP reservation 或 `<hostname>.local` 固定目标。
5. 跨网络优先用 Tailscale / WireGuard / ZeroTier，不直接开放公网 SSH。
6. 项目文档只记录 host alias，例如 `ubuntu20-dev`，不要记录个人私钥或公网敏感信息。

## 一次性搭建步骤

### 1. 在远程 Ubuntu 20.04 电脑上启用 SSH 服务

在远程电脑本机终端执行：

```bash
sudo apt update
sudo apt install -y openssh-server git curl tar gzip ca-certificates
sudo systemctl enable --now ssh
systemctl status ssh --no-pager
hostname -I
```

记录远程电脑的用户名和 IP，例如：

```text
remote user: yr
remote ip:   192.168.1.23
```

如果远程电脑启用了 UFW 防火墙，优先只允许当前电脑的局域网 IP 访问 22 端口：

```bash
sudo ufw allow from <当前电脑IP> to any port 22 proto tcp
sudo ufw status verbose
```

如果只是可信局域网内的临时使用，也可以放开 OpenSSH：

```bash
sudo ufw allow OpenSSH
sudo ufw status verbose
```

远程电脑还需要避免睡眠导致 SSH 断开。推荐在 Ubuntu 设置中关闭自动睡眠：

```text
Settings -> Power -> Automatic Suspend -> Off
Settings -> Power -> Blank Screen -> Never 或足够长
```

### 2. 在当前 Ubuntu 24.04 电脑上创建 SSH key

在当前电脑执行：

```bash
ls ~/.ssh/id_ed25519.pub
```

如果文件不存在，创建新的 key：

```bash
ssh-keygen -t ed25519 -C "ubuntu24-to-ubuntu20-vscode"
```

默认保存到：

```text
~/.ssh/id_ed25519
~/.ssh/id_ed25519.pub
```

不要把 `~/.ssh/id_ed25519` 私钥复制到项目仓库或发给别人。

### 3. 把公钥安装到远程 Ubuntu 20.04 电脑

优先使用：

```bash
ssh-copy-id <远程用户名>@<远程IP>
```

示例：

```bash
ssh-copy-id yr@192.168.1.23
```

如果没有 `ssh-copy-id`，用下面的等价命令：

```bash
cat ~/.ssh/id_ed25519.pub | ssh <远程用户名>@<远程IP> \
  'mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys'
```

验证免密登录：

```bash
ssh <远程用户名>@<远程IP> 'hostname; lsb_release -ds; pwd'
```

预期：不再要求输入远程用户密码，能打印远程机器 hostname 和 Ubuntu 版本。

### 4. 在当前电脑配置 `~/.ssh/config`

编辑当前电脑的 `~/.ssh/config`：

```bash
mkdir -p ~/.ssh
chmod 700 ~/.ssh
nano ~/.ssh/config
```

加入 host alias：

```sshconfig
Host ubuntu20-dev
    HostName <远程IP或远程hostname>
    User <远程用户名>
    Port 22
    IdentityFile ~/.ssh/id_ed25519
    IdentitiesOnly yes
    ServerAliveInterval 30
    ServerAliveCountMax 4
    ForwardAgent no
```

示例：

```sshconfig
Host ubuntu20-dev
    HostName 192.168.1.23
    User yr
    Port 22
    IdentityFile ~/.ssh/id_ed25519
    IdentitiesOnly yes
    ServerAliveInterval 30
    ServerAliveCountMax 4
    ForwardAgent no
```

修正权限并测试：

```bash
chmod 600 ~/.ssh/config
ssh ubuntu20-dev 'hostname; uname -a; lsb_release -ds'
```

如果远程电脑 IP 经常变化，优先选择下面三种方式之一：

1. 在路由器上给远程电脑设置 DHCP reservation。
2. 在远程电脑安装并启用 Avahi，然后用 `<hostname>.local`：
   ```bash
   sudo apt install -y avahi-daemon
   hostnamectl
   ```
3. 跨网络时使用 Tailscale / WireGuard / ZeroTier 分配的稳定 VPN IP 或 DNS 名称。

### 5. 在 VSCode 中连接远程电脑

在当前 Ubuntu 24.04 电脑上：

1. 安装 VSCode。
2. 安装扩展：`Remote - SSH`（extension id: `ms-vscode-remote.remote-ssh`）。
3. 打开 Command Palette：`Ctrl+Shift+P`。
4. 执行：`Remote-SSH: Connect to Host...`。
5. 选择：`ubuntu20-dev`。
6. 第一次连接时选择远程平台：`Linux`。
7. VSCode 会自动在远程电脑安装 VSCode Server，默认位置类似：
   ```text
   ~/.vscode-server/
   ```
8. 连接成功后选择：`Open Folder`，打开远程电脑上的项目目录，例如：
   ```text
   /home/yr/yr/code/my-project
   ```

注意：此时 VSCode 左下角应显示 SSH 远程窗口标识，集成终端里执行的命令都在远程 Ubuntu 20.04 电脑上运行。

## 项目代码与环境管理

### 推荐方式：代码直接在远程电脑上

在 VSCode Remote-SSH 窗口的远程终端中执行：

```bash
mkdir -p ~/yr/code
cd ~/yr/code
git clone <repo-url>
cd <repo-name>
```

然后在远程电脑上创建项目环境：

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -r requirements.txt
```

如果项目使用 Conda / Mamba / uv / Poetry，也应在远程电脑上创建环境。当前电脑的 Python、CUDA、系统包不会自动参与远程运行。

### 数据和结果同步

源代码优先用 Git 同步；大数据、模型权重、运行结果用 `rsync`：

```bash
# 当前电脑 -> 远程电脑
rsync -avP ./data/ ubuntu20-dev:~/data/my-project/

# 远程电脑 -> 当前电脑
rsync -avP ubuntu20-dev:~/runs/my-project/ ./runs-from-ubuntu20/
```

如果远程电脑有 GPU，在远程终端验证：

```bash
nvidia-smi
python3 - <<'PY'
try:
    import torch
    print('torch:', torch.__version__)
    print('cuda:', torch.cuda.is_available())
except Exception as exc:
    print(type(exc).__name__, exc)
PY
```

## 安全加固

先确认 key 登录已经成功，并且保留一个已登录的 SSH session 不要关闭，再做加固。

远程 Ubuntu 20.04 上检查 SSH 配置语法：

```bash
sudo sshd -t
```

确认无误后，可在 `/etc/ssh/sshd_config` 或 `/etc/ssh/sshd_config.d/*.conf` 中设置：

```sshconfig
PubkeyAuthentication yes
PasswordAuthentication no
PermitRootLogin no
```

然后执行：

```bash
sudo sshd -t
sudo systemctl reload ssh
```

在另一个当前电脑终端重新测试：

```bash
ssh ubuntu20-dev 'whoami; hostname'
```

安全原则：

- 能用局域网 / VPN 就不要暴露公网 22 端口。
- 如果必须跨公网访问，至少使用 key 登录、防火墙白名单、非 root 用户、`PermitRootLogin no`、`fail2ban`，并考虑更换端口。
- 丢失当前电脑或怀疑私钥泄露时，立即到远程电脑删除对应 `~/.ssh/authorized_keys` 行。

## 验证清单

在当前电脑终端验证 SSH：

```bash
ssh ubuntu20-dev 'hostname; lsb_release -ds; pwd'
```

在 VSCode Remote-SSH 窗口的集成终端验证远程运行位置：

```bash
hostname
pwd
whoami
python3 -V
which python3
```

如果需要 GPU：

```bash
nvidia-smi
```

检查 VSCode Server 是否已安装到远程电脑：

```bash
ssh ubuntu20-dev 'test -d ~/.vscode-server && du -sh ~/.vscode-server || true'
```

一次连接只有满足下面条件才算成功：

1. `ssh ubuntu20-dev` 能免密登录。
2. VSCode 能通过 `Remote-SSH: Connect to Host...` 打开 `ubuntu20-dev`。
3. VSCode 集成终端显示的是远程电脑 hostname。
4. 项目依赖安装在远程电脑上。
5. 运行代码时 CPU / GPU / 文件路径都来自远程电脑。

## 常见问题排查

### `Connection refused`

远程 SSH 服务未启动、IP 错误或防火墙拦截。

远程电脑执行：

```bash
sudo systemctl status ssh --no-pager
sudo systemctl enable --now ssh
hostname -I
sudo ufw status verbose
```

### `Permission denied (publickey)`

常见原因：公钥没装到远程用户、用户名写错、私钥路径不对、权限不正确。

当前电脑执行：

```bash
ssh -v ubuntu20-dev
chmod 700 ~/.ssh
chmod 600 ~/.ssh/config ~/.ssh/id_ed25519
```

远程电脑检查：

```bash
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```

### VSCode 一直卡在 installing VSCode Server

常见原因：远程磁盘满、`tar` / `gzip` 缺失、网络中断、旧 server 目录损坏。

远程电脑执行：

```bash
df -h
sudo apt install -y tar gzip
rm -rf ~/.vscode-server/bin/*
```

然后从 VSCode 重新连接。

### VSCode 连接失败但普通 `ssh ubuntu20-dev` 正常

在 VSCode 中打开：

```text
View -> Output -> Remote - SSH
```

检查具体错误。常用修复：

```bash
ssh ubuntu20-dev 'rm -rf ~/.vscode-server/bin/*'
```

然后重连。

### IP 经常变化

优先顺序：

1. 路由器 DHCP reservation。
2. `<hostname>.local` + Avahi。
3. Tailscale / WireGuard / ZeroTier 的固定 VPN IP 或 DNS。

不要把经常变化的裸 IP 写进项目文档；项目文档只写 `ubuntu20-dev` 这样的 host alias。

### 远程电脑睡眠后断开

关闭远程 Ubuntu 20.04 的自动睡眠；必要时接电源、合盖不睡眠。远程开发机器应被当作短期 workstation / server 使用。

## 在未来项目中的使用方式

当某个项目需要远程开发时，按这个模板落地：

1. 在当前电脑 `~/.ssh/config` 建立项目无关 host alias，例如 `ubuntu20-dev`。
2. 在项目自己的 `docs/runbooks/remote-development.md` 只记录：
   - 使用哪个 host alias
   - 远程项目路径
   - 远程 Python / Conda / CUDA / Docker 环境
   - 验证命令
   - 数据同步规则
3. 不把私钥、个人 token、真实公网 IP 或临时密码写入项目仓库。
4. 如果项目由 harness 管理，把远程开发验证加入项目的 runbook 或 README，而不是依赖聊天记忆。

## 最小可复制模板

当前电脑 `~/.ssh/config`：

```sshconfig
Host ubuntu20-dev
    HostName <远程IP或VPN名称>
    User <远程用户名>
    Port 22
    IdentityFile ~/.ssh/id_ed25519
    IdentitiesOnly yes
    ServerAliveInterval 30
    ServerAliveCountMax 4
    ForwardAgent no
```

最小验证命令：

```bash
ssh ubuntu20-dev 'hostname; lsb_release -ds; pwd'
```

VSCode 操作：

```text
Ctrl+Shift+P
Remote-SSH: Connect to Host...
ubuntu20-dev
Open Folder -> 选择远程项目目录
```
