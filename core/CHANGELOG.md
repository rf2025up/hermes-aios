# 变更日志（CHANGELOG）

> 每次锋哥通过SSH修改OpenClaw文件后，必须在这里记一条。
> OpenClaw每次cron执行时先读这个文件，知道最近被改了什么。

## 2026-04-23

- [锋哥] jobs.json：4个业务cron（晨间三件事/午间对焦/周日复盘）添加强制记忆读取前缀（改进1：大脑优先查找）
- [锋哥] jobs.json：统一记忆路径为 ~/.openclaw/workspace/MEMORY.md（编译真相）+ ~/.openclaw/workspace/memory/（时间线）
- [锋哥] core/CHANGELOG.md：新建本文件（改进2：变更检测）
- [锋哥] jobs.json：新增梦境周期cron（21:30），silent模式，记忆整理（改进3）
- [锋哥] 幂等同步确认——改进1的强制前缀已覆盖git pull失败报告（改进4）
- [锋哥] core/SOUL.md：追加信号捕获规则（改进5）
- [锋哥] 飞书群同步机制确认已建立（改进6）
- [锋哥] MEMORY.md：三段式需求拦截协议修正（需求质疑/本质思考/推进行动）
- [锋哥] MEMORY.md：能力链7环框架确认

## 2026-04-22

- [锋哥] jobs.json：晚间复盘+午间对焦加防误判指令
- [锋哥] DUAL-STACK-RULES-v2.md：双端协议全新编写

## 2026-04-21

- [锋哥] MEMORY.md全量覆盖（OpenClaw覆盖了锋哥版本）
- [锋哥] jobs.json 6个cron全量修复（加git pull+修路径+调timeout）
- [锋哥] 全量同步：skills/prompts/reports/about-me 通过SCP/rsync
- [锋哥] Git remote HTTPS→SSH切换
- [锋哥] bridge agent创建 + SOUL-bridge.md + SSH隧道配置
