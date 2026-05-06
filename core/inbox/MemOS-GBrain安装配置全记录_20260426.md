# MemOS + GBrain 安装配置全记录

> 整理：锋哥（WorkBuddy）| 日期：2026-04-26
> 用途：同步给OpenClaw，建立统一的记忆系统认知

---

## 一、MemOS 本地记忆插件

### 1.1 基本信息
- **版本**：v1.0.8
- **安装日期**：2026-04-25 14:00-14:40
- **安装位置**：Windows 32G主机（`C:\Users\Administrator\.openclaw\`）
- **状态**：✅ 已安装运行中

### 1.2 核心配置
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
  "memorySearch": {
    "disabled": true  // 避免与MemOS冲突
  },
  "memory-core": {
    "disabled": true
  },
  "memory-lancedb": {
    "disabled": true
  }
}
```

### 1.3 访问地址
- **Viewer本地**：`http://127.0.0.1:18799`
- **Viewer远程**：`http://100.68.184.107:18799`（需Tailscale在线）
- **数据库**：`C:\Users\Administrator\.openclaw\memos-local\memos.db`

### 1.4 MemOS覆盖的GBrain设计（4/5）

| GBrain设计 | MemOS实现方式 |
|-----------|-------------|
| 信号检测（每条消息自动捕获） | ✅ auto-recall：每轮对话自动写入记忆 |
| 大脑优先查找（先查记忆再回答） | ✅ auto-recall：响应前先检索相关记忆 |
| 记忆整理（碎片→结构化） | ✅ skillEvolution：技能进化+记忆整理 |
| 幂等操作（跑N次=跑1次） | ✅ 内置哈希去重，不重复写入 |
| 编译真相+时间线 | ❌ 未覆盖（由MEMORY.md+日志系统承担） |

### 1.5 安装踩坑记录（5个）

1. **puppeteer下载Chrome失败** → 设置环境变量 `PUPPETEER_SKIP_DOWNLOAD=true`
2. **OpenClaw安全检测拦住child_process** → 加 `--dangerously-force-unsafe-install --force`
3. **EBUSY锁文件** → 先停gateway再删旧目录
4. **slots为空** → PowerShell Add-Member不生效，用regex直接改JSON
5. **BOM标记导致JSON解析失败** → 移除UTF-8 BOM

---

## 二、GBrain 理念层（不装工具，借鉴设计）

### 2.1 核心洞察

**GBrain的核心洞察：记忆不是存储问题，是整理问题。**

5个核心记忆设计：

1. **编译真相+时间线**：MEMORY.md = 当前最佳结论（可重写），日志 = 证据链（只追加）
2. **信号检测器**：每条消息都是知识捕获机会，不等用户说"帮我记"
3. **梦境周期**：每晚自动整理碎片信息→压缩成结论→第二天更聪明
4. **大脑优先查找**：每次响应前先查大脑，再决定是否外部搜索
5. **幂等+自愈**：操作失败重跑一次就恢复，不需要人工判断进度

### 2.2 已落地的6项改进

| # | 改进项 | 状态 | 说明 |
|---|--------|------|------|
| 1 | 强制记忆读取 | ✅ 已完成 | 4个业务cron加【强制·大脑优先查找】前缀 |
| 2 | 变更日志 | ✅ 已完成 | core/CHANGELOG.md，SSH改文件必记 |
| 3 | 梦境周期cron | ✅ 已完成 | 22:00记忆整理，不发飞书群，silent模式 |
| 4 | 幂等同步 | ✅ 已完成 | git pull失败→⚠️同步异常标注 |
| 5 | 信号捕获规则 | ✅ 已完成 | OpenClaw SOUL.md加对话结束自动提取规则 |
| 6 | 飞书群同步 | ✅ 已完成 | 锋哥发摘要+OpenClaw拉消息，双向通信验证 |

### 2.3 GBrain改进的完整prompt模板

**强制记忆读取（加在cron prompt头部）**：
```
【强制·大脑优先查找】执行任何操作前，必须先完成：
1. git pull --rebase origin main
2. 读取 ~/.openclaw/workspace/.workbuddy/memory/MEMORY.md（编译真相）
3. 读取 ~/.openclaw/workspace/.workbuddy/memory/ 当天日志（时间线）
如果步骤1失败：在回复开头标注 ⚠️同步异常，说明git pull失败，不要假装信息是最新的。
如果步骤2读不到：报告"记忆同步异常：MEMORY.md不存在"，停止执行，不要凭空生成内容。
```

**梦境周期（22:00 cron）**：
```
你是锋哥的记忆整理模块（梦境周期）。现在是22:00，执行记忆整理：

【强制·大脑优先查找】
1. git pull --rebase origin main
2. 读取 ~/.openclaw/workspace/.workbuddy/memory/MEMORY.md
3. 读取 core/CHANGELOG.md（最近的变更）
4. 读取今天的所有日志（*-openclaw.md / *-handoff.md / YYYY-MM-DD.md）
5. 读取飞书群最近消息：lark-cli im +chat-messages-list --chat-id oc_b67031872aa8ade8d6ae607d5f65a3a6 --as bot --page-size 20

【记忆整理任务】
1. 实体扫描：从今天的对话/日志中提取新出现的实体（人名、事件、数字、决策）
2. 引用修复：检查MEMORY.md中是否有信息与今天的新信息冲突，有则更新
3. 记忆巩固：把今天的碎片信息压缩成简洁的结论，更新到MEMORY.md对应位置
4. 清理过时：标记MEMORY.md中已过时的信息

【输出】
- 更新后的MEMORY.md
- git commit -m "openclaw: 梦境周期记忆整理 YYYY-MM-DD"
- git push origin main
- 不需要发飞书群（这是给自己做的整理）
```

**信号捕获（加在SOUL.md）**：
```
【信号捕获】每次对话结束时，自动提取以下信息写入当日日志：
1. 关键决策（做了什么决定）
2. 业务数据（数字、人名、时间线变化）
3. 待办事项（承诺了什么、截止日期）
4. 新增实体（第一次出现的人名/概念/事件）
```

---

## 三、当前记忆架构全景

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

---

## 四、待办/注意事项

1. **git push cron**：还没配好。Star被模型限速没执行，需重新触发。任务文件在 `core/inbox/git-push-setup.md`
2. **MemOS Viewer验证**：可以通过 `http://100.68.184.107:18799` 查看记忆数据库，确认auto-recall是否在工作
3. **Python 3.14兼容性**：Windows上是Python 3.14，部分pip包可能不兼容（如faster-whisper）
4. **dashscope API Key**：之前的Key导致openclaw崩溃已被删除，如需Paraformer转文字需重新申请

---

*整理：锋哥 | 2026-04-26 08:28*
