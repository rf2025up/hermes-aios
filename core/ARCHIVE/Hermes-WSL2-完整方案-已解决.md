# Hermes Gateway 进程保活 + Fallback 方案 — 完整配置总览

**最后更新**: 2026-05-05 23:45

---

## 背景

Hermes Gateway 从 Windows 原生迁移到 WSL2 (Ubuntu-22.04) 后，面临两个核心问题：
1. **进程保活** — WSL2 实例在无活跃连接时会自动关闭，Gateway 进程被杀
2. **GLM 限流** — Coding Plan 5小时内约80次调用限制，遇到429后无法回复

---

## 配置文件（当前生效）

### config.yaml
```yaml
model:
  provider: zai
  default: glm-5-turbo
  base_url: https://open.bigmodel.cn/api/coding/paas/v4
providers:
  zai:
    model: glm-5-turbo
    base_url: https://open.bigmodel.cn/api/coding/paas/v4
fallback_providers:
  - provider: alibaba
    model: qwen3.6-flash
  - provider: alibaba
    model: deepseek-v4-flash
```

### .env
```
GLM_API_KEY=1146ff2f5e784c6f944d43caaa6e534d.HMEbFg2wmYpl12UW
DASHSCOPE_API_KEY=sk-128088af83f6479faba62f4a93530033
GATEWAY_ALLOW_ALL_USERS=true
FEISHU_APP_ID=cli_a97996259a7a1cd4
FEISHU_APP_SECRET=s0XVpkLqAqrGR7e2g77HGbH4oyAyE8LA
FEISHU_DOMAIN=feishu
FEISHU_CONNECTION_MODE=websocket
FEISHU_GROUP_POLICY=open
TERMINAL_CWD=/root
```

---

## 1️⃣ Fallback 自动切换配置（已生效 ✅）

| 层级 | Provider | 模型 | 触发条件 | 计费 |
|------|----------|------|----------|------|
| **主模型** | `zai` (智谱GLM) | `glm-5-turbo` | 正常使用 | Coding Plan（80次/5小时） |
| **Fallback 1** | `alibaba` (百炼) | `qwen3.6-flash` | GLM 429限流时自动切 | 按token收费，推理能力强 |
| **Fallback 2** | `alibaba` (百炼) | `deepseek-v4-flash` | qwen也失败时再切 | ¥1/百万tokens，最便宜 |

### 自动切换机制（Hermes 原生支持）

- **触发条件**：HTTP 429（限流）、5xx、401/403/404
- **切换方式**：无缝切换，对话历史、工具调用、上下文全部保留
- **每轮恢复**：每个新消息自动尝试主模型 GLM，限流恢复后自动切回
- **飞书手动切**：`/hermes model <provider>/<model>`

### 手动切换命令（飞书对话中发送）

| 场景 | 命令 |
|------|------|
| 切回GLM | `/hermes model zai/glm-5-turbo` |
| 切到Qwen | `/hermes model alibaba/qwen3.6-flash` |
| 切到DeepSeek | `/hermes model alibaba/deepseek-v4-flash` |

---

## 2️⃣ 进程保活方案（已实施 ✅）

### 核心方案：Start-Process 独立启动

**原理**：在 Windows 上用 `Start-Process` 创建独立的 wsl.exe 进程，该进程持有 WSL2 实例，从而让 WSL2 实例保持活跃，Gateway 进程就不会被杀。

```powershell
Start-Process -FilePath wsl.exe -ArgumentList "-d Ubuntu-22.04 -u root -- /root/.hermes/hermes-agent/venv/bin/hermes gateway run --replace" -WindowStyle Hidden
```

**为什么其他方案不行**：
| 方案 | 失败原因 |
|------|----------|
| `nohup` | 只能防 SIGHUP，不防 WSL 实例关闭 |
| `screen` / `tmux` | screen 随 WSL 实例一起被清理 |
| `systemd` | **WSL 内核 5.10.16 不支持 systemd**（需 5.15+） |

### 开机自启（Windows Startup Folder）

**文件位置**: `C:\Users\Administrator\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\hermes_gateway.bat`

```bat
@echo off
:: Hermes Gateway WSL2 Auto-Start
:: 开机自动启动Hermes Gateway（后台静默运行，无窗口弹窗）
powershell -Command "Start-Process -FilePath wsl.exe -ArgumentList '-d Ubuntu-22.04 -u root -- /root/.hermes/hermes-agent/venv/bin/hermes gateway run --replace' -WindowStyle Hidden"
```

**行为**：Windows 每次开机/重启后自动静默启动 Gateway，无窗口弹窗。

### 外部 agent 重启方案

**脚本位置**: `C:\Users\Administrator\hermes_restart.bat`

```bat
@echo off
:: Hermes Gateway Restart (供外部agent通过SSH调用)
wsl -d Ubuntu-22.04 -- systemctl restart hermes-gateway 2>nul || (
    wsl -d Ubuntu-22.04 -u root bash -c "pkill -f 'hermes gateway' 2>/dev/null; sleep 2"
    start /B wsl -d Ubuntu-22.04 -u root -- /root/.hermes/hermes-agent/venv/bin/hermes gateway run --replace
)
```

**外部 agent SSH 调用**（不依赖 SSH 会话）：
```powershell
schtasks /Create /TN "HermesRestartOnce" /TR "C:\Users\Administrator\hermes_restart.bat" /SC ONCE /ST 00:00 /F
schtasks /Run /TN "HermesRestartOnce"
```
计划任务在 Windows 后台运行，执行完后自动清理自身。

---

## 3️⃣ 踩坑记录

| # | 问题 | 根因 | 解法 |
|---|------|------|------|
| 1 | `dashscope` 不是内置 provider | Hermes 不认识 `dashscope` 这个 provider 名 | 改为 `alibaba` + `DASHSCOPE_API_KEY` |
| 2 | systemd 无法启用 | WSL 内核版本 5.10.16，不支持 systemd | 改用 `Start-Process` 方式 |
| 3 | 开机自启后 Gateway 没跑 | startup bat 只写了 `wsl -u root exit`，没启动进程 | 改为 `Start-Process` 启动 wsl+Gateway |
| 4 | `nohup`/`&` 后台进程被杀 | WSL 的 bash 结束时会清理子进程 | 用 Windows 端 `Start-Process` 独立启动 |
| 5 | PowerShell 引号嵌套问题 | `wsl -- bash -c "..."` 与 PowerShell 引号冲突 | 用 Python 脚本或独立的 .sh 文件修改配置 |

---

## 4️⃣ 运维命令速查

| 操作 | 命令 |
|------|------|
| **检查Gateway进程** | `wsl -d Ubuntu-22.04 -u root bash -c "ps aux \| grep hermes \| grep -v grep"` |
| **检查飞书连接** | `wsl -d Ubuntu-22.04 -u root bash -c "tail -5 /root/.hermes/logs/gateway.log"` |
| **查看错误日志** | `wsl -d Ubuntu-22.04 -u root bash -c "cat /root/.hermes/logs/errors.log \| tail -10"` |
| **本机重启 Gateway** | 双击 `C:\Users\Administrator\hermes_restart.bat` |
| **外部 agent 重启** | 见上方 SSH schtasks 命令 |
| **查看配置** | `wsl -d Ubuntu-22.04 -u root bash -c "head -15 /root/.hermes/config.yaml"` |
| **查看环境变量** | `wsl -d Ubuntu-22.04 -u root bash -c "cat /root/.hermes/.env"` |
| **飞书手动切GLM** | `/hermes model zai/glm-5-turbo` |
| **飞书手动切Qwen** | `/hermes model alibaba/qwen3.6-flash` |
| **飞书手动切DeepSeek** | `/hermes model alibaba/deepseek-v4-flash` |

---

## 5️⃣ 关键文件索引

| 文件 | 路径 |
|------|------|
| Hermes 配置 | `/root/.hermes/config.yaml` |
| 环境变量 | `/root/.hermes/.env` |
| Gateway 日志 | `/root/.hermes/logs/gateway.log` |
| 错误日志 | `/root/.hermes/logs/errors.log` |
| Windows 开机自启 | `C:\Users\Administrator\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\hermes_gateway.bat` |
| 外部agent重启脚本 | `C:\Users\Administrator\hermes_restart.bat` |

---

## 6️⃣ 待办（后续可选）

- [ ] 修复 memos-local-plugin — WSL2 内重新 `npm install`，解决 `Exec format error: tsx.cmd` 问题
- [ ] Hermes 版本落后 164 commits — 运行 `hermes update`
- [ ] 清理 Windows 端旧代码：`C:\Users\Administrator\AppData\Local\hermes\`
