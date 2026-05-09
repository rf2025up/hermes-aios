# INFRA.md - 技术基础设施参考文档

> 本文档集中管理所有技术基础设施信息，MEMORY.md 只保留引用。

## 1. VPS (Hermes)

### 基本信息
- **IP:** 74.48.186.223
- **SSH端口:** 2222（不是22！）
- **用户:** root
- **密码:** Login666
- **控制面板:** https://nerdvm.racknerd.com/ (vmuser278504 / Iaixuexi666)
- **规格:** 2.5GB KVM, 2核, Debian 12, 43GB磁盘

### SSH连接
```bash
# 从笔记本/Mac连接
ssh -i ~/.ssh/id_ed25519 -p 2222 root@74.48.186.223

# 远程执行Hermes命令
ssh -i ~/.ssh/id_ed25519 -p 2222 root@74.48.186.223 "export PATH=/root/.local/bin:\$PATH && hermes <command>"
```

### Hermes配置
- **主目录:** /root/.hermes/hermes-agent
- **命令位置:** /root/.local/bin/hermes
- **版本:** v0.9.0 (2026.4.13)
- **AI-OS同步:** /root/aios
- **飞书App ID:** cli_a95762ce28b81bb4

### VPS关键路径
```
FRP目录:        /root/frp
Hermes日志:      /root/.hermes/logs
AI-OS同步:      /root/aios
```

## 2. Windows 主机（OpenClaw 主Agent）

### 基本信息
- **主机名:** WIN-RBARICJ02HS
- **Tailscale IP:** 100.68.184.107
- **局域网 IP:** 192.168.1.103
- **用户:** Administrator
- **系统:** Windows, 32GB RAM
- **Node.js:** v24.11.0

### 连接方式
- SSH via Tailscale: `ssh Administrator@100.68.184.107`（已配公钥）

### 软件环境
- **OpenClaw:** 主Agent（锋哥/Star/贾维斯/小园老师等）
- **Gateway端口:** 18789
- **代理:** Clash/mihomo 127.0.0.1:6789

### 关键路径
- OpenClaw配置: `C:\Users\Administrator\.openclaw\`
- Workspace: `C:\Users\Administrator\.openclaw\workspace\`
- Python: `C:\Python314\python.exe`
- SSH公钥: `C:\ProgramData\ssh\administrators_authorized_keys`
- MemOS DB: `C:\Users\Administrator\.openclaw\memos-local\memos.db`
- MemOS Viewer: `http://100.68.184.107:18799`

### 计划任务
- **OpenClaw Gateway:** 系统启动时自动运行，72h超时，崩溃后不会自动重启

## 3. Lenovo 笔记本（Linux）

### 基本信息
- **Tailscale IP:** 100.118.178.110
- **用户:** rf
- **系统:** Ubuntu 24.04, Linux 6.17.0-22-generic
- **主机名:** rf-Lenovo
- **SSH:** ✅ 已连通（2026-04-28）

## 3. FRP隧道

### 配置
- **VPS服务端:** 74.48.186.223:7000, token: openclaw_frp_2026
- **笔记本客户端:** ~/frp/frpc.toml, 转发 18789端口
- **用途:** VPS → 笔记本OpenClaw Gateway

### 客户端配置 (~/frp/frpc.toml)
```toml
serverAddr = "74.48.186.223"
serverPort = 7000
[auth]
token = "openclaw_frp_2026"
[[proxies]]
name = "openclaw-gateway"
type = "tcp"
localIP = "127.0.0.1"
localPort = 18789
remotePort = 18789
```

### 服务端配置 (/root/frp/frps.toml)
```toml
bindPort = 7000
[auth]
token = "openclaw_frp_2026"
webServer.addr = "0.0.0.0"
webServer.port = 7500
[[sshProxy]]
name = "ssh"
bindPort = 6000
```

## 4. 消息通道

### 飞书
- **插件:** openclaw-lark (bundled)
- **连接模式:** WebSocket
- **App ID:** cli_a95762ce28b81bb4
- **状态:** ✅ 已通

### 微信
- **插件:** @tencent-weixin/openclaw-weixin (v2.1.8)
- **机制:** iLink Bot QR扫码登录
- **状态:** ✅ 已通（私聊）

## 5. Systemd服务（开机自启）

```bash
# 查看状态
systemctl --user status openclaw-gateway.service frpc.service

# 管理
systemctl --user start/stop/restart openclaw-gateway
systemctl --user start/stop/restart frpc

# 日志
journalctl --user -u openclaw-gateway -f
journalctl --user -u frpc -f
```

## 6. Mac端

- 通过SSH连接VPS和笔记本
- SSH密钥: ~/.ssh/id_ed25519
- 文档同步: ~/Documents/openclaw/OpenClaw-Brain/imports/

## 7. 关键文档索引

```
~/Documents/openclaw/OpenClaw-Brain/
├── imports/
│   ├── 多端同步网络基础设置_综合配置文档_20260416.md
│   ├── VPS_Hermes连接与控制指南_20260416.md
│   └── WorkBuddy文档总打包_20260415/
└── reports/
    └── 全景助力方案_v1.md
```
