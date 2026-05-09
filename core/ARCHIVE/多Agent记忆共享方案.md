# 多Agent记忆共享方案

> **创建**：2026-05-02 | **版本**：v1.0
> **目标**：Hermes全量掌握OpenClaw全部agent动态，一个地方查所有记忆

---

## 一、当前现状（记忆碎片化）

### 你有多少个AI Agent？

| Agent | 归属 | 模型 | 记忆位置 | 工作区 |
|-------|------|------|----------|--------|
| **Hermes（直击本质）** | Hermes独立运行 | GLM-5-Turbo | `~/.hermes/memory_store.db` + `state.db` + `~/.hermes/memory`文本 | `aios/core/` |
| **OpenClaw main** | OpenClaw默认agent | GLM-5-Turbo | `~/.openclaw/workspace/MEMORY.md` | `~/.openclaw/workspace/` |
| **OpenClaw bridge** | OpenClaw桥接agent | GLM-5.1 | 与main共享workspace | `~/.openclaw/workspace/` |
| **OpenClaw edu（小园老师）** | OpenClaw教育agent | GLM-4.7 | `~/.openclaw/workspace-edu/MEMORY.md` | `~/.openclaw/workspace-edu/` |
| **OpenClaw ops（贾维斯）** | OpenClaw运维agent | GLM-5-Turbo | `~/.openclaw/workspace-ops/MEMORY.md` | `~/.openclaw/workspace-ops/` |
| **WorkBuddy** | 同一git仓库 | ? | `aios/` 内相关文件 | `aios/` |

**问题**：
- 6个agent，记忆分散在6个地方，互相看不见
- OpenClaw的bridge和main共享workspace，但edu和ops完全隔离
- Hermes只能通过harvest cron定时去读文件，不是实时
- 没有任何agent能一句话查到"所有agent最近在干什么"

---

## 二、目标架构（MemOS统一记忆层）

```
                    ┌─────────────────────────────┐
                    │     MemOS (记忆管理大脑)       │
                    │  - 记忆去重（LLM判断）          │
                    │  - 混合检索（全文+向量语义）     │
                    │  - 记忆遗忘（自动清理过期）      │
                    │  - Web管理面板(localhost:18799) │
                    └──────────────┬──────────────────┘
                                   │ API
                    ┌──────────────┴──────────────────┐
                    │   memos.db (SQLite统一存储)       │
                    │   ~/.openclaw/memos-local/       │
                    └──────────────┬──────────────────┘
                                   │
        ┌──────────┬───────────┬───┴────┬──────────────┐
        ▼          ▼           ▼        ▼              ▼
    OpenClaw   OpenClaw    OpenClaw  OpenClaw      Hermes
    main       edu(小园)   ops(贾维斯) bridge      (直击本质)
    memory_    memory_     memory_   memory_       harvest cron
    write      write       write     write         读取API
    public     public      public    public        全量查询
```

### 核心思路

**所有agent写入同一个memos.db，通过标签区分来源。任何agent（包括Hermes）都能一次查到所有记忆。**

---

## 三、MemOS是什么？三个项目的关系

你之前提到的三个GitHub项目，关系如下：

```
usememos/memos          ← 独立项目，开源备忘录工具（类似flomo）
                           可以Docker部署，有REST API
                           MemOS把它作为存储后端

MemTensor/MemOS         ← AI记忆操作系统
                           提供记忆去重、混合检索、遗忘机制
                           可以独立使用，也可以接usememos/memos

MemOS/memos-local-plugin ← MemOS为OpenClaw写的插件
                           已经安装在你机器上！
                           直接用SQLite本地存储（不需要Docker）
                           提供memory_search/write等工具给agent用
```

**关键发现：你机器上已经有memos-local-plugin了！**

| 组件 | 状态 | 位置 |
|------|------|------|
| memos-local-plugin代码 | ✅ 已安装 | `~/.openclaw/extensions/memos-local-openclaw-plugin/` |
| memos.db数据文件 | ✅ 存在（628K） | `~/.openclaw/memos-local/memos.db` |
| memos-memory-guide技能 | ✅ 已安装 | `~/.openclaw/skills/memos-memory-guide/` |
| OpenClaw里plugin启用 | ❓ 未知 | 需要确认openclaw.json里plugins配置 |
| 实际运行中 | ❌ 从未成功 | 之前"装错了"，数据是早期测试残留 |

### memos-local-plugin提供的工具

| 工具 | 作用 | 谁能用 |
|------|------|--------|
| `memory_search` | 混合检索（全文+向量） | OpenClaw各agent |
| `memory_get` | 获取记忆完整原文 | OpenClaw各agent |
| `memory_write_public` | 写入共享记忆（所有agent可见） | OpenClaw各agent |
| `memory_share` | 分享已有记忆给其他agent | OpenClaw各agent |
| `memory_timeline` | 按时间线浏览记忆 | OpenClaw各agent |
| `memory_viewer` | Web面板查看记忆 | 浏览器访问 |
| `skill_search/install/publish` | 跨agent技能共享 | OpenClaw各agent |
| `network_memory_detail` | 查看团队共享记忆 | 需配置team server |
| `task_summary` | 任务摘要 | OpenClaw各agent |

---

## 四、Hermes怎么全量掌握？

Hermes不是OpenClaw的agent，不能直接用memos-local-plugin的工具。但有两条路：

### 路径A：直接读memos.db（最简单，现在就能做）

```
Hermes → read_file(search_files) → memos.db → 拿到所有agent记忆
```

- memos.db是SQLite文件，Hermes可以直接用terminal工具查询
- 每天harvest cron自动读一次，变化写入Hermes自己的fact_store
- **优点**：零部署，现在就能用
- **缺点**：不是实时的，依赖cron定时

### 路径B：部署MemOS HTTP API（更完整）

```
Hermes → HTTP API → MemOS → memos.db → 拿到所有agent记忆
```

- MemOS提供HTTP API，Hermes可以随时调用
- 支持语义搜索（不只是关键词）
- **优点**：实时、语义检索、Web管理面板
- **缺点**：需要部署MemOS服务

### 路径C：部署usememos/memos Docker + MemOS桥接（最完整）

```
Hermes → HTTP API → usememos/memos(Docker) ← MemOS桥接 ← OpenClaw各agent
```

- usememos/memos提供Web UI，你可以在浏览器里管理所有memo
- MemOS做记忆去重和语义检索
- **优点**：完整方案，有可视化界面，适合长期使用
- **缺点**：需要Docker，部署复杂度最高

### 推荐路径：先用A，再升级到B

| 阶段 | 做什么 | 时间 |
|------|--------|------|
| **现在** | 路径A：Hermes直接读memos.db，harvest cron定时同步 | 10分钟 |
| **OpenClaw修好后** | 路径B：确认memos-local-plugin正常运行，Hermes调API | 需要你配合 |
| **长期** | 路径C：如果需要Web管理面板，再加usememos/memos | 按需 |

---

## 五、Hermes的harvest cron需要补充什么？

当前cron job `870bf347b492`（每日收割OpenClaw进展）只读了主workspace的文件。需要补充：

| 来源 | 文件路径 | 当前覆盖 |
|------|----------|----------|
| OpenClaw main MEMORY.md | `~/.openclaw/workspace/MEMORY.md` | ✅ 已有 |
| OpenClaw edu MEMORY.md | `~/.openclaw/workspace-edu/MEMORY.md` | ❌ 缺失 |
| OpenClaw ops MEMORY.md | `~/.openclaw/workspace-ops/MEMORY.md` | ❌ 缺失 |
| OpenClaw kitchen MEMORY.md | `~/.openclaw/workspace-kitchen/MEMORY.md` | ❌ 缺失 |
| memos.db全量记忆 | `~/.openclaw/memos-local/memos.db` | ❌ 缺失 |
| OpenClaw daily日志 | `~/.openclaw/*/memory/YYYY-MM-DD.md` | ❌ 缺失 |

---

## 六、待你确认的问题

1. **OpenClaw现在能正常启动吗？** 如果能，我需要确认memos-local-plugin是否在运行
2. **你想先走路径A（零部署直接读db）还是直接上路径B（部署MemOS API）？**
3. **飞书云文档权限（docx:document:write）开了吗？** 之前发的授权指南你操作了吗？

---

## 七、备份机制（已完成）

| 项目 | 状态 |
|------|------|
| 备份脚本v2.0 | ✅ `~/.hermes/scripts/hermes-memory-backup.sh` |
| 覆盖范围 | Hermes db + OpenClaw 4个workspace + memos.db + openclaw.json |
| 每日自动备份 | ✅ Cron 每天20:00 |
| 备份位置 | `~/.hermes/backups/`（在git仓库外，其他agent碰不到） |
| 恢复指南 | `core/记忆恢复指南.md`（待更新路径） |
