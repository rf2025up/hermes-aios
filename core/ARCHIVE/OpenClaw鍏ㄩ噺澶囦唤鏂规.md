# OpenClaw 全量备份方案

> 2026-04-24 | 背景：运行OpenClaw的笔记本不稳定，出现过多次卡死需强制重启

---

## 一、问题

笔记本不定期卡死，存在以下风险：
1. **工作文件丢失**：对话中产生的文档、调研报告、脚本等可能未及时保存
2. **记忆断层**：memory/下的日志和MEMORY.md是跨会话记忆的唯一载体，丢了等于失忆
3. **交付物归零**：如昨晚跑的165个视频逐字稿（60万字），跑了2小时才完成，丢了要重来

## 二、现有机制

| 机制 | 频率 | 覆盖范围 | 问题 |
|------|------|---------|------|
| git-sync.sh | 每小时cron | 已跟踪文件 | 新文件可能漏掉，不处理大文件 |
| WorkBuddy双端同步 | WorkBuddy侧控制 | core/daily等共享目录 | 只同步指定目录 |
| GitHub仓库 | 持续 | rf2025up/aios | 两端共用，已有合并机制 |

## 三、方案：每日全量保底备份

### 3.1 核心原则
- **不替换现有同步**，只做保底兜底
- **不冲突双端协议**：使用同一个仓库，同一个分支，先pull再push
- **只同步文档类文件**（md/json/txt/py/sh/toml/yaml），大文件（视频/图片/压缩包）当天发老板后清理
- **提交前缀区分**：`daily-backup:` 前缀，与 `openclaw:` 和 `workbuddy:` 区分

### 3.2 备份范围

| 目录 | 内容 | 是否备份 |
|------|------|---------|
| memory/ | 每日日志、长期记忆 | ✅ 必须 |
| MEMORY.md | 长期记忆索引 | ✅ 必须 |
| skills/ | 所有Skill（含绿毛怪怪蒸馏） | ✅ 必须 |
| core/ | 方案文档、双端协议 | ✅ 必须（只读但备份） |
| daily/ | 每日记录 | ✅ 必须 |
| scripts/ | 工具脚本 | ✅ 必须 |
| 为何小姐/ | 165篇逐字稿（60万字） | ✅ 必须 |
| inbox/ | 灵感收集 | ✅ 必须 |
| TOOLS.md / AGENTS.md / SOUL.md 等 | 系统配置 | ✅ 必须 |
| *.mp4 / *.mp3 / 大图片 | 媒体文件 | ❌ 当天发老板后清理 |

### 3.3 执行机制

**每日23:30**（晚间收口之后）自动执行：

```
1. git pull --rebase origin main    ← 先拉WorkBuddy的最新内容，避免冲突
2. git add -A                        ← 强制添加所有新文件
3. git commit -m "daily-backup: YYYY-MM-DD"
4. git push origin main              ← 推送到GitHub
```

### 3.4 与双端同步的兼容性

| 关注点 | 处理方式 |
|--------|---------|
| 冲突 | 先pull --rebase，有冲突自动暂停，不强制推送 |
| 提交污染 | 前缀 `daily-backup:` 区分，不影响日志阅读 |
| 大文件 | .gitignore排除媒体文件，只同步文档 |
| 覆盖 | 不覆盖，git add -A只添加新文件和修改，不会删别人的文件 |

### 3.5 灾难恢复流程

**笔记本挂了，换新电脑：**

```
1. 安装OpenClaw
2. git clone git@github.com:rf2025up/aios.git ~/.openclaw/workspace
3. 配置飞书通道（openclaw.json）
4. openclaw gateway start
5. 完成——所有记忆、Skill、工作文件完整恢复
```

预计恢复时间：**15分钟以内**

## 四、已部署

- [x] 脚本：`scripts/daily-backup.sh`
- [x] Cron：每日23:30自动执行
- [x] 日志：`/tmp/daily-backup.log`
- [x] 仓库：`git@github.com:rf2025up/aios.git`

---

> 方案创建：2026-04-24 | 维护者：锋哥（OpenClaw）
