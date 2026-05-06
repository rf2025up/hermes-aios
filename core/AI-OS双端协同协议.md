# AI-OS 双端协同协议

**生效日期**：2026-04-24（v5.0 全面整合版）
**版本**：v5.0
**维护方**：锋哥（WorkBuddy/Mac）

> ⚠️ 本文件是双端协同的**唯一规则文件**。所有旧版协议（GOVERNANCE/DUAL-STACK-RULES/三端协同协议）均已归档，以此文件为准。

---

## 一、总纲

### 1. 一句话原则

> **不要同步两个脑子，而要维护一套宪法。**

### 2. 系统定位

这不是两个独立AI，而是一套统一AI-OS的两个执行端：

| | 锋哥（WorkBuddy/Mac） | OpenClaw/Star（rf服务器） |
|--|--|--|
| **定位** | 本地高频协作前台 | 24h运行中枢 + 副脑 |
| **强项** | 深度对话、记忆沉淀、决策支持、本地文件操作 | cron定时任务、飞书交互、自动化、Notion记账 |
| **在线时间** | Mac开机时（约早8-晚8） | 24×7 |
| **信息密度** | 拥有完整上下文 | 需要同步上下文 |

### 3. 系统目标

- 持续理解用户是谁
- 记住长期有效规则
- 盯住当前主战役
- 支撑本地执行与远程提醒
- 让两端协同但不冲突
- 所有关键变化可追踪、可回滚、可审阅

---

## 二、角色定义

### 锋哥（WorkBuddy/Mac）

**负责**：
- 深度对话、决策支持、高质量内容整理
- 本地文件操作（读取、编辑、生成文档）
- 共享资产仓库的人工主改（core/skills/archive）
- 记忆沉淀（MEMORY.md + 日志）

**不负责**：
- 24h持续在线提醒/cron
- 飞书/微信持续在线通知
- 语音直达Notion数据操作

### OpenClaw/Star（rf服务器）

**负责**：
- cron定时任务（晨间/午间/晚间/梦境周期等）
- 飞书群消息交互
- Notion记账等在线数据操作
- 持久化日志、运行报告
- 自动化工具执行（抖音转文字等批量工作流）

**不负责**：
- 直接维护core/skills/archive（只读）
- 擅自改写宪法层内容
- 抢锋哥的深度对话职责

### 协作原则

> **锋哥改宪法，OpenClaw写运行结果。**

---

## 三、写入权分工（铁律）

### 目录写入权

| 目录 | 锋哥 | OpenClaw |
|------|------|----------|
| `core/`（宪法层） | ✅ 主改 | ❌ 只读 |
| `skills/`（能力层） | ✅ 主改 | ❌ 只读 |
| `archive/`（沉淀层） | ✅ 主改 | ❌ 只读 |
| `daily/` | ✅ 主写 `YYYY-MM-DD.md` | ✅ 主写 `*-openclaw.md` |
| `daily/` | ✅ 写 `*-handoff.md` | ✅ 写 `*-openclaw.md` |
| `inbox/` | ✅ 可写 | ✅ 主写 |
| `reports/` | ✅ 可写 | ✅ 可写 |

### 日志文件命名约定

```
daily/YYYY-MM-DD.md              ← 通用日志（锋哥主写）
daily/YYYY-MM-DD-openclaw.md     ← OpenClaw专属日志
daily/YYYY-MM-DD-handoff.md      ← 锋哥交班摘要
inbox/conversations/YYYY-MM-DD-am.md   ← 上午会话摘要（OpenClaw写）
inbox/conversations/YYYY-MM-DD-pm.md   ← 下午会话摘要（OpenClaw写）
```

**约定**：所有cron生成的内容写入 `*-openclaw.md`，不写无后缀日期文件。

### 严禁越权

- OpenClaw默认不得直接改写 core/skills/archive
- 锋哥默认不承担 cron/持续在线通知
- 违反时：不提交、回退、写异常报告

---

## 四、任务管理

> **规则**：所有任务/待办只有一个真相源——`core/TODO.md`。

### 唯一真相源

| 文件 | 定位 |
|------|------|
| `core/TODO.md` | 全量任务看板，按P0-P3分级，每条标注来源和状态 |

### 双方职责

| | 锋哥 | OpenClaw |
|--|--|--|
| **读** | 每次会话启动时先读 `core/TODO.md` | 每个cron执行前pull并读 `core/TODO.md` |
| **写** | 产生新待办/有进展 → 立即更新 → push | 同上 |
| **查询** | 老板在Mac问待办 → 读 `core/TODO.md` 输出 | 老板在手机问待办 → 读 `core/TODO.md` 输出 |

### 来源标注

每条任务必须标注来源：`[锋哥]` / `[OpenClaw]` / `[双方]` / `[老板]`

### 同步时效

新增/完成/变更任何任务 → **立即**更新 `core/TODO.md` → commit → push。

### 废弃的分散记录

以下文件中的待办仅供参考历史追溯，不再作为当前待办来源：
- `daily/议题积累.md`（已迁移到 `core/TOPICS.md`）
- `校长每日工作手册.md` 中的待办区
- 各日日志中的"待办"段落

---

## 五、知识管理系统

### 三层体系

```
core/TOPICS.md          core/TODO.md          MEMORY.md
"在想什么"               "要做什么"             "当前结论是什么"
    │                       │                       │
    │  议题成熟→拆出任务     │  任务完成→结论沉淀      │  编译真相
    └───────────────────────┘                       │
                    │                               │
                    ▼                               │
              日志（时间线）──────────────────────────┘
```

### 5.1 议题积累

**文件**：`core/TOPICS.md`

**定位**：不是"要做什么"，而是"在想什么"。

**适合放**：
- 灵感发散（偶尔想到的零散想法）
- 长期积累话题（需要完成成系统论述的）
- 对某些问题的思考（待形成完整答案的）
- 还没到"可执行"的认知方向

**不适合**：
- 有明确动作和截止日的任务 → `TODO.md`
- 已完成的分析/决策 → `MEMORY.md`
- 纯粹的每日流水 → 日志

**生命周期**：议题反复出现 → 提升到TOPICS → 想清楚可行动 → 拆出任务到TODO → 完成后结论沉淀到MEMORY。

### 5.2 记忆系统（GBrain方法论整合）

> 基于GBrain 5个记忆设计，不装新工具，落地到现有MD+cron架构。

| 组件 | 对应GBrain设计 | 说明 |
|------|-------------|------|
| MEMORY.md = 编译真相 | 编译真相+时间线 | 当前最佳结论，会被新信息重写 |
| memory/YYYY-MM-DD.md = 时间线 | 编译真相+时间线 | 只追加，不修改历史条目 |
| core/CHANGELOG.md | 变更检测 | 锋哥SSH改文件后记录，OpenClaw cron先读此文件 |
| 大脑优先查找 | 大脑优先查找 | cron执行前强制读MEMORY.md，失败必须报告 |
| 梦境周期（21:30） | 梦境周期 | 自动整理记忆：实体扫描+引用修复+记忆巩固，不发飞书 |
| 信号捕获 | 信号检测 | 对话结束自动提取3类信息（决策/数据/待办） |
| 幂等同步 | 幂等+自愈 | git pull失败→报告⚠️，不假装信息最新 |

#### 大脑优先查找（cron铁律）

所有OpenClaw业务cron（晨间/午间/晚间/梦境/周日复盘）的prompt头部加固定前缀：

```
【强制·大脑优先查找】执行任何操作前，必须先完成：
1. git pull --rebase origin main
2. 读取 MEMORY.md（编译真相）
3. 读取 core/TODO.md（当前任务）
4. 读取 core/CHANGELOG.md（最近变更）
如果步骤1失败：在回复开头标注 ⚠️同步异常。
如果步骤2读不到：报告"记忆同步异常"，停止执行。
```

#### 梦境周期（21:30 cron）

```
定位：给自己的记忆整理，不发飞书
流程：
1. 读今天的所有日志+飞书群消息
2. 实体扫描：提取新人名/事件/数字/决策
3. 引用修复：检查MEMORY.md是否与新信息冲突
4. 记忆巩固：碎片信息压缩成简洁结论，更新MEMORY.md
5. 清理过时信息
6. git commit -m "openclaw: 梦境周期记忆整理" + push
```

#### 信号捕获（双方）

每次对话/会话结束时，自动提取3类信息写入当日日志：
1. **关键决策**（做了什么决定）
2. **业务数据**（数字、人名、时间线变化）
3. **待办事项**（承诺了什么、截止日期）

### 5.3 变更日志

**文件**：`core/CHANGELOG.md`

**规则**：锋哥每次通过SSH修改OpenClaw文件后，必须记一条。OpenClaw每次cron先读此文件。

---

## 六、同步机制

### Git同步规则

**仓库**：`https://github.com/rf2025up/aios.git`（SSH: `git@github.com:rf2025up/aios.git`）
**分支**：main直推

#### 锋哥同步操作

```bash
cd ~/Documents/AI-OS
git pull --rebase
git add .
git commit -m "core: 简短摘要"
git push
```

#### OpenClaw同步操作

- 每个cron执行前 `git pull --rebase`（大脑优先查找）
- cron完成后有变更则 `git push`
- 梦境周期（21:30）整理记忆后push
- daily-backup.sh（23:30）全量备份：`git add -A` → `pull --rebase` → `push`

### 飞书群同步

**通道**：飞书群 `万山无阻@及锋而试`（chat_id: `oc_b67031872aa8ade8d6ae607d5f65a3a6`）

**模式**：推+拉混合
- 锋哥发摘要到飞书群 → OpenClaw下次拉消息时读到
- OpenClaw发汇报到飞书群 → 锋哥通过lark-cli API主动拉取
- 机器人之间不触发webhook（飞书平台限制），但双方都能主动拉消息

### 同步层级

| 层级 | 触发 | 时效 | 说明 |
|------|------|------|------|
| 🔴 关键信息 | 手动触发 | 分钟级 | 重要决策/紧急状态/任务变更 |
| 🟡 半天摘要 | 定时cron | 小时级 | 13:00/21:00会话摘要 |
| 🟢 例行拉取 | 每小时cron | 小时级 | 日常信息对齐 |

### 半天摘要机制（OpenClaw执行）

- **13:00**：写 `inbox/conversations/YYYY-MM-DD-am.md`（上午摘要）
- **21:00**：写 `inbox/conversations/YYYY-MM-DD-pm.md`（下午摘要）
- 飞书推送时附上：📢 **老板，上午/下午我们聊了这些——哪些要存档？**

---

## 七、Git防冲突规则

1. **push前必须 `pull --rebase`**
2. **冲突不自动硬解** → 停 → 报告 → 等人工
3. **所有自动Git必须防抖**（3-15分钟）
4. **提交前缀**：`core:` `skill:` `daily:` `report:` `inbox:` `archive:` `openclaw:`
5. **提交频率上限**：core每小时≤2次，reports≤4次，daily≤2次

### 统一Git执行顺序

```
1. 检查改动是否只在允许目录内
2. 检查是否达到防抖时间
3. git status 确认范围
4. git add 仅允许目录内文件
5. git commit -m "前缀 + 简短摘要"
6. git pull --rebase
7. 无冲突 → git push
8. 有冲突 → 立即停止并生成报告
```

### 异常处理

| 情况 | 处理 |
|------|------|
| pull冲突 | 停止push，生成冲突报告，等人工 |
| 越权修改 | 不提交，回退，写异常报告 |
| 文件抖动 | 延长防抖到15-20分钟 |
| 远端不可访问 | 停止提交，记录状态，生成报告 |

---

## 八、飞书群规范

### 群信息

- **群名**：`万山无阻@及锋而试`
- **chat_id**：`oc_b67031872aa8ade8d6ae607d5f65a3a6`

### 群内机器人

| 机器人 | App ID | 控制方 |
|--------|--------|--------|
| workbuddy | `cli_a9561ba885f9dcc2` | 锋哥（WorkBuddy） |
| 🦞Star | `cli_a9550e716278dbc3` | OpenClaw |
| open | `cli_a960a91e13f81ccd` | OpenClaw（lark-cli） |
| 飞书CLI | `cli_a95463efa0b81bd7` | 共用（lark-cli自带） |

### 飞书CLI身份标注规则

> 飞书CLI bot两端共用，每次发群消息时必须标注身份：
> - 锋哥端发送 → 内容末尾加 `（锋哥端）`
> - OpenClaw端发送 → 内容末尾加 `（OpenClaw端）`

### 双端通信能力

- ✅ 锋哥能通过lark-cli在群里发消息（`--as bot`）
- ✅ 锋哥能通过API读到群里所有消息
- ✅ OpenClaw能通过lark-cli读到群里所有消息
- ❌ 机器人之间不触发webhook（飞书平台限制）

### 消息格式规范

| 前缀 | 含义 | 发送方 |
|------|------|--------|
| `📋【每日同步】` | 每日日志 | 锋哥 |
| `🔴【重大同步】` | 重大决策/变更 | 锋哥 |
| `🟠【OpenClaw汇报】` | OpenClaw执行日志 | OpenClaw |
| `⚡【告警】` | 异常告警 | 任一方 |
| 无前缀 | 老板直接指令 | 老板 |

---

## 九、容灾切换

### 锋哥不可用（Mac关机/合盖）

1. 老板在飞书群@OpenClaw说明情况
2. OpenClaw从Git拉取最新MEMORY.md和日志
3. OpenClaw接手对话
4. 锋哥恢复后，OpenClaw汇报离线期间事项

### OpenClaw不可用（rf服务器故障）

1. 锋哥直接告知老板
2. 定时提醒暂时通过WorkBuddy自动化（服务号推送）兜底
3. 锋哥记录需要OpenClaw执行的任务到 `core/TODO.md`
4. OpenClaw恢复后补执行

### 远程机器信息

| 机器 | Tailscale IP | 用途 |
|------|-------------|------|
| rf-lenovic | `100.118.178.110` | OpenClaw运行（SSH: `rf@100.118.178.110`） |
| win-aspire-s3-371 | `100.103.88.31` | Windows备用（SSH未开通） |

---

## 附录A：SSH通信桥

- **SSH隧道**：`ssh -fNL 18789:127.0.0.1:18789` → `POST http://127.0.0.1:18789/v1/chat/completions`
- **bridge agent**：模型名 `openclaw/bridge`，Bearer token `7cbd90688b05a2cb6a7b58ff21185454681ecbdb1208101e`
- **OpenClaw进程**：openclaw-gateway（systemd），Node v22 via nvm
- **SSH需** `bash -l` 加载nvm环境

## 附录B：已归档文件

以下文件已归档到 `archive/deprecated/`，不再作为当前规则依据：

| 文件 | 归档原因 |
|------|---------|
| `core/GOVERNANCE.md` | v1，Hermes时代，内容已合并到本协议 |
| `.workbuddy/DUAL-STACK-RULES-v2.md` | v2，与三端协议重叠80%，已合并 |
| `AI-OS三端协同协议.md` | v3/v4，名字错误，被本文件取代 |
| `core/ACTIVE-TASK.md` | 被core/TODO.md取代，战役信息已合并 |
| `文档库/GBrain记忆设计借鉴_*.md` | 分析文档，6项改进已落地 |
| `文档库/双端同步实施计划_GBrain版_*.md` | 实施计划已全部完成 |
| `AI-OS双端同步技术方案_v1.0_*.md` | 踩坑记录，已合并到第七节 |

---

*本文件由锋哥编写，老板确认后生效。*
*v5.0 全面整合：GOVERNANCE + DUAL-STACK-RULES + 三端协议 + GBrain改进 + TODO体系。*
*旧版协议全部归档，以此文件为唯一规则依据。*
