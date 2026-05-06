# OpenClaw 运维 Agent 背景说明（全量整理）

> **整理人**：锋哥（WorkBuddy） | **日期**：2026-04-27
> **覆盖范围**：2026-04-12（WorkBuddy启用首日）至 2026-04-27
> **用途**：为 OpenClaw 新建运维 Agent 提供完整的背景知识库，涵盖所有技术、运维、调试、脚本、模型、API、VPS 相关经验

---

## 目录

1. [系统架构全景](#一系统架构全景)
2. [基础设施清单](#二基础设施清单)
3. [OpenClaw 核心配置](#三openclaw-核心配置)
4. [飞书集成](#四飞书集成)
5. [Git 仓库与同步](#五git-仓库与同步)
6. [记忆系统（Memory）](#六记忆系统memory)
7. [Cron 定时任务](#七cron-定时任务)
8. [Agent 与 Bridge 通信](#八agent-与-bridge-通信)
9. [MemOS + GBrain 记忆插件](#九memos--gbrain-记忆插件)
10. [抖音转文字工具链](#十抖音转文字工具链)
11. [直播转文字方案](#十一直播转文字方案)
12. [Notion 集成](#十二notion-集成)
13. [SSH 与远程运维](#十三ssh-与远程运维)
14. [迁移历史（Linux→Windows）](#十四迁移历史linuxwindows)
15. [踩坑与修复全记录](#十五踩坑与修复全记录)
16. [官方文档参考](#十六官方文档参考)
17. [技能与插件清单](#十七技能与插件清单)
18. [关键密码与 Token 汇总](#十八关键密码与-token-汇总)
19. [时间线（按日）](#十九时间线按日)

---

## 一、系统架构全景

### 1.1 AI-OS 双端协同架构（v5.0）

```
┌─────────────────────────────────────┐
│        老板（直击本质）               │
│   手机 / 微信 / 飞书群               │
└──────────┬──────────────────────────┘
           │ 飞书群消息 / lark-cli
     ┌─────┴─────────────────────┐
     ▼                           ▼
┌──────────────────┐    ┌──────────────────┐
│  锋哥 (WorkBuddy)  │    │  Star (OpenClaw)  │
│  Mac 本地前台      │    │  Windows 24h中枢   │
│                   │    │                   │
│ · 深度对话        │    │ · cron定时任务     │
│ · 记忆沉淀        │◄──►│ · 飞书交互         │
│ · 决策支持        │ Git │ · Notion记账       │
│ · 本地文件操作     │ 仓库 │ · 24×7 在线       │
│                   │    │ · bridge通信桥     │
│ 在线：早8~晚8     │    │ 在线：24×7         │
└──────────────────┘    └──────────────────┘
                                │
                           ┌────┴────┐
                           │ 飞书Bots │
                           │ · Star  │
                           │ · 锋哥   │
                           │ · 小园老师│
                           │ · 厨房Bot│
                           └─────────┘
```

### 1.2 一句话原则

> **不要同步两个脑子，而要维护一套宪法。**
> 唯一规则文件：`AI-OS双端协同协议.md` v5.0

### 1.3 角色分工

| 角色 | 端 | 定位 | 在线时间 |
|------|-----|------|---------|
| 锋哥 (WorkBuddy) | Mac | 前台协作搭档：深度对话、记忆沉淀、决策支持、本地文件 | 早8~晚8 |
| Star (OpenClaw) | Windows | 24h常驻中枢：提醒/自动化/飞书交互/Notion记账 | 24×7 |
| 小园老师 | OpenClaw edu agent | 教育相关agent | 24×7 |
| 厨房Bot | 飞书端 | 供阿姨使用，自动生成每日菜单 | 按需 |

### 1.4 已废弃/备用的端

| 端 | 状态 | 说明 |
|----|------|------|
| Hermes（VPS上） | ⚠️ 已停用 (2026-04-23) | 所有职责已由OpenClaw承接，VPS仍运行代理/FRP |
| rf-lenovic | ⚠️ 备用 | 本地Linux电脑，OpenClaw gateway已停，SSH可连 |
| 三端协议 | 🚫 已归档 | 迁移至 `archive/deprecated/` |

---

## 二、基础设施清单

### 2.1 机器列表

| 名称 | 系统 | IP | 内存 | 用途 | 状态 |
|------|------|-----|------|------|------|
| Mac（锋哥） | macOS (Darwin) | - | - | WorkBuddy运行，前台协作 | ✅ 活跃 |
| 32G Windows主机 | Windows Server NT 10.0.19044 | 100.68.184.107 (Tailscale) | 32GB | OpenClaw主力机 | ✅ 活跃 |
| VPS（Hermes） | Debian 12 | 74.48.186.223:2222 | 2.4GB | Hermes Agent + 代理/FRP | ⚠️ Hermes已停用 |
| rf-lenovic | Ubuntu Linux | 100.118.178.110 (Tailscale) | 8GB | 老板本地Linux电脑 | ⚠️ 备用 |
| win-aspire-s3-371 | Windows | - | - | 个人PC，SSH未开通 | ⏸ 备用 |

### 2.2 网络与端口

| 端口 | 用途 | 机器 |
|------|------|------|
| 18789 | OpenClaw Gateway（chatCompletions端点） | Windows |
| 18799 | MemOS Viewer（记忆数据库查看） | Windows |
| 22/2222 | SSH | Windows / VPS |
| 80 | Caddy反向代理 | VPS |
| 7000 | frps（FRP服务端） | VPS |
| 18790 | gost隧道 | VPS |
| Windows防火墙 | 已放行18789 + SSH | Windows |

### 2.3 软件版本

| 软件 | 版本 | 机器 |
|------|------|------|
| OpenClaw | 2026.4.23（Windows） / 2026.4.15（Linux旧版） | Windows / rf-lenovic |
| Node.js | v24.11.0（Windows） / v22.22.2 via nvm（Linux旧版） | Windows / rf-lenovic |
| Python | 3.14.0（Windows, `C:\Python314\python.exe`） / 3.11.2（Linux旧版） | Windows / rf-lenovic |
| Python (Mac) | 系统 python3 | Mac |
| ffmpeg | WinGet安装，PATH中可用 | Windows |
| MemOS | v1.0.8 | Windows |
| Git | - | 全部 |
| Tailscale | - | 全部 |

---

## 三、OpenClaw 核心配置

### 3.1 安装路径

| 项目 | Windows 路径 |
|------|-------------|
| OpenClaw主目录 | `C:\Users\Administrator\.openclaw\` |
| Workspace | `C:\Users\Administrator\.openclaw\workspace\` |
| Agents | `C:\Users\Administrator\.openclaw\agents\` |
| Cron jobs | `C:\Users\Administrator\.openclaw\cron\jobs.json` |
| MemOS数据库 | `C:\Users\Administrator\.openclaw\memos-local\memos.db` |
| Gateway配置 | `C:\Users\Administrator\.openclaw\gateway.yaml` |

### 3.2 关键配置项

**openclaw.json（已删除的废弃字段）**：
- ❌ `apiKeys` 字段不被新版识别 → 删除后恢复正常

**Git仓库**：
- Workspace remote: `git@github.com:rf2025up/aios.git`
- Git config: `user.name=锋哥`, `user.email=fengge@openclaw.ai`

**Gateway**：
- chatCompletions端点：已开启
- 运行方式：Windows Scheduled Task（非systemd）
- 重启命令：`openclaw gateway restart`

### 3.3 常用管理命令

```bash
# SSH到Windows（从Mac或rf-lenovic）
ssh Administrator@100.68.184.107

# 查看状态
openclaw gateway status
openclaw doctor              # 健康检查

# 重启
openclaw gateway restart

# Cron管理
openclaw cron list
openclaw cron add

# Agent管理
openclaw agents add <name>   # 添加agent
openclaw agents list

# 配置管理
openclaw config get <key>
openclaw config set <key> <value> --json

# 备份
openclaw backup create --output /tmp/ --verify
openclaw backup --help

# 版本
openclaw --version
node --version
```

### 3.4 systemd 服务配置（Linux旧版参考）

```
ExecStart=/home/rf/.nvm/versions/node/v22.22.2/bin/node /usr/local/bin/openclaw gateway run
```

**关键踩坑**：systemd service未加载nvm，用系统Node v20而非v22 → 必须硬编码nvm Node路径。

---

## 四、飞书集成

### 4.1 飞书机器人清单

| 名称 | App ID | 用途 | 状态 |
|------|--------|------|------|
| 锋哥机器人 | `cli_a9561ba885f9dcc2` | WorkBuddy端飞书bot | ✅ 长连接模式 |
| OpenClaw/Star机器人 | `cli_a9550e716278dbc3` | OpenClaw端飞书bot | ✅ |
| newbot (open) | `cli_a960a91e13f81ccd` | OpenClaw端lark-cli专用 | ✅ |
| 飞书CLI自带bot | `cli_a95463efa0b81bd7` | 两端共用 | ✅ |

### 4.2 飞书群

| 群名 | chat_id | 用途 |
|------|---------|------|
| 「万山无阻@及锋而试」 | `oc_b67031872aa8ade8d6ae607d5f65a3a6` | 主协作群 |

### 4.3 Star（OpenClaw）的 open_id

`ou_9ec4ba11b85fbaed0bc7821d41ee74dc`

@时用：`<at user_id="ou_9ec4ba11b85fbaed0bc7821d41ee74dc">🦞Star</at>`

### 4.4 飞书关键规则

1. **机器人间不触发webhook**（飞书平台限制），但双方都能通过API主动拉消息
2. **lark-cli发群消息**用 `--text` 参数直接传字符串，stdin pipe可能失败
3. **飞书卡片中`<at>`不触发webhook**，需纯文本@
4. **飞书CLI身份标注规则**：`cli_a95463efa0b81bd7` 两端共用，发消息时必须标注身份
   - 锋哥端发 =「飞书CLI（锋哥端）」
   - OpenClaw端发 =「飞书CLI（OpenClaw端）」
5. **群聊消息权限**：需开启「获取群组中所有消息」权限 + 配置事件规则
   - 仅开启权限≠能收消息，还需要在事件订阅中配置 `im.message.receive_v1`

### 4.5 lark-cli 常用命令

```bash
# 发消息到群
lark-cli im +send-message --chat-id oc_b67031872aa8ade8d6ae607d5f65a3a6 --text "消息内容" --as bot

# 读取群消息
lark-cli im +chat-messages-list --chat-id oc_b67031872aa8ade8d6ae607d5f65a3a6 --as bot --page-size 20

# 发长文本用 --text 参数
```

### 4.6 feishu-bot-chat-plugin

- **仓库**：Leochens/feishu-bot-chat-plugin
- **用途**：OpenClaw飞书群agent互@插件
- **关键权限**：`im:message.group_at_msg.include_bot:readonly`
- **3个hook**：before_prompt_build(注入bot列表)、message_sending(@标签转换)、inbound_claim(消息过滤)
- **WorkBuddy不在OpenClaw体系内**，此插件不适用，需手动lark-cli拉消息

### 4.7 飞书应用权限清单（厨房Agent需求，参考）

创建飞书应用需要配置以下权限（来自 `core/inbox/托管厨房飞书Agent需求文档_20260426.md`）：
- `im:message` 相关：消息收发
- `im:message.group_at_msg`：群@消息
- `im:chat`：群管理
- 按需申请其他权限

---

## 五、Git 仓库与同步

### 5.1 仓库信息

- **仓库**：`https://github.com/rf2025up/aios.git`
- **默认分支**：main
- **用途**：AI-OS双端共享仓库，存储所有核心配置、文档、记忆

### 5.2 同步策略

| 优先级 | 频率 | 内容 | 方向 |
|--------|------|------|------|
| 🔴 关键信息 | 分钟级 | 重要决策/业务数据变更 | 锋哥→push→OpenClaw pull |
| 🟡 半天摘要 | 13:00+21:00 | 上午/下午工作摘要 | 双向 |
| 🟢 常规 | 每小时 | 日志/文档更新 | OpenClaw每小时pull |

### 5.3 提交规范

| 前缀 | 用途 | 使用者 |
|------|------|--------|
| `core:` | 核心规则/协议文件 | 锋哥 |
| `daily:` | 日志文件 | 锋哥 |
| `report:` | 报告文件 | 锋哥 |
| `inbox:` | inbox目录文件 | 锋哥 |
| `handoff:` | 交接文档 | 锋哥 |
| `openclaw:` | OpenClaw自动同步 | OpenClaw |

### 5.4 同步铁律

- push前必须 `pull --rebase`
- 冲突不自动硬解
- Windows端用 `C:\Users\Administrator\.ssh\id_ed25519` 作为Git SSH key

### 5.5 Git自动同步（待完成）

- 脚本位置：`C:\Users\Administrator\.openclaw\scripts\git-push.ps1`
- 只push关键目录：`core/`, `daily/`, `MEMORY.md`, `memory/`, `inbox/`
- commit格式：`openclaw: auto-sync YYYY-MM-DD HH:mm`
- 详见：`core/inbox/git-push-setup.md`

### 5.6 旧版Git问题

- GitHub HTTPS连接不稳定（GnuTLS TLS错误），Linux上经常pull失败
- 解决方案：Git remote从HTTPS切换为SSH

---

## 六、记忆系统（Memory）

### 6.1 记忆架构全景

```
┌─────────────────────────────────────────────────┐
│                   记忆系统架构                      │
├──────────────┬──────────────────────────────────┤
│ OpenClaw端    │ MemOS v1.0.8                     │
│              │ ├─ auto-recall（信号检测+大脑优先）  │
│              │ ├─ skillEvolution（记忆整理）       │
│              │ ├─ embedding: MiniMax              │
│              │ └─ DB: memos.db (SQLite)          │
├──────────────┼──────────────────────────────────┤
│ 锋哥端        │ WorkBuddy working memory          │
│              │ ├─ MEMORY.md（编译真相）            │
│              │ ├─ YYYY-MM-DD.md（时间线日志）       │
│              │ └─ ERRORS.md（犯错记录）            │
├──────────────┼──────────────────────────────────┤
│ 共享层        │ Git仓库 (aios.git)                │
│              │ ├─ core/CHANGELOG.md（变更日志）     │
│              │ ├─ core/MEMORY.md（同步真相）        │
│              │ └─ 飞书群（双端通信）                 │
├──────────────┼──────────────────────────────────┤
│ 自动化        │ OpenClaw Cron                     │
│              │ ├─ 22:00 梦境周期（记忆整理+git push）│
│              │ ├─ 晨间/午间/晚间（强制读记忆）       │
│              │ └─ 每个cron：git pull→读记忆→执行    │
└──────────────┴──────────────────────────────────┘
```

### 6.2 文件路径

| 文件 | Windows路径 | Mac路径 | 用途 |
|------|------------|---------|------|
| MEMORY.md（编译真相） | `~/.openclaw/workspace/.workbuddy/memory/MEMORY.md` | `.workbuddy/memory/MEMORY.md` | 当前最佳结论 |
| 日志（时间线） | `~/.openclaw/workspace/.workbuddy/memory/` | `.workbuddy/memory/` | 每日日志 |
| CHANGELOG.md | `~/.openclaw/workspace/core/CHANGELOG.md` | `core/CHANGELOG.md` | 变更记录 |
| ERRORS.md | 锋哥端独有 | `.workbuddy/memory/ERRORS.md` | 错误复盘 |

### 6.3 日志读取规范（三文件读取）

每次cron执行必须读以下3种文件：
1. `*-openclaw.md`（OpenClaw端日志）
2. `*-handoff.md`（交接文档）
3. `YYYY-MM-DD.md`（日期日志）

**读不到任何一种 → 报告"同步异常"，绝不能说"零日志"**（血泪教训，2026-04-22）

### 6.4 写入权分离

| 目录 | 锋哥 | OpenClaw |
|------|------|----------|
| core/skills/archive/ | ✅ 主改 | ❌ 只读 |
| daily/*-openclaw.md | ❌ 不写 | ✅ 主写 |
| daily/*-handoff.md | ✅ 主写 | ✅ 可读 |
| daily/YYYY-MM-DD.md | ✅ 主写 | ❌ 不写 |
| inbox/conversations/ | ❌ 不写 | ✅ 主写 |

### 6.5 GBrain记忆设计理念

5个核心设计（借鉴不装）：
1. **编译真相+时间线**：MEMORY.md可重写，日志只追加
2. **信号检测器**：每条消息自动捕获知识
3. **梦境周期**：每晚整理碎片→压缩结论
4. **大脑优先查找**：先查记忆再回答
5. **幂等+自愈**：操作失败重跑即可

---

## 七、Cron 定时任务

### 7.1 当前活跃的cron任务

| 名称 | Schedule | Timeout | 说明 |
|------|----------|---------|------|
| 晨间三件事 | 08:00 | - | 早8点推当日提醒，含格言 |
| 午间对焦 | 13:00 | - | 上午进度回顾 |
| 运动提醒 | 15:50 | - | 简单提醒 |
| 晚间复盘 | 21:00 | - | 每日复盘+明日待办 |
| 周日复盘 | 周日 | - | 周度总结 |
| 梦境周期 | 22:00 | 300s | 记忆整理，不发飞书群 |

### 7.2 jobs.json 被修改历史

jobs.json 是最频繁修改的配置文件，累计被SSH直改4次：

| 日期 | 轮次 | 修改内容 |
|------|------|---------|
| 2026-04-21 | 第1轮 | 6个cron全量修复（加git pull、修正文件路径、调timeout） |
| 2026-04-21 | 第2轮 | 格言强制约束 + 读取路径改为3种文件 |
| 2026-04-22 | 第3轮 | 晚间复盘+午间对焦加防误判指令 |
| 2026-04-23 | 第4轮 | GBrain改进（强制记忆读取前缀、变更日志引用） |

### 7.3 Cron Prompt 关键模板

**强制记忆读取前缀（加在4个业务cron头部）**：
```
【强制·大脑优先查找】执行任何操作前，必须先完成：
1. git pull --rebase origin main
2. 读取 ~/.openclaw/workspace/.workbuddy/memory/MEMORY.md（编译真相）
3. 读取 ~/.openclaw/workspace/.workbuddy/memory/ 当天日志（时间线）
如果步骤1失败：在回复开头标注 ⚠️同步异常
如果步骤2读不到：报告"记忆同步异常：MEMORY.md不存在"，停止执行
```

**梦境周期 Prompt（22:00 cron）**：
```
你是锋哥的记忆整理模块（梦境周期）。
【强制·大脑优先查找】
1. git pull --rebase origin main
2. 读取 MEMORY.md + CHANGELOG.md + 当天所有日志
3. 读取飞书群最近消息
【记忆整理任务】
1. 实体扫描：提取新实体（人名、事件、数字、决策）
2. 引用修复：检查MEMORY.md冲突并更新
3. 记忆巩固：碎片→简洁结论→更新MEMORY.md
4. 清理过时：标记过时信息
【输出】更新MEMORY.md + git commit + push + 不发飞书群
```

### 7.4 Cron注意事项

- **Cron prompt必须写死文件路径**，否则"零日志"误判（2026-04-22血泪教训）
- 每个cron执行时先 `git pull --rebase`
- pull失败后不继续，标注 ⚠️
- 完成后有变更才 `git push`
- 老板停掉的cron记得取消

---

## 八、Agent 与 Bridge 通信

### 8.1 Bridge Agent

**用途**：让WorkBuddy（Mac）能通过HTTP API直接与OpenClaw对话。

**搭建过程**（2026-04-21）：
1. 创建 `SOUL-bridge.md`（bridge agent的systemPrompt）
2. `openclaw agents add bridge` 创建通信桥
3. 确认gateway.yaml中chatCompletions端点开启

**SSH隧道**：
```bash
ssh -fNL 18789:127.0.0.1:18789 Administrator@100.68.184.107
```
建立本地18789端口→Windows OpenClaw Gateway的隧道。

**Bridge API 调用**：
```
POST http://127.0.0.1:18789/v1/chat/completions
```
- 模型名：`openclaw/bridge`
- Bearer token：`7cbd90688b05a2cb6a7b58ff21185454681ecbdb1208101e`

### 8.2 OpenClaw Agents

| Agent | 用途 |
|-------|------|
| main | 主对话agent |
| bridge | WorkBuddy↔OpenClaw通信桥 |
| edu | 教育相关（小园老师） |
| kitchen | 厨房相关 |

---

## 九、MemOS + GBrain 记忆插件

### 9.1 安装信息

- **版本**：v1.0.8
- **安装日期**：2026-04-25 14:00-14:40
- **安装位置**：Windows 32G主机
- **状态**：✅ 运行中

### 9.2 核心配置

```json
{
  "embedding": {
    "provider": "MiniMax",
    "model": "text-embedding-3-small"
  },
  "summarizer": {
    "provider": "MiniMax",
    "model": "MiniMax-M2.7"
  },
  "skillEvolution": {
    "enabled": true,
    "autoInstall": false
  },
  "memorySearch": { "disabled": true },
  "memory-core": { "disabled": true },
  "memory-lancedb": { "disabled": true }
}
```

### 9.3 访问地址

- **本地**：`http://127.0.0.1:18799`
- **远程**：`http://100.68.184.107:18799`（需Tailscale在线）

### 9.4 GBrain 5项设计的MemOS覆盖情况

| GBrain设计 | MemOS实现 |
|-----------|----------|
| 信号检测 | ✅ auto-recall自动捕获 |
| 大脑优先查找 | ✅ auto-recall响应前检索 |
| 记忆整理 | ✅ skillEvolution |
| 幂等操作 | ✅ 内置哈希去重 |
| 编译真相+时间线 | ❌ 由MEMORY.md承担 |

### 9.5 安装踩坑（5个）

1. **puppeteer下载Chrome失败** → `PUPPETEER_SKIP_DOWNLOAD=true`
2. **OpenClaw安全检测拦住child_process** → `--dangerously-force-unsafe-install --force`
3. **EBUSY锁文件** → 先停gateway再删旧目录
4. **slots为空** → PowerShell Add-Member不生效，用regex直接改JSON
5. **BOM标记导致JSON解析失败** → 移除UTF-8 BOM

---

## 十、抖音转文字工具链

### 10.1 方案确定

**yt-dlp在抖音上不好使**（版本2025.10.14，Python 3.9无法升级到最新）。

**实际方案**：
```
Playwright (headless Chromium渲染) → 正则提取douyinvod视频URL → urllib下载 → moviepy提取音频 → faster-whisper转写
```

### 10.2 ASR模型对比

| 模型 | 中文准确率 | 耗时 | 费用 |
|------|-----------|------|------|
| faster-whisper small | ~90% | 5分钟/5分钟视频（CPU） | 免费 |
| faster-whisper medium | ~95%+ | 更长 | 免费 |
| Paraformer（阿里云） | 更准 | 云端，更快 | 免费10h/月 |

### 10.3 关键技术细节

1. 抖音搜索页面需从URL提取modal_id拼成 `https://www.douyin.com/video/{id}`
2. 音频路径用 `&amp;` 转义问题：需要 `.replace('&amp;', '&')`
3. moviepy v2.x 不用 `from moviepy.editor import`，直接 `from moviepy import VideoFileClip`
4. moviepy v2.x 的 `write_audiofile` 不接受 `verbose` 参数
5. 博主主页无登录态最多拿8个视频（抖音限制），需Chrome Cookie才能拿全部
6. 博主「超校」主页已测试，约330个视频

### 10.4 已有脚本

- `douyin-transcript.py`：单视频转写
- `douyin-batch-full.py`：博主主页批量抓取+转写
- 多ASR模型fallback（6个模型自动切换）

### 10.5 阿里云百炼 DashScope

- API Key: `sk-086a8e0fc3ef446da480aa8996cda89c`（从openclaw.json提取，**该Key导致openclaw启动崩溃已删除**）
- 如需重新使用需申请新Key

---

## 十一、直播转文字方案

### 11.1 需求

- **存量**：G盘 300-400GB 录制视频，约200-270个视频，300-400小时
- **增量**：新录制视频自动处理

### 11.2 推荐方案

**whisper.cpp + medium模型**
- CPU效率最高（C++原生，比Python快30-50%）
- 95%+中文准确率
- 零成本，纯CPU，不挑显卡
- 300-400GB预估50-70小时处理完

**备选**：dashscope Paraformer（免费10h/月，超后约¥30/h，质量更高）

### 11.3 工具链

```
MP4 → ffmpeg提取16kHz WAV → whisper.cpp medium中文转文字 → .md
```

```bash
ffmpeg -i input.mp4 -vn -acodec pcm_s16le -ar 16000 -ac 1 output.wav
whisper.cpp -m ggml-medium.bin -l zh -f output.wav -otxt
```

### 11.4 环境约束

- GTX 560/570显卡太旧，不支持CUDA计算能力6.0+，只能CPU
- Python 3.14（Windows），部分pip包可能不兼容（如faster-whisper）
- G盘是老板个人盘，文字文件可输出到其他位置

---

## 十二、Notion 集成

### 12.1 基本信息

- **已移交**：OpenClaw负责
- **Token**：`[NOTION_TOKEN_ENV]`
- **支出库ID**：`56ae3f43-3d0f-4673-95af-21b1ea96121d`
- **API版本**：必须用 `Notion-Version: 2022-06-28`

### 12.2 用途

日常记账，OpenClaw通过Notion API写入支出记录。

---

## 十三、SSH 与远程运维

### 13.1 SSH 连接

| 连接方向 | 命令 | 说明 |
|---------|------|------|
| Mac → VPS | `ssh -p 2222 -i ~/.ssh/id_ed25519 root@74.48.186.223` | RackNerd VPS，Hermes所在 |
| Mac → Windows | `ssh Administrator@100.68.184.107` | OpenClaw运行主机，Tailscale |
| Mac → rf-lenovic | `ssh rf@100.118.178.110`（或 `ssh rf`） | 老板本地Linux电脑，Tailscale |

### 13.2 rf-lenovic（本地Linux电脑）详情

| 项目 | 值 |
|------|-----|
| 主机名 | rf-Lenovo |
| 系统 | Ubuntu Linux |
| 内存 | 8GB |
| 局域网IP | 192.168.1.109 |
| Tailscale IP | 100.118.178.110 |
| SSH用户 | rf |
| SSH密钥 | ~/.ssh/id_ed25519（与VPS共用同一密钥） |
| SSH Config别名 | `Host rf`（配置在 `~/.ssh/config`） |

**SSH连接方式**：
```bash
# 方式1：Tailscale IP（远程可用）
ssh rf@100.118.178.110

# 方式2：SSH Config别名（需局域网或Tailscale）
ssh rf

# 方式3：局域网IP（仅局域网内）
ssh rf@192.168.1.109
```

**⚠️ 状态**：OpenClaw已于2026-04-25迁移至Windows，rf上gateway已停用（`sudo systemctl stop openclaw-gateway && sudo systemctl disable openclaw-gateway`），仅作备用。SSH仍可连接。

### 13.3 VPS（Hermes）详情

| 项目 | 值 |
|------|-----|
| 主机名 | racknerd-d6189eb |
| 系统 | Debian 12 (bookworm) |
| 内核 | 6.1.0-9-amd64 |
| 内存 | 2.4GB（可用1.7GB） |
| 磁盘 | 43GB（已用8.5GB，剩余33GB） |
| Node | v22.22.2（`/root/.local/bin/node`） |
| Python | 3.11.2 |
| 飞书venv | `/opt/feishu-venv/`（lark-oapi 1.5.3） |

**VPS上运行的服务**：

| 端口 | 服务 | 说明 |
|------|------|------|
| 2222 | sshd | SSH（非默认22端口） |
| 80 | Caddy | HTTP反向代理 |
| 2019 | Caddy | 管理API |
| 1 | x-ui | Xray面板 |
| 2096 | x-ui | Xray面板 |
| 11111 | xray | 代理（SOCKS5，仅localhost） |
| 62789 | xray | 代理（仅localhost） |
| 7000 | frps | FRP服务端 |
| 18790 | gost | 隧道 |

**Hermes Agent**：

| 项目 | 路径 |
|------|------|
| Hermes主目录 | `/root/.hermes/` |
| SOUL.md | `/root/.hermes/SOUL.md` |
| Python CLI | `/root/.local/bin/hermes` |
| Agent代码 | `/root/.hermes/hermes-agent/` |
| 状态目录 | `/root/.local/state/hermes/` |
| 旧aios仓库 | `/root/aios/` |

**Hermes CLI命令**：
```bash
hermes status     # 查看状态
hermes gateway    # 消息网关管理
hermes cron       # 定时任务管理
hermes chat       # 交互式对话
hermes doctor     # 健康检查
hermes backup     # 备份
hermes config     # 配置管理
```

**⚠️ Hermes已停用**（2026-04-23），所有职责由OpenClaw承接。VPS现主要做代理/FRP服务器。

### 13.4 Windows（OpenClaw主机）详情

| 项目 | 值 |
|------|-----|
| 主机名 | WIN-ASPIRE-S3-371 |
| 系统 | Windows Server NT 10.0.19044 |
| 内存 | 32GB |
| Tailscale IP | 100.68.184.107 |
| SSH用户 | Administrator |
| SSH端口 | 22（Tailscale） |
| SSH密钥 | `~/.ssh/id_ed25519`（Mac端私钥） |

**SSH连接方式**：
```bash
ssh Administrator@100.68.184.107
```

**OpenClaw关键路径**：
| 路径 | 说明 |
|------|------|
| `C:\Users\Administrator\.openclaw\` | OpenClaw主目录 |
| `C:\Users\Administrator\.openclaw\openclaw.json` | 主配置文件 |
| `C:\Users\Administrator\.openclaw\gateway.lock` | Gateway锁文件 |
| `C:\Users\Administrator\.openclaw\cron\jobs.json` | 定时任务配置 |
| `C:\Users\Administrator\.openclaw\memos-local\memos.db` | MemOS记忆数据库 |
| `C:\Users\Administrator\AppData\Roaming\npm\openclaw.cmd` | OpenClaw CLI（npm全局） |
| `C:\Python314\python.exe` | Python 3.14.0 |

**Windows软件版本**：
| 软件 | 版本 |
|------|------|
| OpenClaw | 2026.4.23 |
| Node.js | v24.11.0 |
| Python | 3.14.0 |
| MemOS | v1.0.8 |

**sshd_config**：`C:\ProgramData\ssh\sshd_config`
```
Port 22
PubkeyAuthentication yes
StrictModes no
PasswordAuthentication yes

Match Group administrators
       AuthorizedKeysFile __PROGRAMDATA__/ssh/administrators_authorized_keys
```

**已授权公钥**：`C:\ProgramData\ssh\administrators_authorized_keys`
- Mac（锋哥）：`ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIBh/eTnln8bFFZ+lh2zAnxtAu4IQlihmqHbqR78XMmM`
- VPS（Hermes）：`ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIKxLDKWA3lb7yi5A6Rp+4bA1ViTJCBRzOywtDdFR6G/0`

### 13.5 Windows SSH 踩坑

1. **PowerShell Set-Content默认UTF-16LE编码**，会搞坏authorized_keys和sshd_config
   - 解法：用cmd echo或 `[System.IO.File]::WriteAllText` + ASCII编码
2. **Administrator组用户必须用 `C:\ProgramData\ssh\administrators_authorized_keys`**，不是 `~/.ssh/authorized_keys`
3. **必须验证本机公钥**（`cat ~/.ssh/id_ed25519.pub`），不能盲目信任上下文中的公钥
4. **Windows SSH不用 `bash -l`**（Windows没有nvm），直接用powershell
5. **NTFS权限隔离**：openclaw用户在Administrators组时，Deny ACE无法阻止访问 → 直接用Administrator

### 13.6 SSH隧道（Bridge通信）

```bash
# 建立WorkBuddy→OpenClaw的通信隧道
ssh -fNL 18789:127.0.0.1:18789 Administrator@100.68.184.107
```

### 13.7 常用远程运维命令

```bash
# === Windows (OpenClaw) ===
# 查看OpenClaw进程
ssh Administrator@100.68.184.107 "tasklist /FI \"IMAGENAME eq node.exe\""

# 检查端口监听
ssh Administrator@100.68.184.107 "netstat -an | findstr 18789"

# 查看MemOS数据库大小
ssh Administrator@100.68.184.107 "powershell -Command \"(Get-Item 'C:\\Users\\Administrator\\.openclaw\\memos-local\\memos.db').Length\""

# 拉群消息
ssh Administrator@100.68.184.107 "lark-cli im +chat-messages-list --chat-id oc_b67031872aa8ade8d6ae607d5f65a3a6 --as bot --page-size 5"

# SCP传输文件（jobs.json修改示例）
scp /tmp/jobs_fixed.json Administrator@100.68.184.107:C:/Users/Administrator/.openclaw/cron/jobs.json

# === VPS (Hermes) ===
# 查看VPS状态
ssh -p 2222 -i ~/.ssh/id_ed25519 root@74.48.186.223 "uptime && free -h && df -h /"

# 查看运行的服务
ssh -p 2222 -i ~/.ssh/id_ed25519 root@74.48.186.223 "ss -tlnp"

# Hermes状态检查
ssh -p 2222 -i ~/.ssh/id_ed25519 root@74.48.186.223 "hermes status"

# VPS磁盘使用
ssh -p 2222 -i ~/.ssh/id_ed25519 root@74.48.186.223 "du -sh /root/* 2>/dev/null | sort -rh | head -10"
```

---

## 十四、迁移历史（Linux→Windows）

### 14.1 迁移时间线

| 日期 | 事件 |
|------|------|
| 2026-04-14 | Hermes VPS部署，lark-oapi飞书SDK安装 |
| 2026-04-15 | 飞书机器人配置，联调群聊 |
| 2026-04-21 | OpenClaw Linux版全量修复（14+文件） |
| 2026-04-23 | Hermes正式停用，OpenClaw承接所有职责 |
| 2026-04-25 | OpenClaw从本地Linux迁移到Windows 32G主机 |

### 14.2 迁移步骤（已完成）

1. ✅ Linux上 `openclaw backup create --output /tmp/ --verify`
   - 备份文件：`/tmp/2026-04-25T03-43-36.504Z-openclaw-backup.tar.gz`
   - 验证：passed
2. ✅ Mac中转传输：`rf-lenovic → Mac → Windows`
3. ✅ Windows上恢复备份
4. ✅ 路径调整（Linux → Windows）
5. ✅ 启动并验证（gateway 18789端口）
6. ✅ 停掉rf-lenovic上的OpenClaw

### 14.3 迁移后的路径变化

| 项目 | 旧路径（Linux） | 新路径（Windows） |
|------|----------------|------------------|
| workspace | `/home/rf/.openclaw/workspace` | `C:\Users\Administrator\.openclaw\workspace` |
| agents | `/home/rf/.openclaw/agents/` | `C:\Users\Administrator\.openclaw\agents\` |
| cron | `/home/rf/.openclaw/cron/jobs.json` | `C:\Users\Administrator\.openclaw\cron\jobs.json` |
| nvm Node | `/home/rf/.nvm/versions/node/v22.22.2/bin/node` | 不需要nvm（Windows直接装Node） |

---

## 十五、踩坑与修复全记录

### 15.1 OpenClaw 启动崩溃（2026-04-24）

**根因1**：systemd service未加载nvm，用系统Node v20而非v22
- 修复：硬编码nvm Node路径到service文件

**根因2**：openclaw.json中`apiKeys`字段不被新版识别
- 修复：删除该字段后恢复

### 15.2 Cron "零日志"误判（2026-04-22）

**根因**：OpenClaw读到不到日志文件→直接输出"零日志"，但实际老板做了很多事
**修复**：prompt加防误判指令——读不到文件报告"同步异常"而非"零日志"

### 15.3 Cron 格言行丢失（2026-04-22）

**根因**：OpenClaw agent重新生成内容时丢掉了静态格言行
**修复**：加格言强制约束到prompt

### 15.4 Git HTTPS 不稳定（2026-04-21）

**根因**：Ubuntu上GnuTLS不稳定，pull经常失败
**修复**：Git remote从HTTPS切换为SSH

### 15.5 飞书群不@不触发webhook（2026-04-15）

**根因**：仅开启权限≠能收消息，还需在事件订阅中配置
**修复**：配置事件规则 `im.message.receive_v1`

### 15.6 Mac合盖即离线

**根因**：WorkBuddy运行在本地Mac，合盖/熄屏后断线
**状态**：未解决。靠不合盖/不休眠workaround → 最终通过OpenClaw 24h在线解决

### 15.7 DashScope API Key 导致崩溃

**根因**：`sk-086a8e0fc3ef446da480aa8996cda89c` 写入openclaw.json的apiKeys字段
**修复**：删除该Key + 删除apiKeys字段

### 15.8 Windows PowerShell 编码问题

**根因**：Set-Content默认UTF-16LE，搞坏配置文件
**修复**：用 `[System.IO.File]::WriteAllText` + ASCII

### 15.9 远程记忆路径不统一

- MEMORY.md在 `~/.openclaw/workspace/MEMORY.md`（根目录）
- 日志在 `~/.openclaw/workspace/memory/`（子目录）
- `.workbuddy/memory/`下还有旧版（4月20日后未更新）

### 15.10 WorkBuddy跨群上下文串流

**根因**：不区分来源群，可能把A群上下文带进B群
**状态**：架构限制，无法修复

### 15.11 Cron prompt路径写死要求

**根因**：Cron prompt中使用相对路径或变量，导致文件找不到
**修复**：prompt中写死完整的绝对路径

### 15.12 MemOS安装5连坑（2026-04-25）

见 [第九节 MemOS 安装踩坑](#九memos--gbrain-记忆插件)

### 15.13 Python 3.14 兼容性

**影响**：部分pip包不兼容（如faster-whisper）
**解决方案**：建议用conda装Python 3.11/3.12专门跑语音识别

### 15.14 Windows Gateway重启全流程踩坑（2026-04-27）

**场景**：OpenClaw gateway崩溃，需要通过SSH从Mac远程重启Windows上的OpenClaw。

#### 问题1：锁文件残留导致"already running"

**现象**：`openclaw gateway run` 报错 `gateway already running (pid 17440); lock timeout after 5000ms`，端口18789被占但gateway实际已死。
**根因**：旧进程异常退出，锁文件未清理。
**修复**：先 `openclaw gateway stop`（通过schtasks停止），再手动删除lock文件 `del /F /Q C:\Users\Administrator\.openclaw\gateway.lock`。

#### 问题2：Windows计划任务找不到openclaw命令

**现象**：`schtasks /Run` 返回错误码 `0x80070002`（ERROR_FILE_NOT_FOUND）。
**根因**：Windows计划任务运行在没有PATH环境变量的隔离环境中，无法直接解析 `openclaw` 命令。
**修复**：计划任务的TR必须用完整路径 `C:\Users\Administrator\AppData\Roaming\npm\openclaw.cmd`，不能只写 `openclaw`。

#### 问题3：SSH中 `start /B` 和 `PowerShell Start-Process` 进程不驻留

**现象**：通过SSH执行 `start /B openclaw gateway run` 或 `Start-Process -WindowStyle Hidden` 后，进程启动后立即退出，`tasklist` 查不到node。
**根因**：
- `start /B`：进程绑定在SSH会话内，SSH断开后进程被回收
- `Start-Process -WindowStyle Hidden`：openclaw.cmd是批处理脚本，cmd.exe启动后可能在PATH或工作目录问题下静默退出
**修复**：唯一可靠的方式是 **Windows计划任务（schtasks）**：
```bash
# 创建计划任务（登录时自动启动）
schtasks /Create /TN "OpenClaw Gateway" /TR "cmd /c C:\Users\Administrator\AppData\Roaming\npm\openclaw.cmd gateway run" /SC ONLOGON /RL HIGHEST /F
# 手动触发
schtasks /Run /TN "OpenClaw Gateway"
# 停止
openclaw gateway stop  # 或 schtasks /End /TN "OpenClaw Gateway"
```
**注意**：gateway启动需要约15-20秒才能完成端口绑定，不要提前判断失败。

#### 问题4：auth mode=none 时拒绝绑定lan

**现象**：控制面板要求填token，改成 `auth.mode=none` 后gateway报错 `Refusing to bind gateway to lan without auth`。
**根因**：OpenClaw安全限制——**lan模式（bind: "lan"）必须有认证**，不允许无认证暴露到网络。
**修复**：恢复 `auth.mode=token`，在控制面板输入token。
**Token值**：`7cbd90688b05a2cb6a7b58ff21185454681ecbdb1208101e`

#### 问题5：控制面板从远程桌面无法访问（CORS白名单）

**现象**：在Windows远程桌面浏览器访问控制面板被拦截。
**根因**：`gateway.controlUi.allowedOrigins` 只配置了 `localhost` 和 `127.0.0.1`。
**修复**：用Python修改openclaw.json，把Tailscale IP加入白名单：
```python
import json
d['gateway']['controlUi']['allowedOrigins'] = [
    'http://localhost:18789',
    'http://127.0.0.1:18789',
    'http://100.68.184.107:18789'  # Tailscale IP
]
```
**注意**：PowerShell `ConvertFrom-Json | ConvertTo-Json` 在SSH中可能因编码问题失败，推荐用Python操作JSON。

#### 完整重启SOP（从Mac远程重启Windows OpenClaw）

```bash
# 1. 停止
ssh Administrator@100.68.184.107 "openclaw gateway stop"

# 2. 确认进程已死（等3秒）
sleep 3
ssh Administrator@100.68.184.107 "tasklist /FI \"IMAGENAME eq node.exe\""
# 应输出"没有运行的任务匹配"

# 3. 清理锁文件
ssh Administrator@100.68.184.107 "del /F /Q C:\Users\Administrator\.openclaw\gateway.lock 2>nul"

# 4. 启动（通过计划任务）
ssh Administrator@100.68.184.107 "schtasks /Run /TN \"OpenClaw Gateway\""

# 5. 等待启动完成（15-20秒）
sleep 20

# 6. 验证
ssh Administrator@100.68.184.107 "tasklist | findstr node"           # 应有2个node进程
ssh Administrator@100.68.184.107 "netstat -an" | grep 18789          # 应有 0.0.0.0:18789 LISTENING
curl -s -o /dev/null -w "%{http_code}" http://100.68.184.107:18789/  # 应返回200
```

---

## 十六、官方文档参考

### 16.1 OpenClaw 官方文档

| 文档 | URL | 说明 |
|------|-----|------|
| OpenClaw Docs（主站） | `https://docs.openclaw.ai/` | 官方主文档 |
| OpenClaw Docs（中国镜像） | `https://docs.openclaw.ac.cn/` | 中文文档 |
| OpenClaw 社区文档 | `https://clawdocs.org/` | 社区驱动文档 |
| OpenClaw 文档站2 | `https://openclawdoc.com/` | 第三方文档 |

**关键命令参考**：
```bash
openclaw --version          # 版本检查
openclaw doctor             # 健康检查
openclaw gateway run        # 启动gateway
openclaw gateway status     # 查看状态
openclaw gateway restart    # 重启
openclaw agents add <name>  # 添加agent
openclaw cron list          # 查看cron
openclaw cron add           # 添加cron
openclaw backup create      # 创建备份
openclaw backup --help      # 备份帮助
openclaw config get <key>   # 获取配置
openclaw config set <key> <value> --json  # 设置配置
openclaw onboard            # 初始化引导
```

### 16.2 飞书开放平台文档

| 文档 | URL | 说明 |
|------|-----|------|
| 开发文档首页 | `https://open.feishu.cn/document/home/index?lang=zh-CN` | 入口 |
| 机器人概述 | `https://open.feishu.cn/document/client-docs/bot-v3/bot-overview?lang=zh-CN` | Bot开发指南 |
| 自定义机器人 | `https://open.feishu.cn/document/client-docs/bot-v3/add-custom-bot?lang=zh-CN` | 群内webhook机器人 |

**飞书开发关键点**：
1. 在 open.feishu.cn 创建企业自建应用
2. 配置事件订阅（`im.message.receive_v1`）
3. 开启群消息权限（`获取群组中所有消息`）
4. 长连接模式无需webhook地址
5. 机器人间不触发webhook

### 16.3 其他工具文档

| 工具 | 文档 |
|------|------|
| lark-cli | WorkBuddy内置skill（lark-* 系列） |
| faster-whisper | `https://github.com/SYSTRAN/faster-whisper` |
| whisper.cpp | `https://github.com/ggerganov/whisper.cpp` |
| moviepy v2 | `https://github.com/Zulko/moviepy` |
| Playwright | `https://playwright.dev/` |
| yt-dlp | `https://github.com/yt-dlp/yt-dlp` |

---

## 十七、技能与插件清单

### 17.1 已安装 OpenClaw Skills（227个文件，14个skill包）

通过 `rsync` 从锋哥端同步到OpenClaw端，存放在 `~/.openclaw/workspace/skills/`。

核心skill：
| Skill | 用途 |
|-------|------|
| luhmann-book | 卢曼卡片榨书法（读书笔记） |
| luhmann-reflect | 卢曼反思法（个人处境分析） |
| nuwa-skill（女娲） | 人物skill蒸馏生成 |
| knowledge-ip-coach | Dan Koe内容创作系统 |
| truman-perspective | Truman创业视角 |

### 17.2 WorkBuddy 端 Skills

| Skill | 用途 |
|-------|------|
| lark-im | 飞书即时通讯 |
| lark-calendar | 飞书日历 |
| lark-doc | 飞书云文档 |
| lark-drive | 飞书云空间 |
| lark-base | 飞书多维表格 |
| lark-sheet | 飞书电子表格 |
| lark-slides | 飞书幻灯片 |
| lark-task | 飞书任务 |
| lark-vc | 飞书视频会议 |
| lark-minutes | 飞书妙记 |
| lark-whiteboard | 飞书画板 |
| lark-wiki | 飞书知识库 |
| lark-mail | 飞书邮箱 |
| lark-contact | 飞书通讯录 |
| lark-event | 飞书事件订阅 |
| lark-approval | 飞书审批 |
| lark-attendance | 飞书考勤 |
| lark-shared | 飞书共享基础 |
| lark-openapi-explorer | 飞书OpenAPI探索 |
| lark-skill-maker | lark-cli skill创建 |
| openclaw-setup | OpenClaw配置 |
| openclaw-troubleshoot | OpenClaw故障排查 |
| finance-data-retrieval | 金融数据检索 |
| neodata-financial-search | 金融数据搜索 |

### 17.3 OpenClaw Plugins

- **feishu-bot-chat-plugin**（Leochens/feishu-bot-chat-plugin）：群agent互@插件
  - 关键权限：`im:message.group_at_msg.include_bot:readonly`
  - 3个hook：before_prompt_build、message_sending、inbound_claim
  - WorkBuddy端不适用

---

## 十八、关键密码与 Token 汇总

> ⚠️ 以下为运维Agent必须掌握的凭据，请妥善保管。

### 18.1 飞书

| 项目 | 值 |
|------|-----|
| 锋哥bot App ID | `cli_a9561ba885f9dcc2` |
| OpenClaw/Star bot App ID | `cli_a9550e716278dbc3` |
| newbot (open) App ID | `cli_a960a91e13f81ccd` |
| 飞书CLI自带bot App ID | `cli_a95463efa0b81bd7` |
| 群chat_id | `oc_b67031872aa8ade8d6ae607d5f65a3a6` |
| Star open_id | `ou_9ec4ba11b85fbaed0bc7821d41ee74dc` |

### 18.2 通信桥

| 项目 | 值 |
|------|-----|
| Bridge API端点 | `POST http://127.0.0.1:18789/v1/chat/completions` |
| Bridge模型名 | `openclaw/bridge` |
| Bridge Bearer token | `7cbd90688b05a2cb6a7b58ff21185454681ecbdb1208101e` |

### 18.3 Notion

| 项目 | 值 |
|------|-----|
| Token | `[NOTION_TOKEN_ENV]` |
| API版本 | `Notion-Version: 2022-06-28` |
| 支出库ID | `56ae3f43-3d0f-4673-95af-21b1ea96121d` |

### 18.4 Git

| 项目 | 值 |
|------|-----|
| 仓库 | `git@github.com:rf2025up/aios.git` |
| Git user.name | 锋哥 |
| Git user.email | fengge@openclaw.ai |

### 18.5 MemOS

| 项目 | 值 |
|------|-----|
| Embedding Provider | MiniMax |
| Embedding Model | text-embedding-3-small |
| Summarizer Provider | MiniMax |
| Summarizer Model | MiniMax-M2.7 |

### 18.6 已失效的凭据

| 项目 | 状态 |
|------|------|
| DashScope API Key `sk-086a...` | ❌ 已删除（导致openclaw崩溃） |
| rf-lenovic OpenClaw | ⚠️ 已停用 |
| Hermes飞书bot | ⚠️ 已停用 |

---

## 十九、时间线（按日）

### 2026-04-12（WorkBuddy启用首日）
- 首次使用WorkBuddy，建立SOUL.md/IDENTITY.md/USER.md
- 英语启蒙启动（牛津树校园拓展版，庆爸大循环法）
- 大航海3个月业绩增长挑战启动

### 2026-04-13
- 周会机制建立
- 需求拦截协议雏形

### 2026-04-14
- AI-OS共享资产迁移（52个文件，11230行）
- 创建aio.git GitHub私有仓库
- VPS部署Hermes环境
- 飞书集成依赖安装（lark-oapi 1.5.3, websockets 16.0）
- Debian 12 PEP 668限制 → 用venv `/opt/feishu-venv`

### 2026-04-15
- 飞书机器人创建（锋哥bot App ID: cli_a9561ba885f9dcc2）
- 飞书群「万山无阻@及锋而试」建立
- 飞书群联调：@消息OK，不@消息不触发（权限≠事件规则）
- 峰哥↔Hermes同步协议v1.0编写
- MEMORY.md精简（420+行→130行）

### 2026-04-16 ~ 2026-04-18
- 双端协议迭代
- Skill安装和测试
- 业务分析（周会纪要、家长沟通）

### 2026-04-19
- AI协作终极决策分析
- 锋哥协作全景MECE报告
- OpenClaw议题讨论（10个议题）

### 2026-04-20
- 大航海核心战役框架确定
- 能力链7环确认
- 文档归档协议v1.0建立
- WorkBuddy文档总打包（116个文件）

### 2026-04-21
- **OpenClaw Linux版全量修复**（4轮SSH直改，14+文件）
  - jobs.json全量修复（6个cron）
  - Git remote HTTPS→SSH
  - Bridge agent创建 + SSH隧道
  - 14个Skill rsync同步（227个文件）

### 2026-04-22
- AI-OS双端同步技术方案v1.0
- 双端协同协议全新编写
- Cron防误判修复（"零日志"问题）
- 格言约束修复
- 定时提醒迁移方案编写（4个cron迁移）

### 2026-04-23
- **Hermes正式停用**，所有职责由OpenClaw承接
- GBrain记忆设计6项改进方案
  1. ✅ 强制记忆读取
  2. ✅ 变更日志
  3. ✅ 梦境周期cron
  4. ✅ 幂等同步
  5. ✅ 信号捕获规则
  6. ✅ 飞书群同步
- OpenClaw同步差异审计报告

### 2026-04-24
- 知识管理三层体系确立（TODO/TOPICS/MEMORY）
- core/TODO.md创建（唯一任务真相源）
- core/TOPICS.md创建（议题积累）
- OpenClaw启动崩溃修复（nvm路径 + apiKeys字段）

### 2026-04-25
- **OpenClaw迁移Linux→Windows 32G主机**
  - `openclaw backup create --verify`
  - Mac中转传输备份
  - Windows上恢复
  - 验证功能
- MemOS v1.0.8安装（5个坑）

### 2026-04-26
- MemOS + GBrain安装配置全记录整理
- Windows OpenClaw远程访问配置整理
- 托管厨房飞书Agent需求文档
- 直播转文字技术方案
- Git push自动同步任务文档

### 2026-04-27（今天）
- 全量运维知识背景说明整理（本文档）
- OpenClaw Gateway崩溃重启（5个坑：锁文件残留、计划任务PATH、SSH进程不驻留、auth模式限制、CORS白名单）
- 整理完整重启SOP写入文档（第15.14节）

---

## 附录：关键源文档索引

| 文档 | 路径 | 重要性 |
|------|------|--------|
| AI-OS双端协同协议 v5.0 | `AI-OS双端协同协议.md` | ⭐⭐⭐ 宪法级 |
| 双端同步技术方案 v1.0 | `AI-OS双端同步技术方案_v1.0_20260422.md` | ⭐⭐ |
| GBrain双端同步改进 | `文档库/GBrain记忆设计借鉴_双端同步改进_20260423.md` | ⭐⭐ |
| 双端同步实施计划 | `文档库/双端同步实施计划_GBrain版_20260423.md` | ⭐⭐ |
| OpenClaw同步差异审计 | `文档库/OpenClaw同步差异审计_20260423.md` | ⭐⭐ |
| OpenClaw配合事项清单 | `文档库/双端同步_OpneClaw配合事项清单_20260423.md` | ⭐⭐ |
| 迁移方案 Linux→Windows | `workspace/OpenClaw迁移方案-Linux到Windows.md` | ⭐⭐ |
| MemOS+GBrain全记录 | `core/inbox/MemOS-GBrain安装配置全记录_20260426.md` | ⭐⭐ |
| Windows远程访问配置 | `core/inbox/Windows-OpenClaw远程访问配置_20260426.md` | ⭐⭐ |
| 直播转文字技术方案 | `core/inbox/直播转文字技术方案.md` | ⭐ |
| Git push配置 | `core/inbox/git-push-setup.md` | ⭐ |
| 定时提醒迁移方案 | `定时提醒迁移方案_给Hermes.md` | ⭐ |
| 峰哥Hermes同步协议 | `峰哥Hermes同步协议.md` | ⭐（历史参考） |
| 联调报告 | `AI-OS双端同步联调报告_20260415.md` | ⭐（历史参考） |
| 飞书依赖状态报告 | `WorkBuddy文档总打包/.../2026-04-14-feishu-dependency-status.md` | ⭐（历史参考） |
| 厨房Agent需求文档 | `core/inbox/托管厨房飞书Agent需求文档_20260426.md` | ⭐ |
| 文档归档协议 | `文档库/📋_文档归档协议.md` | ⭐ |
| 犯错复盘录 | `.workbuddy/memory/ERRORS.md` | ⭐⭐ |
| MEMORY.md（长期记忆） | `.workbuddy/memory/MEMORY.md` | ⭐⭐⭐ |

---

*本文档由锋哥于2026-04-27整理，覆盖2026-04-12至2026-04-27全部技术运维经验。*
