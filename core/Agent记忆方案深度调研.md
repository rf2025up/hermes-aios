# Agent记忆方案深度调研

> 最后更新: 2026-05-06（ClawMem已安装，BM25可用，向量嵌入待解决）
> 调研方法：GitHub源码+API实测，非二手信息
> 核心问题：为什么现有记忆机制会反复丢信息？哪个方案能根治？

---

## 一、问题的本质

### 1.1 记忆丢失的三个真实原因

| 层级 | 原因 | 举例 |
|------|------|------|
| **系统级** | 上下文压缩（compression）丢弃关键决策 | 对话超过20轮后，"禁止本地模型转写"这条约束被压缩掉 |
| **流程级** | 执行前不查约束，直接动手 | 接到转写任务直接选方案，没去读项目文档 |
| **检索级** | session_search摘要不准，memory容量太小（2200字符） | 搜"转写约束"搜不到，因为摘要里没提 |

### 1.2 需要解决什么

1. **压缩不丢** — 上下文压缩前自动保存关键状态
2. **自动注入** — 每轮对话开始时，相关约束自动推给Agent，不依赖Agent主动搜索
3. **持久可靠** — 跨session、跨天、跨重启都能用
4. **低成本** — 不大量消耗LLM token和系统资源

---

## 二、四个方案实测对比

### 2.1 方案概览

| 方案 | Stars | 许可证 | 版本 | 状态 | Hermes支持 |
|------|-------|--------|------|------|------------|
| **MemTensor** (memos-local-plugin) | N/A | MIT | 2.0.0-beta.1 | ⚠️ npm已装未启动，保留备选 | ✅ 原生MemoryProvider |
| **ClawMem** | 152 | MIT | 0.10.3 | ✅ 已安装已索引，BM25可用 | ✅ MemoryProvider插件 |
| **Mem0** | 54,849 | Apache-2.0 | v3 | 活跃开发 | ❌ 无直接插件 |
| **mem9** | 1 | ? | ? | — | ❌ |

### 2.2 mem9 — 排除（不是记忆系统）

**结论：mem9不是Agent记忆系统，是Windows RAM优化工具。**

GitHub实测：
- 仓库：`unvulcanised-watercress762/mem9`
- 1 star, 0 forks, 19MB，TypeScript
- README描述："helps increase the memory available to OpenClaw, so you can run bigger projects without crashing"
- 就是一个改进程内存上限的Windows工具
- 没有任何记忆存储、检索、学习功能
- ❌ **不可用，排除**

### 2.3 Mem0 — 排除（过重，无Hermes插件）

GitHub实测：
- 仓库：`mem0ai/mem0`
- 54,849 stars, 6,212 forks, Apache-2.0
- Python, Y Combinator S24公司
- 三种使用方式：Library(pip) / Self-Hosted(Docker+Postgres) / Cloud(付费)

优点：
- LoCoMo基准91.6分，LongMemEval 93.4分（记忆检索质量高）
- 成熟的开源项目，社区活跃
- 支持多级记忆（User/Session/Agent）
- 2026年4月新算法：单次ADD提取 + 实体链接 + 多信号检索

问题：
- **Self-hosted需要Docker + PostgreSQL**，对WSL2 VPS太重
- **需要LLM做记忆提取**（默认gpt-5-mini），每个记忆操作都消耗token
- **需要embedding模型**（默认OpenAI text-embedding-3-small）
- **没有Hermes MemoryProvider插件**（只有OpenClaw的skills）
- Cloud版本需要注册账号，数据走外部服务器

❌ **排除原因：资源消耗太大（Docker+PG+LLM+Embedding），无Hermes原生支持**

### 2.4 MemTensor (memos-local-plugin) — 已安装待评估

已安装在 `/root/.hermes/plugins/memos-local-plugin/`，npm依赖已装完（218个包）。

架构：
```
Hermes Gateway → Python Provider → JSON-RPC → Node.js Bridge(tsx) → TypeScript Core → SQLite
```

核心能力（已读源码确认）：
- ✅ **四层记忆**：L1 Trace → L2 Policy → L3 World Model → Skill
- ✅ **每轮自动注入**：turnStartRetrieve三层检索后注入上下文
- ✅ **压缩保护**：on_pre_compress hook，压缩前保存快照
- ✅ **决策修复**：同一工具连续失败3次自动注入纠正
- ✅ **学习闭环**：反思打分 → 奖励回传 → 策略归纳 → 技能结晶
- ✅ **Web面板**：http://127.0.0.1:18910/ 可视化

具体资源消耗（从源码分析）：
- **LLM调用**：每个episode结束后，α-scorer打分(N次) + task summary(1次) + 可能L2归纳(1次) + 可能L3抽象(1次) + 可能Skill结晶(1-2次) = 额外10-20次LLM调用/episode
- **Embedding**：每次capture都要embedding（可用local MiniLM或API）
- **进程**：Node.js常驻进程（tsx运行TypeScript，内存200-500MB）
- **延迟**：每次turnStartRetrieve增加1-3秒
- **架构复杂度**：Python→JSON-RPC→Node→TS→SQLite，排障困难

风险：
- ❌ Beta版本（2.0.0-beta.1）
- ❌ 冷启动问题：头2-4周记忆为空，无检索结果
- ❌ 可能注入噪音（错误的trace也会被检索到）
- ❌ 与原生memory可能冲突（两套独立系统）
- ❌ npm install耗时2小时（依赖链极重：rollup/vite/babel全套构建工具）

### 2.5 ClawMem — 重点候选

GitHub实测：
- 仓库：`yoloshii/ClawMem`
- 152 stars, 24 forks, MIT, TypeScript on Bun
- 版本0.10.3，2026年5月4日最后更新

核心能力：
- ✅ **完全本地**：SQLite vault，不需要API key，不需要云服务
- ✅ **Hermes MemoryProvider插件**：`src/hermes/` 目录下有现成插件（plugin.yaml确认hooks: on_session_end, on_pre_compress）
- ✅ **90/10自动模式**：90%靠hooks自动注入，只有10%需要Agent主动调工具
- ✅ **压缩保护**：PreCompact hook（OpenClaw）+ on_pre_compress（Hermes）
- ✅ **混合检索**：BM25关键词 + 向量搜索 + RRF融合 + Cross-encoder重排 + 查询扩展
- ✅ **A-MEM自进化**：记忆条目自动添加关键词、标签、因果链接
- ✅ **矛盾检测**：新决策与旧决策冲突时自动标记旧决策为过期
- ✅ **会话引导**：每次session开始自动注入profile、最新handoff、最近决策
- ✅ **WSL2明确支持**：README写明"Recommended for Windows users"
- ✅ **跨运行时共享**：Claude Code/OpenClaw/Hermes共用同一个SQLite vault

资源消耗：
- **无需LLM调用**做核心操作（记忆检索、存储、生命周期管理全本地）
- 可选LLM用于观察者模型提取决策（但不是必须，有CPU回退）
- **Embedding**：本地node-llama-cpp（CPU模式自动下载GGUF模型），也可选GPU
- **运行时**：Bun进程（比Node.js轻量）
- **存储**：单个SQLite文件

依赖：
- Bun >= 1.0.0（需要安装）
- SQLite with FTS5（Bun自带）
- 可选：llama-server（GPU加速，不是必须）

安装方式：
```bash
bun add -g clawmem
clawmem bootstrap ~/notes --name notes
clawmem setup openclaw    # 或 hermes
```

局限：
- 需要 Bun 运行时（当前环境未安装）
- 本地embedding需要下载GGUF模型（首次）
- 152 stars，相对小众
- 观察者模型用本地GGUF，提取质量可能不如大模型

---

## 三、核心对比矩阵

| 维度 | MemTensor | ClawMem | Mem0 |
|------|-----------|---------|------|
| **压缩保护** | ✅ on_pre_compress | ✅ on_pre_compress | ❌ 无Hermes支持 |
| **自动注入** | ✅ 每轮turnStart | ✅ 90% hooks自动 | ❌ 需Agent主动调 |
| **Hermes原生** | ✅ MemoryProvider | ✅ MemoryProvider | ❌ 无插件 |
| **LLM消耗** | 高（10-20次/episode） | 低（仅可选观察者） | 高（每次操作需LLM） |
| **本地/隐私** | ✅ 本地 | ✅ 完全本地 | ❌ 需云或Docker+PG |
| **架构复杂度** | 高（Python→JSON-RPC→Node→TS） | 中（Bun单进程+SQLite） | 高（Docker+PG+FastAPI） |
| **版本稳定性** | Beta | v0.10.3稳定 | v3稳定 |
| **冷启动** | 2-4周积累 | 立即可用（索引已有文档） | 立即可用 |
| **检索质量** | 语义(需embedding) | 混合(BM25+向量+重排) | 语义(基准分高) |
| **额外依赖** | Node.js + npm | Bun | Docker + Postgres |
| **磁盘占用** | 218个npm包 | 更轻 | Docker镜像 |
| **跨Agent共享** | ❌ 单Agent | ✅ 共用SQLite | ✅ 共用server |

---

## 四、我的判断

### 4.1 分层解决，不是一个方案的事

记忆问题不是装一个插件就能全部解决的。正确做法是三层防御：

**第一层：确定性规则（零成本，100%可靠）**
- 关键约束写进 SOUL.md（每次加载）和项目 AGENTS.md（workdir下自动注入）
- 不依赖任何记忆系统的检索能力
- 解决"规则被遗忘"问题
- **这层已经做了，需要继续强化**

**第二层：自动记忆注入（解决压缩丢失和跨session）**
- 需要一个支持 on_pre_compress hook 的记忆插件
- 每轮对话自动注入相关记忆
- 在MemTensor和ClawMem之间选

**第三层：手动记忆捕获（解决想法沉淀）**
- daily日志 + TOPICS.md + memory工具
- **这层已有，不需要改**

### 4.2 第二层的选型建议

**推荐 ClawMem，不推荐 MemTensor。**

理由：
1. **不消耗LLM token** — 你用GLM Coding Plan有5小时80次限额，MemTensor每个episode额外消耗10-20次，ClawMem几乎不消耗
2. **冷启动即用** — ClawMem可以立刻索引你已有的core/目录文档，第一天就有检索结果；MemTensor需要积累几十个episode才有L2/L3
3. **架构简单** — Bun单进程 + SQLite，vs MemTensor的Python→JSON-RPC→Node→TS→SQLite四层链路
4. **稳定版本** — v0.10.3 vs beta.1
5. **90/10自动模式** — hooks自动注入比依赖Agent主动检索更可靠
6. **跨Agent共享** — 如果你以后用Claude Code，记忆直接可用
7. **矛盾检测** — 自动发现新旧决策冲突，MemTensor没有这个功能

ClawMem的风险：
- 需要安装Bun（5分钟的事）
- 152 stars相对小众（但MIT许可，代码质量高，README非常详细）
- 本地embedding用GGUF模型，检索质量可能不如大模型embedding

### 4.3 不做的事

- ❌ 不装mem9（它不是记忆系统）
- ❌ 不装Mem0（太重，无Hermes插件）
- ❌ 不同时装两个记忆插件（会冲突）

---

## 五、当前状态（2026-05-06）

### 5.1 ClawMem — 已安装，BM25可用，插件待Gateway重启激活

**安装记录：**
```
2026-05-06 安装步骤：
1. apt install unzip → curl下载bun-linux-x64.zip → /usr/local/bin/bun (v1.3.13)
2. bun install -g clawmem@0.10.3（214包，92秒）
3. clawmem init → DB: /root/.cache/clawmem/index.sqlite
4. clawmem collection add /root/workspace/aios/core --name aios-core
5. clawmem update → 索引80个md文件

2026-05-07 修复（锋哥手动）：
- 问题：CLI装在 /root/.bun/bin/clawmem 但不在PATH，Hermes找不到
- 修复：ln -s /root/.bun/bin/clawmem /usr/local/bin/clawmem
- 补.env：CLAWMEM_BIN=/usr/local/bin/clawmem + CLAWMEM_SERVE_MODE=managed + PORT=7438 + PROFILE=balanced
- 验证：clawmem doctor全部通过，80文档索引，BM25搜索正常，REST API健康
```

**环境变量（~/.hermes/.env）：**
```bash
CLAWMEM_BIN=/usr/local/bin/clawmem
CLAWMEM_SERVE_MODE=managed
CLAWMEM_SERVE_PORT=7438
CLAWMEM_PROFILE=balanced
```

**当前可用功能：**
- ✅ **BM25关键词搜索** — `clawmem search <query>` 正常工作，80个文档已索引
- ✅ **独立CLI验证通过** — `clawmem doctor` all checks passed
- ✅ **REST API** — /health + /retrieve 验证通过
- ✅ **Hermes插件可加载** — ClawMemProvider加载验证通过，5个工具注册成功
- ✅ **生命周期管理** — archive/restore/consolidate/curate

**待解决问题：**
- ⏳ **Gateway重启** — 需重启才能让插件在managed模式下自动拉起clawmem serve
- ⏳ **向量嵌入** — 80个文档全部Unembedded，Vectors: no。BM25已够用，后续量大时升级
- ⏳ **A-MEM enrichment** — `clawmem query` 需连localhost:8089 LLM，本地未开，暂不可用
- ⏳ **watch守护进程** — 文件变化不会自动重索引，需要时手动 `clawmem update`

**配置文件：**
- CLI路径：`/usr/local/bin/clawmem` → `/root/.bun/install/global/node_modules/clawmem/`
- 数据库：`/root/.cache/clawmem/index.sqlite`
- 配置：`/root/.config/clawmem/index.yml`
- Hermes .env：`CLAWMEM_BIN` + `CLAWMEM_SERVE_MODE` + `CLAWMEM_SERVE_PORT` + `CLAWMEM_PROFILE`

### 5.2 MemTensor (memos-local-plugin) — npm已装未启动

**状态：** ⚠️ 保留备选，不启用

**已完成：**
- npm install（218个包，耗时2小时，已完成）
- 路径：`/root/.hermes/plugins/memos-local-plugin/`
- node_modules完整

**未完成：**
- `install.hermes.sh` 未运行（未初始化Python Provider）
- Hermes config未配置为使用MemTensor的memory provider
- 未启动任何进程

**不启用原因（2026-05-06决策）：**
1. 每episode额外10-20次LLM调用，消耗GLM Coding Plan限额
2. 冷启动需要2-4周才有价值
3. 架构复杂（Python→JSON-RPC→Node→TS→SQLite四层）
4. Beta版本
5. ClawMem已能覆盖主要需求

**重新启用方法（如果需要）：**
```bash
cd /root/.hermes/plugins/memos-local-plugin/
bash install.hermes.sh   # 初始化Python Provider
# 然后在Hermes config中配置memory provider
```

### 5.3 三层记忆架构 — 当前状态

| 层级 | 组件 | 状态 | 覆盖范围 |
|------|------|------|----------|
| **第一层：确定性规则** | SOUL.md + Hermes config | ✅ 已有，需强化 | 核心铁律（执行口令、建文档规则等） |
| **第二层：自动记忆** | ClawMem (BM25) | ⚠️ CLI+索引正常，待Gateway重启激活插件 | 压缩保护、跨session记忆注入 |
| **第三层：手动记忆** | daily日志 + TOPICS.md + memory | ✅ 已有 | 想法沉淀、复盘记录 |

### 5.4 Hermes插件激活记录

```
2026-05-06 激活步骤：
1. cp -r /root/.bun/install/global/node_modules/clawmem/src/hermes /root/.hermes/plugins/clawmem
2. hermes plugins list → 确认ClawMem被发现（source: user）
3. hermes plugins enable clawmem → ✓ Plugin clawmem enabled
4. hermes config set memory.provider clawmem → ✓ Provider: clawmem
5. hermes config set memory.clawmem_serve_mode managed → 插件自动启停REST API
6. hermes memory status → Provider: clawmem, Plugin: installed ✓, Status: available ✓

激活后的hooks：
- on_pre_compress → clawmem hook precompact-extract → 压缩前保存状态
- on_session_end → decision-extractor + handoff-generator + feedback-loop
- queue_prefetch → context-surfacing → 每轮后台自动检索相关记忆注入
- session-bootstrap → 首轮自动注入profile和最近handoff

激活后的工具（REST API，端口7438）：
- clawmem_retrieve / clawmem_get / clawmem_session_log / clawmem_timeline / clawmem_similar

需要重启Hermes gateway才能生效。
```

### 5.5 下一步待办

1. ~~**[高] 激活ClawMem Hermes插件**~~ — ✅ 2026-05-06 完成
2. **[中] 解决向量嵌入** — batch→单条代理 或 本地GGUF（BM25够用时不急）
3. **[中] A-MEM enrichment验证** — 配置LLM API后验证实体提取和图遍历
4. **[低] watch守护进程** — `clawmem watch` 或 systemd服务（手动update够用时不急）
5. **[低] 7天灰度观察** — 记录记忆召回准确率、压缩保护是否生效

---

## 六、记忆系统持续迭代与瘦身方案

> 2026-05-06 补充：基于锋哥会话卫生+瘦身需求，建立系统化的记忆运维机制。

### 6.1 记忆分层架构（L1~L6）

| 层级 | 载体 | 放什么 | 注入方式 | 更新频率 |
|------|------|--------|----------|----------|
| L1 行为规则 | SOUL.md（~4000字） | 身份+核心规则+会话卫生+改动规则 | 每轮system prompt定 | 有改动时 |
| L2 事实速查 | MEMORY.md（≤2200字符） | 当前30天关键事实+禁忌 | 每轮system prompt注入，压缩后持续负载 | 每周/清理时 |
| L3 用户画像 | USER.md（~1375字符） | 稳定偏好 | 每轮注入，自动管理 | 几乎不动 |
| L4 按需检索 | ClawMem BM25（77个md文件） | 项目文档/历史日志/方案全文 | 每轮后台自动检索相关记忆 | 文件变动自动更新索引 |
| L5 知识库 | core/目录+飞书云文档 | 完整文档/手册/报告 | 手动或skill读取 | 按需补充 |
| L6 会话状态 | 交接摘要+项目文件 | 当前任务进度 | /new后手动恢复 | 每session结束时 |

### 6.2 会话卫生规则

> 已写入SOUL.md。核心原则：**Session = 工作台，不是数据库。**

**触发/new条件**（任一满足即可）：
1. 当前session超过60条消息
2. 已发生3次以上上下文压缩
3. 简单问题响应超过20秒
4. 即将开始一个新主题
5. 当前任务已有阶段性结论

**交接流程**：
1. 代理生成交接摘要（目标/已完成/未完成/关键配置/下一步，800-1500字）
2. 将摘要沉淀到记忆/项目文档
3. 锋哥执行/new

### 6.3 月度记忆维护计划

| 频率 | 动作 | 执行者 |
|------|------|--------|
| 每轮对话结束 | 落盘确认（"本轮有结论需要落盘吗？"） | 代理主动问 |
| 每次清理时 | MEMORY.md瘦身：删过期事实，去重 | 锋哥审核后执行 |
| 每次Git推送 | 整个workspace/aios备份到GitHub | 自动/手动 |
| 每月 | 完整盘点：清理clawmem索引，更新配置 | 锋哥+代理 |

### 6.4 锋哥使用指南（保持高效）

| 场景 | 应该 | 不应该 |
|------|------|--------|
| 感觉回复变慢 | /new（开新session） | 继续堆上下文 |
| /new之前 | 让代理生成交接摘要并落盘 | 直接/new丢上下文 |
| 有重要结论 | 当场说"这条落盘" | 等"最后再说" |
| 开始新话题 | /new后开始 | 在旧session里切换 |
| 系统改动需求 | 让代理列清单→逐条确认 | "帮我优化一下" |
| 长文档/大方案 | 写到文件，不要在对话展开 | 在对话里铺几千字 |

### 6.5 回复变慢的排查步骤

```
感觉变慢
  → 检查session消息数（>60条？）
  → 检查压缩次数（>3次？）
  → 检查是否开启新话题
  → 如果是 → /new（先交接摘要）
  → 如果不是 → 检查模型是否限流
```

### 6.6 核心改动规则

**SOUL.md、MEMORY.md、USER.md以及任何涉及行为准则/记忆/个性的修改，必须逐条列出变更内容，由锋哥逐条确认后才能执行。禁止"我帮你优化一下"然后一口气改完。**

**禁止代理主动提议删减SOUL.md/MEMORY.md/USER.md的核心内容。只有锋哥明确要求精简时，才能提出删减方案，且删减前必须验证信息已安全存储在可检索的外部文档中。**

### 6.7 将来可用方案（待启用）

| 方案 | 当前不可用原因 | 启用条件 |
|------|---------------|---------|
| Session按任务类型分（业务/技术/招生/文案/战略） | 单飞书入口，无多profile | Hermes多profile配置 |
| Skills减肥（高频15-30常驻，冷门归档） | 70+skill大部分是Hermes自带，不可控 | Hermes支持skill disable/enable |
| Skill描述压缩（100-200字） | 自带skill描述改不了 | 同上 |
| SOUL.md字数上限800-1500字 | 与现有核心规则量冲突，需锋哥权衡 | 锋哥明确要求时再评估 |

---

*本文档持续更新，每次记忆方案有调整时同步更新。*
