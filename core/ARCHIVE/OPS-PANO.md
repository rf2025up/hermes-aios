# 运维全景文档 (OPS-PANO.md)

> **维护方**：Hermes（远程 SSH → Windows VPS）通过 git 维护此文件
> **最后更新**：2026-05-02
> **同步规则**：见底部「同步协议」

---

## 一、当前系统架构

```
┌─────────────────────────────────────────────────────┐
│              校长（手机 / 飞书）                       │
└──────────────────────┬──────────────────────────────┘
                       │ 飞书群/DM
            ┌──────────┴──────────┐
            ▼                     ▼
   ┌─────────────────┐  ┌─────────────────┐
   │  OpenClaw        │  │  Hermes Agent   │
   │  (NSSM服务)      │  │  (NSSM服务)     │
   │  服务名:          │  │  服务名:         │
   │  OpenClawGateway │  │  HermesGateway  │
   │  飞书长连接 ✅    │  │  飞书长连接 ✅    │
   └────────┬────────┘  └────────┬────────┘
            │                    │
            └────────┬───────────┘
                     ▼
        Windows Server (100.68.184.107)
        ┌─────────────────────────┐
        │  NSSM → 崩溃自动重启(10s) │
        │  LocalSystem 运行        │
        └─────────────────────────┘
                     │
              git pull/push
                     ▼
        github.com/rf2025up/aios.git
```

### 角色分工
| 角色 | 位置 | 职责 | 服务名 | 模型 |
|------|------|------|--------|------|
| **OpenClaw** | 本机 Windows VPS | 主中枢，业务对接，万山无阻群协调 | OpenClawGateway | zhipu/GLM-5-Turbo |
| **Hermes** | 本机 Windows VPS | 运维Agent，远程操作、文档管理 | HermesGateway | zai/glm-5-turbo |
| **Hermes远程** | 远程云环境 | 通过SSH操作本机 | — | 同上 |

> ⚠️ **区分规则**：OpenClaw 和 Hermes 同跑一台机器，通过 NSSM 服务名、配置路径、进程名 区分，严禁搞混。

---

## 二、基础设施清单

### 2.1 Windows VPS（唯一服务器）
- **主机名**: WIN-RBARICJ02HS
- **公网IP**: 74.48.186.223
- **Tailscale IP**: 100.68.184.107
- **系统**: Windows Server, 32GB RAM
- **SSH**: `ssh Administrator@100.68.184.107`
- **代理**: Clash 端口 6789

#### OpenClaw 配置
| 项目 | 值 |
|------|------|
| NSSM服务名 | `OpenClawGateway` |
| 启动方式 | bat wrapper: `C:\Users\Administrator\AppData\Roaming\npm\openclaw_svc.bat` |
| 实际命令 | `openclaw.cmd gateway run` |
| 配置目录 | `C:\Users\Administrator\.openclaw\` |
| 配置文件 | `C:\Users\Administrator\.openclaw\openclaw.json` |
| 进程特征 | node.exe / openclaw.cmd |
| 崩溃恢复 | NSSM 10s重启，无限次 |
| 飞书状态 | ✅ 已连接（长连接模式，App ID cli_a9561ba885f9dcc2） |

#### Hermes Agent 配置
| 项目 | 值 |
|------|------|
| NSSM服务名 | `HermesGateway` |
| 启动方式 | `hermes.exe gateway run` |
| 配置目录 | `C:\Users\Administrator\.hermes\`（⚠️ 不是 AppData\Local\hermes） |
| 配置文件 | `C:\Users\Administrator\.hermes\config.yaml` |
| 凭证文件 | `C:\Users\Administrator\.hermes\auth.json` |
| 环境变量 | `C:\Users\Administrator\.hermes\.env` |
| 记忆目录 | `C:\Users\Administrator\.hermes\memories\` |
| 会话目录 | `C:\Users\Administrator\.hermes\sessions\` |
| 进程特征 | hermes.exe |
| NSSM环境变量 | `PYTHONIOENCODING=utf-8`, `USERPROFILE`, `HOME`, `APPDATA` |
| 崩溃恢复 | NSSM 10s重启，无限次 |
| 飞书状态 | ✅ 已连接 |

### 2.2 备份清单
| 备份 | 路径 | 内容 | 时间 |
|------|------|------|------|
| Hermes旧数据（服务迁移前） | `C:\Users\Administrator\hermes_backup_old_core\` | 旧记忆+23个历史会话+db+config+auth+SOUL | 2026-05-02 |
| Hermes新数据（迁移后快照） | `C:\Users\Administrator\hermes_backup_new\` | 完整 ~/.hermes/ 快照 | 2026-05-02 |
| 旧Hermes原目录（未删除） | `C:\Users\Administrator\AppData\Local\hermes\` | 完整旧配置+源码+venv+会话+记忆 | — |

### 2.3 其他设备
| 设备 | Tailscale IP | 用户 | 系统 | 用途 |
|------|-------------|------|------|------|
| RackNerd VPS | 100.97.16.108 | hermes | Debian 12 | 旧Hermes（已不用） |
| S3 Aspire | 100.103.88.31 | win | Ubuntu 24.04 | Kitchen Agent（小园老师） |
| Lenovo | 100.118.178.110 | rf | Ubuntu 24.04 | 个人电脑 |

---

## 三、NSSM 服务管理

### 3.1 常用操作
```powershell
# 查看状态
nssm status OpenClawGateway
nssm status HermesGateway

# 重启（⚠️ 确认服务名再操作！）
nssm restart OpenClawGateway
nssm restart HermesGateway

# 停止
nssm stop OpenClawGateway
nssm stop HermesGateway

# 启动
nssm start OpenClawGateway
nssm start HermesGateway
```

### 3.2 区分规则（防搞混）
| 维度 | OpenClaw | Hermes |
|------|----------|--------|
| 服务名 | OpenClawGateway | HermesGateway |
| 配置目录 | ~/.openclaw/ | ~/.hermes/ |
| 进程名 | node.exe / openclaw.cmd | hermes.exe |
| 安装路径 | AppData\Roaming\npm\ | Hermes安装目录 |
| bat wrapper | openclaw_svc.bat | 无（直接执行） |

### 3.3 崩溃恢复策略
- 两者均配置为：失败后10秒重启，重启次数=0（无限），重置周期=0
- 无需看门狗脚本，Windows服务原生处理

---

## 四、模型与Fallback配置

### 4.1 Hermes 模型配置
| 项目 | 值 |
|------|------|
| 主模型 | zai/glm-5-turbo |
| Base URL | https://open.bigmodel.cn/api/paas/v4 |
| 备用Provider | minimax-cn (MiniMax-M2.7, Anthropic协议) |
| 备用URL | https://api.minimaxi.com/anthropic |
| 备用Key环境变量 | MINIMAX_CN_API_KEY |

### 4.2 代理配置
- **Clash端口**: 6789
- **Git代理**: `git config --global http.proxy http://127.0.0.1:6789`
- **OpenAI访问**: 必须走代理

---

## 五、当前问题与状态

| 问题 | 优先级 | 状态 | 备注 |
|------|--------|------|------|
| ~~Gateway崩溃无自动重启~~ | ~~🔴 高~~ | ✅ 已解决 | NSSM服务+原生崩溃恢复 |
| ~~Hermes记忆丢失~~ | ~~🔴 高~~ | ✅ 已解决 | 从AppData\Local\hermes迁移到~/.hermes |
| MiniMax Key续期 | 🟡 中 | 待确认 | — |
| ~~旧计划任务清理~~ | ~~🟡 中~~ | ✅ 已禁用 | HermesGateway/Hermes Gateway/OpenClaw Gateway 三个旧任务已禁用 |
| S3 OpenClaw升级 | 🟢 低 | 待处理 | 2026.4.14→latest |

---

## 六、运维日志

> 格式：`[日期] [操作端] 事件描述 — 结果/待办`

### 2026-05-01
- [05-01] [Hermes远程] 双Gateway部署为NSSM服务 — OpenClawGateway + HermesGateway 注册成功，崩溃10s自动重启
- [05-01] [Hermes远程] 删除看门狗计划任务 — OpenClaw Watchdog + HermesWatchdog 已删除
- [05-01] [Hermes远程] 安装NSSM — 通过chocolatey安装
- [05-01] [Hermes远程] 修复Hermes GBK编码崩溃 — 设置PYTHONIOENCODING=utf-8
- [05-01] [Hermes远程] 修复OpenClaw LocalSystem路径问题 — 创建bat wrapper设置USERPROFILE/HOME/APPDATA
- [05-01] [Hermes远程] 修复Hermes飞书连接 — .env从AppData\Local\hermes复制到~/.hermes
- [05-01] [Hermes远程] 禁用旧计划任务 — HermesGateway/Hermes Gateway/OpenClaw Gateway三个已禁用

### 2026-05-02
- [05-02] [Hermes远程] Hermes记忆丢失排查 — 发现服务迁移后工作目录从AppData\Local\herms变为~/.hermes，旧数据未迁移
- [05-02] [Hermes远程] 数据备份 — 创建hermes_backup_old_core（旧数据核心文件）和hermes_backup_new（新目录快照）
- [05-02] [Hermes远程] 记忆+会话迁移 — MEMORY.md/USER.md/20个历史会话/memory_store.db/state.db从旧目录复制到新目录，Hermes服务重启，记忆恢复

### 2026-04-28
- [04-28] [贾维斯] OpenAI Codex 接入 — OAuth授权成功(gpt-5.5)
- [04-28] [贾维斯] aios仓库clone到本机 — `C:\Users\Administrator\aios`
- [04-28] [贾维斯] OPS-PANO.md 创建 — 初始化双端同步方案
- [04-28] [Hermes] Windows OpenClaw Gateway 崩溃恢复 — 原因：unhandled_rejection（内存2GB+）

---

## 七、同步协议

### 7.1 核心原则
- **只同步一个文件**：OPS-PANO.md
- **Hermes远程维护**：通过SSH操作Windows VPS上的git仓库
- **push 前必须 pull**：`git pull --rebase` 避免冲突
- **日志只追加**：不修改历史条目

### 7.2 操作流程
```
1. SSH到Windows VPS
2. cd C:\Users\Administrator\aios
3. 编辑 OPS-PANO.md
4. git add OPS-PANO.md
5. git commit -m "hermes: [简要描述]"
6. git pull --rebase origin main
7. git push origin main
```

### 7.3 Git仓库
- **SSH**: `git@github.com:rf2025up/aios.git`
- **HTTPS**: `https://github.com/rf2025up/aios.git`

---

## 八、紧急联系与恢复

### 8.1 Gateway 崩溃恢复
```powershell
# 确认服务名再操作！
nssm restart OpenClawGateway   # 重启OpenClaw
nssm restart HermesGateway     # 重启Hermes（⚠️ 不是OpenClaw！）
```

### 8.2 远程恢复（SSH）
```bash
ssh Administrator@100.68.184.107
nssm restart OpenClawGateway
nssm restart HermesGateway
```

### 8.3 Git 冲突
- 放弃本地修改：`git checkout --theirs OPS-PANO.md` 后重新编辑

### 8.4 网络排查
```powershell
tailscale ping racknerd-d6189eb
curl -x http://127.0.0.1:6789 https://api.openai.com -I
netstat -ano | findstr ":18789"
```
