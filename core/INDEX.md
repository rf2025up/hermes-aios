# AIOS 业务主线版索引

> 最后更新: 2026-05-11（v2业务主线版）
> 用途：每次新session读这个文件，知道去哪找什么。

---

## 🔧 运维备忘录（OPS-MEMO.md）

> **系统出问题时先查这个文件**：技术架构、API配置、Key管理、Gateway重启、ClawMem、Notion记账、故障排查速查。

## 🔥 每次对话必读

| 文件 | 路径 | 作用 |
|------|------|------|
| BUSINESS-SOUL.md | core/BUSINESS-SOUL.md | 业务主控台身份+判断铁律+管理动作系统 |
| MEMORY.md | ~/.hermes/memories/MEMORY.md | 长期记忆（自动注入） |
| USER.md | core/USER.md | 锋哥偏好和习惯 |
| TODO.md | core/TODO.md | 任务清单 |

## 🎯 主战役驾驶舱

| 文件 | 路径 | 作用 |
|------|------|------|
| ACTIVE_TASK.md | core/ACTIVE_TASK.md | 当前唯一主战役+阶段目标+关键战场 |
| THIS_WEEK_TOP3.md | core/THIS_WEEK_TOP3.md | 本周3个业务动作+3个管理重点 |
| SCOREBOARD.md | core/SCOREBOARD.md | 6层指标看板（北极星→招生→交付→管理→纪律→节点） |

## 💼 业务文档

| 文件 | 路径 | 作用 |
|------|------|------|
| DECISIONS.md | core/DECISIONS.md | 关键决策记录（含执行状态） |
| PEOPLE.md | core/PEOPLE.md | 学生/家长/老师跟进表 |
| 幼小衔接完整方案.md | core/business/01_幼小衔接/ | 幼小衔接招生方案 |

## 📁 目录结构

```
core/
├── BUSINESS-SOUL.md     # 业务主控台身份
├── ACTIVE_TASK.md       # 当前主战役
├── THIS_WEEK_TOP3.md    # 本周重点
├── SCOREBOARD.md        # 数字看板
├── TODO.md              # 任务清单
├── DECISIONS.md         # 决策记录
├── PEOPLE.md            # 人物跟进
├── INDEX.md             # 本文件
├── CHANGELOG.md         # 变更日志
│
├── business/            # 业务文档（按战场分）
│   ├── 01_幼小衔接/
│   ├── 02_招生增长/
│   ├── 03_家长沟通/
│   ├── 04_体验课转化/
│   ├── 05_朋友圈宣传/
│   ├── 06_老师管理/
│   ├── 07_托管交付/
│   ├── 08_续费准备/
│   ├── 09_暑假班/
│   ├── 10_现场管理/
│   └── 11_会议驱动结果/
│
├── runtime/             # 运行时记录
│   ├── daily/           # 每日日志
│   ├── weekly/          # 周报
│   ├── meetings/        # 会议纪要
│   ├── inspections/     # 巡查记录
│   └── followups/       # 跟进记录
│
├── assets/              # 可复用资产
│   ├── scripts_话术/
│   ├── sop_流程/
│   ├── templates_模板/
│   ├── cases_案例/
│   └── posts_朋友圈/
│
├── inbox/               # 原始素材（待处理）
│
├── ARCHIVE/             # 已归档（v2升级前的非业务文件）
└── backups/             # 备份
```

## ☁️ 飞书云文档

| 文档 | 用途 | 链接 |
|------|------|------|
| AIOS驾驶舱 | 主战役状态+6关键数字 | DkKEdWvbYoK1qfxk3MEcP0cjnbf |
| AIOS顶层文档 | 知识库（8章节） | UFTkdwXzcoBbucxX62rcjIPfnOg |

## 📦 归档位置

v2升级前的非业务文件已归档到：
- **本地**: `core/ARCHIVE/`
- **H盘**: `H:\Hermes\v2升级归档\`（含归档清单.md）

## 🔑 关键规则

- 日志路径: `core/runtime/daily/YYYY-MM-DD.md`（顶部必须有⚡关键进展区块）
- 记账走Notion（不走daily）
- 核心文件改动必须锋哥确认
- SOUL.md（.hermes/）= 系统级 | BUSINESS-SOUL.md（core/）= 业务身份副本
