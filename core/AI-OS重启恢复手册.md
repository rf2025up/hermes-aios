# AI-OS 系统化开局指南 · 重启恢复手册

> **哪怕一切归零，有这一份就能重启。**
> 最后更新：2026-05-03 | 版本：v1.0
> 这份文档是你的"应急U盘"——所有agent、记忆、配置全部丢失时，拿着它重建一切。

---

## 目录

- [第一部分：认识我](#第一部分认识我)
- [第二部分：AI协作顶层设计](#第二部分ai协作顶层设计)
- [第三部分：系统架构](#第三部分系统架构)
- [第四部分：core/文件系统](#第四部分core文件系统)
- [第五部分：主战役](#第五部分主战役)
- [第六部分：42个协作场景](#第六部分42个协作场景)
- [第七部分：记忆持久化](#第七部分记忆持久化)
- [第八部分：外部工具配置](#第八部分外部工具配置)
- [第九部分：重启检查清单](#第九部分重启检查清单)
- [附录](#附录)

---

# 第一部分：认识我

## 1.1 五个核心身份

| # | 身份 | 说明 |
|---|------|------|
| 1 | 托管经营者 | 长沙托管机构校长，28名学生，满员70人 |
| 2 | 校长 | 兼业务负责人+产品负责人，面对真实团队和现金流 |
| 3 | 结果导向系统搭建者 | 用AI搭建"从信息到结果"的能力链 |
| 4 | AI-OS实践者 | 用AI放大器推进业务，而非用AI替代业务 |
| 5 | 高度参与型家长 | 孩子英语陪跑、教育理念实践 |

## 1.2 核心自诊断

> **"用高质量思考替代高质量行动"——这是高级逃避。**

长期循环：想很久→动作少→结果不出→热情消磨→怀疑方向→换新东西（跳船惯性）

**终极目标**：把本质判断稳定压成动作、闭环和结果的能力。

## 1.3 七项想练成的能力

1. **抓本质**——不被表象带走
2. **结构化推演**——分层、分类、识别因果、看清变量
3. **落真实场景**——回到真实约束
4. **拆逻辑依赖**——先后顺序、前提条件
5. **形成可执行方案**——谁来做、今天做什么、做到什么算完成
6. **进入每日惯例**——正确东西变每天稳定动作
7. **检查、验证、复盘、迭代**

## 1.4 工作节奏

- 早8点-晚8点
- **9:00-11:30** 黄金深度工作时间
- 中午固定陪孩子学英语1小时
- 下午5-7点最混乱

## 1.5 沟通偏好

- ✅ 结论先行、直击本质、表格形式、多选项决策带优先级
- ❌ 过度分析不行动、重复踩坑、空泛鼓励、漂亮不落地的框架
- 能说透说透，能压短压短

## 1.6 深层背景

- **核心恐惧**：多年未解决的深层次问题，无法定义就无法解决
- **过往经历**：影视外包→加盟售水机（被动收入2-3万/年）→养发店→中职招生→托管机构（当前）
- **近期范式升级**：AI分析后发现"高级逃避"+宏大叙事多巴胺上瘾+20年思维固化
- **三篇核心文章**：《高级逃避破局》《托管产品设计思维升级》《从本质到执行》

---

# 第二部分：AI协作顶层设计

## 2.1 总原则

> **AI不是主线，AI是放大器。真实业务结果才是主线。**

5个成功标准：
1. 主战役在推进
2. 信息在转化为结果
3. 日常有闭环
4. 能力在提升
5. 家庭教育在推进

## 2.2 双模式协作

| | 智库模式（帮理清） | 锋刀模式（逼落地） |
|---|---|---|
| **定位** | 深度理解、提问反问推演 | 本质判断、拆依赖、逼执行 |
| **触发** | "来聊/探讨/帮我想清楚" | "来做/帮我落地" |
| **AI行为** | 专业切入、不急着收、帮结构化 | 直击本质、拦截逃避、进TODO |
| **收尾** | 理清→分类（认知vs行动）→落地进TODO→清空 | 直接输出可执行方案+闭环检查 |

**拿不准时AI主动问：这次是来聊还是来做？**

## 2.3 四阶段流程

```
零散想法 → 聊透理清 → 结构化抽象 → 落地进TODO/沉淀存档
```

**认知清空完整链路**：
零散想法→智库模式→概念理清→结构化抽象→收敛判断→心里清空

**收敛判断标准**：
- 有外部锚点（明天要给家长讲/这周要执行/有人会用）→ 可以收敛
- 无锚点（纯打磨框架/觉得没想透）→ 继续聊或存档

## 2.4 铁律

### 72小时铁律
> 凡是不能在72小时内转化为招生、交付、管理、现金流、案例沉淀的AI折腾，全部暂停。

### 14天冻结规则
- 不设计新架构、不增加Agent、不迁移新工具、不追求完美同步、不扩展非必要自动化
- **每天至少推进一个业务可见结果**

### 需求拦截协议（每次任务前）

输出三个词：**本质→归属→最小动作**
- 业务动作→立即执行
- 非业务无强力理由→拒绝执行
- 回避→点破逃避

参考这个格式，每条需求过这三关才动手，不走捷径：

**① 需求质疑（马斯克五步法）**
- 需求是否成立？有没有更简单的方案？
- 是不是在用行动逃避思考？
- 质疑你的，也质疑我的

**② 本质思考**
- 这件事的本质是什么？目标是什么？问题到底是什么？
- 依赖关系有没有想清楚？

**③ 推进行动和关键结果**
- 明确最小可验证动作
- 定义关键结果——做这件事要产出什么？

## 2.5 反高级逃避协议

**7个触发信号**：
1. 理解层面反复打转，不进"做什么"
2. 沉迷配置不推业务
3. "有什么好的XX方法"还没说场景就问工具
4. 同时关注5+方向
5. 高燃概念+无落地动作
6. 跳船惯性——低反馈阶段换方向
7. 体系化上瘾——满足掌控感/秩序感

**AI标准话术**："你现在不是在推进主线，你在高级逃避。"

## 2.6 AI工具讨论5条规则

1. 战役推进不足时，工具升级自动降级
2. 不能转化为7天可验证动作→进候选区
3. 没连接业务结果→不无限展开
4. 系统建设须回答：服务什么结果/本周改善/不做机会成本
5. 借系统升级逃避→拉回

---

# 第三部分：系统架构

## 3.1 当前实际架构（2026-05-03）

```
Windows VPS（E3-1230v3 / 32GB / GTX 750Ti）
├── Hermes Agent ⭐ 唯一主中枢
│   ├── 通道：飞书WebSocket
│   ├── 模型：GLM-5-Turbo（主）/ GLM-4-flash（memos embedding）
│   ├── 记忆：memos-local-plugin（三层保护）
│   ├── Cron：9个定时任务
│   └── Git备份：github.com/rf2025up/hermes-memos-backup
│
├── OpenClaw Gateway（端口18789）
│   ├── main / edu / ops 三个独立workspace
│   └── 逐步被Hermes替代
│
├── WorkBuddy（锋哥Mac，白天使用）
│   ├── 本地高频协作前台
│   ├── core/文件可写（锋哥主改权）
│   └── 关键上下文同步到Hermes
│
└── 备份
    ├── ~/.hermes/backups/（每日20:30）
    └── GitHub（每日22:00）
```

## 3.2 双端协同（Hermes主 + WorkBuddy辅）

| | Hermes（VPS 24h主脑） | WorkBuddy（Mac白天前台） |
|---|---|---|
| **定位** | 决策/记忆/协调/定时/深度推演 | 高频执行/本地文件/core修改/快速交互 |
| **记忆** | memos-local-plugin（主） | MEMORY.md（辅） |
| **写入** | daily/reports/inbox + Hermes记忆 | core/全部文件 + daily |
| **同步** | 每日收割WorkBuddy日志 | 每次实质对话后push到Git |

**同步机制**：
- Git共享仓库：`github.com/rf2025up/aios`（唯一真相源）
- daily按来源分文件：`YYYY-MM-DD.md`（锋哥）/ `YYYY-MM-DD-workbuddy.md`（WorkBuddy）
- Hermes每日收割cron读取WorkBuddy日志→提炼→写Hermes记忆

## 3.3 写入权铁律

| 目录/文件 | WorkBuddy | Hermes |
|---|---|---|
| core/SOUL.md | ✅可写 | ❌只读 |
| core/USER.md | ✅可写 | ❌只读 |
| core/MEMORY.md | ✅可写 | ❌只读 |
| core/TODO.md | ✅可写 | ✅可写 |
| core/TOPICS.md | ✅可写 | ✅可写 |
| core/SCOREBOARD.md | ✅可写 | ✅可写 |
| core/DECISIONS.md | ✅可写 | ✅可写 |
| daily/ | ✅主写 | ✅可写 |
| weekly/ reports/ inbox/ | ✅可写 | ✅可写 |
| Hermes记忆(memos) | — | ✅独写 |

## 3.4 消息前缀系统

| 前缀 | 含义 |
|------|------|
| 【主战役】 | 招生/交付/管理/现金流 |
| 【复盘】 | 日常/周复盘 |
| 【文案】 | 口播/短视频/朋友圈 |
| 【视频】 | 视频转文案/知识提取 |
| 【孩子】 | 教育相关 |
| 【运维】 | 技术问题 |
| 【灵感】 | 零散想法/待清理 |

---

# 第四部分：core/文件系统

> 所有文件位于Git仓库 `C:\Program Files\Git\workspace\aios\core\`

## 4.1 核心配置文件

| 文件 | 用途 | 谁可写 | 更新频率 |
|------|------|--------|---------|
| **SOUL.md** | AI人格定义（叫"锋"、直击本质、有态度） | WorkBuddy | 稳定，很少改 |
| **USER.md** | 用户档案（身份/偏好/深层背景） | WorkBuddy | 偶尔更新 |
| **OPERATING_SYSTEM.md** | 方法论底座（沟通/高级逃避/架构原则） | WorkBuddy | 很少改 |
| **MEMORY.md** | 长期记忆（业务/技术/决策） | WorkBuddy | 每次有重要结论 |

## 4.2 任务与思考文件

| 文件 | 用途 | 谁可写 | 更新频率 |
|------|------|--------|---------|
| **TODO.md** | 唯一任务真相源，P0-P3四级 | 双端可写 | 每天更新 |
| **TOPICS.md** | 议题积累（想什么不是做什么） | 双端可写 | 每周整理 |
| **SCOREBOARD.md** | 战役计分板（6关键数字） | 双端可写 | 每周固定 |
| **DECISIONS.md** | 关键决策记录 | 双端可写 | 有决策时 |

## 4.3 运维文件

| 文件 | 用途 |
|------|------|
| **CHANGELOG.md** | 系统变更日志 |
| **HERMES_OPENCLAW_SYNC_V2.md** | 同步协议 |
| **NOTION-RULES.md** | Notion记账API配置 |
| **PEOPLE.md** | 重点学生/老师跟进 |
| **ROUTER.md** | 任务路由（什么任务给谁） |
| **记忆恢复指南.md** | 容灾恢复SOP |

## 4.4 核心文档（锋哥思想精华）

| 文件 | 用途 |
|------|------|
| **从信息到结果（母文档）.md** | 哲学根基，能力链7项，高级逃避自诊断 |
| **锋哥协作全景MECE报告.md** | 42场景全景状态看板 |
| **AI Agent 协作顶层需求方案 v1.md** | 15条规则的"宪法级"需求 |
| **关于我最近以及我需要把这套机制转化为对业务推进的痴迷.md** | 注意力黑洞机制分析 |
| **给 Hermes 的初始化总指令（按我的情况）.md** | Agent初始化总提示词 |
| **认知清空指南.md** | 双模式协作操作手册 |

---

# 第五部分：主战役

## 5.1 大航海3个月增长挑战（2026.04-07）

**核心目标**：
- 托管学生：26人 → 46人+（新增20人）
- 新一家长微信：0 → 300个
- 建成流量×转化×交付闭环

**12周节奏**：
| 阶段 | 时间 | 重点 |
|------|------|------|
| 阶段一 | 第1-3周（4/14-5/4） | 收产品内核 |
| 阶段二 | 第4-7周（5/5-6/1） | 搭获客闭环 |
| 阶段三 | 第8-10周（6/2-6/22） | 打转化率 |
| 阶段四 | 第11-12周（6/23-7/7） | AI落地 |

**定价**：标价1780-1880，团购1180-1280

## 5.2 6个关键数字（每天跟踪）

| # | 指标 | 目标 |
|---|------|------|
| 1 | 新增触达 | — |
| 2 | 有效咨询 | — |
| 3 | 试听意向 | — |
| 4 | 成交 | — |
| 5 | 家校沟通 | ≥3次/天 |
| 6 | 老师管理 | — |

## 5.3 任务分解

### P0 幼小衔接主战场
- #1 **一句话价值主张**（🔴最核心卡点，连续多天未完成）
- #2 每日至少3个家长深度沟通
- #3 体验课准备
- #4-#13 运营方案/宣传物料/地推/礼品/微信积累/朋友圈/视频素材/招新老师/6月蓄水

### P1 托管日常运营
- 高价值可视化、体验课流程、积分系统、期中复习、家长交付物、跟进记录

### P2 技术基建
- memos插件（✅已完成）、飞书写权限、晨间三件事

### P3 个人成长
- 英语启蒙、口播日拍10条

## 5.4 关键时间线

| 日期 | 事件 | 紧迫度 |
|------|------|--------|
| **05-08** | 允允+文锦叶试课 | 🔴 |
| **05-18** | MiniMax Key到期 | 🟡 |
| **05-20~25** | 小学报到日·决战 | 🔴🔴 |

---

# 第六部分：42个协作场景

## 6.1 12个身份维度

| 维度 | 身份 | 场景数 | 状态 |
|------|------|--------|------|
| D1 | 校长·日常运营 | 10 | 4个cron定时（8:00/13:30/15:00/21:00） |
| D2 | 业务负责人·招生增长 | 8 | **B5幼小衔接=最高优先级** |
| D3 | 产品负责人·课程服务 | 5 | 期中复习/错题机制待落地 |
| D4 | 父亲·英语陪跑 | 5 | 听力跟踪/词汇测试未开始 |
| D5 | 个人成长·AI协作 | 6 | 高级逃避识别协议运行中 |
| D6 | 知识IP·内容创作 | 2 | 绿毛怪蒸馏165视频已建skill |
| D7 | 一堂学习体系 | 1 | 流程已定义待首次跑通 |
| D8 | 商业洞察收集 | 1 | 抖音→洞察→归档 |
| D9-D12 | 育儿/反思/灵感/本地AI | 各1 | 语音转写已切阿里云Paraformer |

**汇总**：✅已通25(60%) | ⚠️部分通10(24%) | ❌未开始4(10%) | ⚙️进行中3(7%)

## 6.2 五种协作模式

| 模式 | 类型 | 场景数 | 说明 |
|------|------|--------|------|
| 0 | 认知清空（元模式） | — | 丢进来→聊透→结构化→分拣 |
| 1 | 定时触发 | 9个cron | 待办/午间/运动/晚间/周复盘等 |
| 2 | 随手对话 | 18 | 发一句就行 |
| 3 | 后台批处理 | 6 | 甩文件跑完通知 |
| 4 | 深度协作 | 10 | 需来回讨论 |

## 6.3 9个Cron定时任务

| 时间 | 任务 | 说明 |
|------|------|------|
| 7:50 | 夜间报告推送 | OpenClaw→锋哥 |
| 8:00 | 晨间对焦 | 3个问题启动 |
| 13:00 | 午间对焦 | 半天收口 |
| 15:50 | 运动提醒 | |
| 20:00 | 记忆备份 | 备份脚本 |
| 21:00 | 晚间复盘+OpenClaw收割 | 读日志→提炼→写记忆 |
| 21:30 | 梦境周期 | 静默记忆整理 |
| 22:00 | memos Git备份 | push到GitHub |

---

# 第七部分：记忆持久化

## 7.1 三层保护架构

```
第一层（实时）：memos-local-plugin
├── on_turn_start：每轮检索相关记忆
├── on_session_end：自动保存对话摘要
├── on_memory_write：memory工具操作同步
└── 数据：~/.hermes/memos-plugin/data/memos.db

第二层（每日）：Git自动备份
├── 脚本：~/.hermes/scripts/hermes-memory-backup.sh
├── 时间：每天20:00
├── 覆盖：Hermes db + OpenClaw 4个workspace + memos.db
└── 保留：30天历史 + .latest

第三层（远程）：GitHub
├── 仓库：github.com/rf2025up/hermes-memos-backup（private）
├── 时间：每天22:00
└── 内容：memos数据+配置
```

## 7.2 memos-local-plugin 配置

- **Provider**: memos-local-plugin
- **代码位置**: `~/.hermes/plugins/memos-local-plugin/`
- **数据位置**: `~/.hermes/memos-plugin/`
- **LLM**: glm-4-flash（智谱）
- **Embedding**: Xenova/all-MiniLM-L6-v2（本地）
- **Bridge**: Node.js (tsx) + Python bridge_client.py

**Windows已知修复**：
- npm install（314包）
- bridge_client.py第85-93行：Windows优先tsx.cmd路径
- shell_path: /c/Program Files/Git/bin/bash.exe

## 7.3 记忆恢复SOP

1. `ls ~/.hermes/backups/` 确认备份
2. 恢复Hermes：cp memory_store.db + state.db + config.yaml
3. 恢复OpenClaw：循环cp各workspace的MEMORY.md/SOUL.md/USER.md
4. 恢复memos.db
5. 重启gateway

---

# 第八部分：外部工具配置

## 8.1 Notion记账

```
Token: [NOTION_TOKEN_ENV]
API版本: 2022-06-28（⚠️新版2025-09-03返回0属性）
Base URL: https://api.notion.com/v1
```

| 数据库 | ID |
|--------|-----|
| 支出库（内联） | 56ae3f43-3d0f-4673-95af-21b1ea96121d |
| 营业账户 | 67db8db90-adb0-40d9-925a-0f964a2c9054 |
| 个人账户 | b473ec6a-a343-4089-8c26-ad6b943bb49b |

**字段**：項目(title/繁体)、花费(number)、种类(select)、日期(date)、对应账户(relation)、花費理由(rich_text)

**12个种类**：食材/学习用品/日用/活动材料/教辅资料/办公材料/营销费用/水电房租/工资/个人消费/房租/餐饮

## 8.2 飞书

- Hermes机器人App ID: `cli_a97996259a7a1cd4`
- 通道：WebSocket
- 群组：「万山无阻@及锋而试」

## 8.3 Git仓库

| 仓库 | 地址 | 用途 |
|------|------|------|
| AIOS核心 | github.com/rf2025up/aios | 全部core/文件 |
| memos备份 | github.com/rf2025up/hermes-memos-backup | 记忆数据 |

## 8.4 模型API

- **主模型**: GLM-5-Turbo（智谱Z.AI）
- **Memos LLM**: glm-4-flash
- **Embedding**: Xenova/all-MiniLM-L6-v2（本地）
- **Hermes API**: endpoint `open.bigmodel.cn/api/paas/v4`

---

# 第九部分：重启检查清单

## 9.1 全新部署步骤

```bash
# 1. 安装Hermes
powershell -Command "irm https://hermes-agent.nousresearch.com/install.ps1 | iex"

# 2. 配置飞书
hermes config set channels.feishu.app_id "cli_a97996259a7a1cd4"

# 3. 配置模型
hermes config set models.default.provider zai
hermes config set models.default.model glm-5-turbo

# 4. 修复Windows shell
hermes config set shell "/c/Program Files/Git/bin/bash.exe"

# 5. 安装memos插件
npm install -g @memtensor/memos-local-plugin
powershell -ExecutionPolicy Bypass -File install.ps1 -Agent hermes
cd ~/.hermes/plugins/memos-local-plugin && npm install

# 6. 修复bridge_client.py（Windows tsx.cmd兼容）
# 第85-93行增加tsx.cmd优先逻辑

# 7. 配置记忆provider
hermes config set memory.provider memos-local-plugin

# 8. 克隆AIOS仓库
git clone https://github.com/rf2025up/aios.git /c/Program\ Files/Git/workspace/aios

# 9. 安装gh CLI
# 下载gh_2.67.0并放入PATH

# 10. 初始化memos Git备份
cd ~/.hermes/memos-plugin && git init && git remote add origin https://github.com/rf2025up/hermes-memos-backup.git

# 11. 启动
hermes gateway start
```

## 9.2 验证检查

- [ ] `hermes` 命令可用
- [ ] 飞书能收发消息
- [ ] Terminal可执行命令（不报CWD错误）
- [ ] memos bridge进程运行（`wmic process where "name='node.exe'" get CommandLine | grep bridge`）
- [ ] memory add后memos.db WAL增长
- [ ] memory_search能返回结果
- [ ] cron任务列表正常（`hermes cron list`）
- [ ] Git备份仓库可push

## 9.3 常见坑

| 坑 | 现象 | 解决 |
|----|------|------|
| terminal CWD腐烂 | `[WinError 267]` | shell改为Git Bash路径 |
| bridge WinError 193 | tsx不是有效Win32应用 | 优先用tsx.cmd |
| gateway session重置通知 | restart后自动发消息 | 硬编码无法关闭，忽略即可 |
| git push超时 | GitHub直连不通 | remote URL嵌入token |
| memos加载失败 | data/为空 | 检查provider名称=目录名 |

---

# 附录

## A. 文件路径索引

```
Windows VPS:
  ~/.hermes/config.yaml                          # Hermes主配置
  ~/.hermes/plugins/memos-local-plugin/          # memos插件代码
  ~/.hermes/memos-plugin/data/memos.db           # memos数据库
  ~/.hermes/memos-plugin/config.yaml             # memos运行配置
  ~/.hermes/scripts/hermes-memory-backup.sh      # 备份脚本
  ~/.hermes/backups/                             # 备份目录
  C:/Program Files/Git/workspace/aios/core/      # AIOS核心文件

Mac (WorkBuddy):
  ~/WorkBuddy/Claw/                              # OpenClaw workspace
  ~/WorkBuddy/Claw/.workbuddy/memory/            # WorkBuddy日志
```

## B. 关键命令速查

```bash
# Hermes管理
hermes config set <key> <value>    # 修改配置
hermes gateway start                # 启动gateway
hermes tools                        # 查看工具
hermes cron list                    # 查看cron

# 记忆验证
wmic process where "name='node.exe'" get CommandLine 2>/dev/null | grep bridge
ls -la ~/.hermes/memos-plugin/data/

# Git备份
cd ~/.hermes/memos-plugin && git add -A && git commit -m "backup" && git push

# 备份恢复
ls ~/.hermes/backups/
cp ~/.hermes/backups/.latest/* ~/.hermes/
```

## C. AI一句话使命

> 帮我盯住当前主线，识别高级逃避，把高质量认知持续压到现实动作、反馈闭环和结果沉淀里，最终让我真正长出"从信息到结果"的能力。

---

*本文档由Hermes Agent生成，基于core/目录下全部文件 + 2026-05-03系统状态。如有重大变更请更新本文档。*
