# 个人Hermes系统审计·进度文件

> 创建：2026-05-09 00:40
> 本轮只做审计不修改。任务拆为8步，第1步已完成（信息收集），剩余7步待new后继续。

---

## 已收集的核心数据摘要

### 1. 目录结构

```
/root/.hermes/                          ← Hermes Home
├── config.yaml (386行) 主配置
├── .env (16行) API密钥
├── auth.json (111行) 凭证池
├── SOUL.md (222行) .hermes层SOUL（更完整版）
├── memory_store.db (ClawMem SQLite)
├── cron/jobs.json (8个定时任务)
├── skills/productivity/ (12个skill: 5自建+7内置)
└── hermes-agent/ (源码)

/root/workspace/aios/core/ (55个md文件, 18027行)
├── INDEX.md (114行) 索引中心
├── SOUL.md (141行) core层SOUL（比.hermes版少）
├── MEMORY.md (148行) 长期记忆
├── USER.md 用户偏好
├── TODO.md (123行) 任务看板
├── SCOREBOARD.md (78行) 业务指标
├── TOPICS.md (218行) 议题积累
├── CHANGELOG.md (29行, 最后更新4-23, OpenClaw时代)
├── DECISIONS.md (44行, 最后更新5-3)
├── IDENTITY.md (空文件!)
├── INFRA.md (153行, 过时, 仍指向旧VPS和OpenClaw)
├── OPERATING_SYSTEM.md (67行, 长期有效)
├── ROUTER.md (44行, WorkBuddy/OpenClaw时代产物, 过时)
├── COMMAND-TEMPLATES.md (41行, 4-14更新)
├── NOTION-RULES.md (100行, 仍标注"交由OpenClaw负责")
├── PEOPLE.md (47行, 学生跟进, 4-13后未更新)
├── OPENCLAW_SYNC_PROTOCOL.md (191行, OpenClaw已不用)
├── 人机协作指南.md (458行) 协作宪法
├── 认知清空指南.md (197行)
├── HERMES-WSL2-运维方案.md (1005行) 唯一运维文档
├── Hermes-WSL2-完整方案-已解决.md (172行, 旧版)
├── 幼小衔接完整方案.md (537行)
├── Agent记忆方案深度调研.md (412行)
├── 视频转文档项目文档.md (221行)
├── 视频转文档进度.md
├── 孩子教育Agent完整架构方案.md (504行)
├── 孩子教育Agent新人配置.md (1028行)
├── 双端协同设计v3.md
├── 全年直播内容沉淀与AI知识卡片工作流.md (1669行)
├── 一号位工作设计背后的思考指南.md (2743行, 最大文件)
├── 决心修炼AMCC.md (1344行)
├── OpenClaw全量备份方案.md
├── 4个UTF-8编码乱码文件
├── 12+个OpenClaw迁移期历史文件(已标注不活跃)
├── daily/ (21个md, 2026-04-15起)
├── inbox/ (8个md)
├── backups/ (空)
└── 凌霄方案/ (4个md)

/root/workspace/aios/scripts/ (8个py)
├── paraformer_batch_v3.py ← 当前主力
├── paraformer_batch_v3_timeout.py
└── 6个旧版/测试脚本

/mnt/h/Hermes/ ← Windows同步目录(约20个文件)
```

### 2. config.yaml 摘要

- 主模型: glm-5-turbo (zai)
- Fallback: qwen3.6-plus → deepseek-v4-flash (custom:bailian)
- 飞书: websocket模式, app_id=cli_a97996259a7a1cd4
- Vision: alibaba/qwen-vl-plus
- Memory: clawmem, 2200字限制
- Plugin: clawmem启用

### 3. Cron定时任务(8个)

| 任务 | 时间 | Deliver | 状态 |
|------|------|---------|------|
| 晨间三件事 | 8:00 周一-六 | origin(飞书) | ok |
| 午间对焦 | 13:00 周一-六 | origin | ok |
| 想法池推送 | 15:50 周一-六 | origin | 未运行过 |
| 梦境周期 | 21:30 每天 | local | ok |
| 晚间双向复盘 | 22:00 周一-六 | origin | ok |
| 每日Git备份 | 22:30 每天 | local | ok |
| 每小时自动转写 | 整点 | local+terminal | ok(48次) |
| 周日复盘 | 9:00 周日 | origin | 未运行过 |

### 4. Skills(12个)

自建5个: aios-core-governance, audio-transcription, knowledge-production, notion, feishu-doc-api
内置7个: powerpoint, ocr-and-documents, nano-pdf, maps, linear, google-workspace, airtable

### 5. 关键发现

- **两份SOUL.md不一致**: core/(141行) vs .hermes/(222行), .hermes版更全
- **ROUTER.md过时**: 仍按WorkBuddy/OpenClaw分工, Hermes已是唯一主中枢
- **INFRA.md过时**: 指向旧VPS(74.48.186.223)和OpenClaw配置
- **NOTION-RULES.md过时**: 仍标注"交由OpenClaw负责"
- **CHANGELOG.md停在4-23**: OpenClaw时代, Hermes时代无更新
- **DECISIONS.md部分过时**: 5-3的"memos替代MEMORY"决策未执行
- **IDENTITY.md空文件**: 存在但无内容
- **4个UTF-8乱码文件**: Windows→WSL2编码问题
- **12+个OpenClaw迁移期文件**: INDEX已标注不活跃但仍存在
- **转写脚本3版本共存**: v1/v2/v3
- **config.yaml暴露飞书app_secret**: 明文
- **教育Agent独立机器**: rf-edu-agent@100.122.213.77
- **主key欠费**: sk-128...033 Arrearage, 备用key正常
- **当前人数**: 30人(目标46→70)

### 6. .hermes/SOUL.md 关键规则摘要

- 名字: 直击本质, 叫锋哥
- 反高级逃避协议(最高优先级): 72小时铁律
- 业务沉迷机制迁移(5要素)
- 需求拦截协议(3问30秒)
- 从信息到结果7问链路
- 能力链7环
- 时间边界: 22:30后叫停
- 议题沉淀三层管道
- 一句话: "AI是放大器不是主线"

---

## TODO进度(8步)

1. ✅ 信息收集
2. ✅ 第一章(定位) + 第二章(需求全景) ← 01:10
3. ✅ 第三章(文件文档结构审计) + 第四章(记忆系统) ← 01:15
4. ✅ 第五章(自动化定时任务) + 第六章(任务路由) + 第七章(上手机制) ← 01:18
5. ✅ 第八章(进化机制) + 第九章(痛点) + 第十章(已有效机制) ← 01:20
6. ✅ 第十一章(v2材料清单) + 第十二章(给设计者摘要) ← 01:22

**全部完成。** 报告在 /mnt/h/Hermes/个人Hermes系统现状审计报告v1.md

每步输出追加写入 /mnt/h/Hermes/个人Hermes系统现状审计报告v1.md

---

## 锋哥需求全景(已在H盘)

/mnt/h/Hermes/锋哥需求全景图.md — 51个业务需求+10个技术运维需求
