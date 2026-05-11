# Hermes 系统运维备忘录

> **版本**: v2.0 | **更新**: 2026-05-11
> **目的**: 一份文件覆盖当前全部技术架构、API、问题处理。Agent自用，遇到问题时先查这里。

---

## 一、当前架构总览

```
Windows VPS（E3-1230v3 / 32GB / GTX 750Ti）
├── WSL2: Ubuntu-22.04, root
│   ├── Hermes Agent（唯一主中枢）
│   │   ├── 通道：飞书 WebSocket
│   │   ├── 模型：GLM-5-Turbo（主）/ Qwen3.6-Plus（fallback）
│   │   ├── 记忆：MEMORY(2200字符) + ClawMem(BM25检索)
│   │   ├── Cron：10个定时任务
│   │   └── Git备份：每日22:30自动推送
│   │
│   └── ClawMem（记忆检索外挂）
│       ├── 索引：/root/workspace/aios/core（84个文档）
│       ├── 模式：BM25关键词检索（推荐）
│       └── REST API：managed模式，端口7438
│
└── Windows保活链路
    ├── 开机任务：HermesGatewayWSL2
    ├── 启动脚本：C:\Users\Administrator\hermes_restart.ps1
    └── 入口：C:\Users\Administrator\hermes_restart.bat
```

**核心路径：**

| 用途 | 路径 |
|------|------|
| Hermes配置 | `/root/.hermes/config.yaml` |
| 密钥 | `/root/.hermes/.env` |
| 认证池 | `/root/.hermes/auth.json` |
| Gateway日志 | `/root/.hermes/gateway.log` |
| 错误日志 | `/root/.hermes/logs/errors.log` |
| 启动脚本 | `/root/hermes_run.sh` |
| ClawMem CLI | `/usr/local/bin/clawmem` |
| ClawMem索引 | `/root/.cache/clawmem/index.sqlite` |
| 核心文档 | `/root/workspace/aios/core/` |
| H盘同步 | `/mnt/h/Hermes/` |

**核心原则：**
- API Key只写`.env`，不写config.yaml、文档、飞书、Notion、Git
- 改key前必须备份`.env`和`auth.json`
- 改key后需重启Gateway才生效
- 外部Agent重启Gateway必须通过Windows `schtasks`
- **哪个有钱用哪个**：key失效时立即切换，不依赖固定优先级，不确认不停工

---

## 二、API与密钥管理

### 2.1 当前API配置

| Key | 用途 | 状态 |
|-----|------|------|
| GLM_API_KEY | 主模型 glm-5-turbo | Coding Plan，限流5h~80次 |
| DASHSCOPE_API_KEY | Fallback（Qwen/DeepSeek） | 主key欠费，备用key正常 |
| FEISHU_APP_ID/SECRET | 飞书Gateway | 正常 |
| NOTION_API_KEY | 记账 | 正常 |

**限流说明**：
- GLM用的是Coding Plan，URL必须是 `/api/coding/paas/v4/`（标准PAAS URL会报429"余额不足"，这是误导信息）
- DashScope主key欠费，当前使用备用key `bailian-backup-202605`

**Credential Pool配置**：
```
custom:bailian:
1. bailian-backup-202605  当前优先
2. bailian-primary-env    旧key备用

alibaba:
1. bailian-backup-202605  当前优先
2. DASHSCOPE_API_KEY      旧key备用
```

### 2.2 更换Key的标准流程

**改前备份**：
```bash
STAMP="$(date +%F-%H%M%S)"
cp -a /root/.hermes/.env "/root/.hermes/.env.bak.$STAMP"
cp -a /root/.hermes/auth.json "/root/.hermes/auth.json.bak.$STAMP"
```

**临时测试（不写配置）**：
```bash
read -rsp "Paste NEW KEY: " NEW_KEY
echo
curl -sS https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions \
  -H "Authorization: Bearer $NEW_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"qwen3.6-plus","messages":[{"role":"user","content":"只回复OK"}]}'
unset NEW_KEY
```

**写入配置（交互式，不暴露key到命令历史）**：
```bash
source /root/.hermes/hermes-agent/venv/bin/activate
hermes auth add custom:bailian --type api-key --label bailian-backup-YYYYMM
hermes auth add alibaba --type api-key --label bailian-backup-YYYYMM
hermes auth list  # 验证
```

**回滚**：
```bash
cp -a /root/.hermes/.env.bak.时间戳 /root/.hermes/.env
chmod 600 /root/.hermes/.env
```

### 2.3 模型配置

**config.yaml关键结构**：
```yaml
model:
  provider: zai
  default: glm-5-turbo
  base_url: https://open.bigmodel.cn/api/coding/paas/v4

fallback_providers:
  - provider: custom:bailian
    model: qwen3.6-plus
  - provider: custom:bailian
    model: deepseek-v4-flash

model_aliases:
  glm: {provider: zai, model: glm-5-turbo}
  qwen: {provider: custom:bailian, model: qwen3.6-plus}
  deepseek: {provider: custom:bailian, model: deepseek-v4-flash}
```

**飞书切模型**：`/model qwen`、`/model deepseek`、`/model glm`
- 只影响当前会话，`--global`才写全局

---

## 三、Gateway保活与重启

### 3.1 启动链路
```
Windows计划任务 → hermes_restart.bat → hermes_restart.ps1
  → Start-Process wsl.exe → /root/hermes_run.sh
    → hermes gateway run --replace
```

### 3.2 重启Gateway
```powershell
# Windows侧执行
schtasks /Create /TN HermesRestartOnce /TR "C:\Users\Administrator\hermes_restart.bat" /SC ONCE /ST 23:59 /F
schtasks /Run /TN HermesRestartOnce
```

### 3.3 验证
```bash
# WSL侧
ps aux | grep '[h]ermes gateway'
tail -30 /root/.hermes/gateway.log
# 成功标志：Lark/Feishu WebSocket connected
```

### 3.4 冷启动验收
```powershell
wsl --shutdown
schtasks /Create /TN HermesRestartOnce /TR "C:\Users\Administrator\hermes_restart.bat" /SC ONCE /ST 23:59 /F
schtasks /Run /TN HermesRestartOnce
# 等20秒后检查
wsl -d Ubuntu-22.04 -u root -- bash -lc "date -Is; ps aux | grep '[h]ermes gateway'; tail -30 /root/.hermes/gateway.log"
```

### 3.5 一键诊断
```bash
echo "== gateway =="; ps aux | grep '[h]ermes gateway' || true
echo "== keys =="; grep -E '^(GLM_API_KEY|DASHSCOPE_API_KEY)=' /root/.hermes/.env | sed 's/=.*/=present/'
echo "== fallback =="; source /root/.hermes/hermes-agent/venv/bin/activate && hermes fallback list 2>/dev/null || true
echo "== clawmem =="; clawmem status 2>/dev/null || true
echo "== ports =="; ss -ltn | awk 'NR==1 || /:7438/'
echo "== logs =="; tail -20 /root/.hermes/gateway.log 2>/dev/null | sed -E 's/access_key=[^& ]+/[REDACTED]/g'
```

---

## 四、ClawMem记忆系统

### 4.1 当前状态
- 索引：84个文档（/root/workspace/aios/core）
- 模式：BM25关键词检索（已验证可用）
- 向量embedding：暂不启用
- REST API：managed模式，Gateway启动时自动拉起

### 4.2 日常操作
```bash
clawmem update          # 新增/修改core文档后刷新索引
clawmem status          # 查看索引状态
clawmem doctor          # 健康检查
clawmem search 关键词 -n 5  # BM25搜索
```

### 4.3 常见误区
- `clawmem search`：BM25检索，不需要embedding，**当前推荐**
- `clawmem query`：混合检索+可能用LLM，localhost:8089没开会报错，不用作验收
- `clawmem embed`：生成向量索引，DashScope batch兼容性有问题，暂不启用
- update时出现LLM 8089 ConnectionRefused：高级增强层失败，不影响BM25可用性

### 4.4 配置
```bash
# .env中
CLAWMEM_BIN=/usr/local/bin/clawmem
CLAWMEM_SERVE_MODE=managed
CLAWMEM_SERVE_PORT=7438
CLAWMEM_PROFILE=balanced
```

---

## 五、Git备份

| 仓库 | 地址 | 用途 |
|------|------|------|
| AIOS核心 | github.com/rf2025up/hermes-aios.git | 全部core/文件+scripts |
| 备份频率 | 每日22:30自动（cron） | |
| .gitignore | .env / *.pyc / .cache / hermes-agent/ | |

---

## 六、Notion记账

| 项目 | 值 |
|------|-----|
| API版本 | `2022-06-28`（⚠️不能用新版） |
| 数据库ID | `56ae3f43-3d0f-4673-95af-21b1ea96121d` |
| 默认账户 | 营业 `6738db90` |
| 个人账户 | `b473ec6a-a343-4089-8c26-ad6b943bb49b` |

**字段映射**：項目(繁体title) / 花费(number) / 种类(select) / 日期(date) / 对应账户(relation) / 花費理由(rich_text)

**12个种类**：食材/学习用品/日用/活动材料/教辅资料/办公材料/营销费用/水电房租/工资/个人消费/房租/餐饮

**已知坑**：字段名"項目"是繁体；种类必须用已有选项；API版本必须2022-06-28

---

## 七、飞书集成

| 项目 | 值 |
|------|-----|
| App ID | `cli_a97996259a7a1cd4` |
| 通道 | WebSocket |
| API写入 | POST blocks/{block_id}/children（非batch_create） |
| 驾驶舱文档 | DkKEdWvbYoK1qfxk3MEcP0cjnbf |
| 顶层文档 | UFTkdwXzcoBbucxX62rcjIPfnOg |

---

## 八、SSH入口

```bash
# 外部进入
ssh Administrator@100.68.184.107

# 进入WSL
wsl -d Ubuntu-22.04 -u root

# 单条命令
wsl -d Ubuntu-22.04 -u root -- bash -lc "命令"
```

---

## 九、Cron定时任务（当前10个）

| 时间 | 名称 | 说明 |
|------|------|------|
| 8:00 | 晨间三件事 | 周一-六 |
| 8:05 | 系统功能推送 | 周二-日 |
| 8:15 | 每日TODO推送 | 周一-六 |
| 13:00 | 午间对焦 | 周一-六 |
| 15:50 | 想法池推送 | 周一-六 |
| 21:30 | 梦境周期（记忆整理） | 每日，local |
| 22:00 | 晚间双向复盘 | 周一-六 |
| 22:30 | 每日Git备份 | 每日，local |
| 每小时 | 自动转写 | local，terminal only |
| 周日9:00 | 周日复盘+议题整理 | 周日 |

---

## 十、故障排查速查

| 症状 | 可能原因 | 处理 |
|------|----------|------|
| 飞书无响应 | Gateway挂了 | 检查gateway进程，必要时重启 |
| 429"余额不足" | GLM限流（不是欠费） | 自动fallback到Qwen |
| Qwen也报错 | DashScope key问题 | 检查credential pool，切换key |
| clawmem_retrieve无结果 | 索引过期 | `clawmem update` |
| 日志中LLM 8089报错 | clawmem query的高级层 | 不影响BM25，忽略 |
| 记账API返回空属性 | 用了新版API | 确认Notion-Version: 2022-06-28 |

---

## 十一、v2业务主线版目录结构

```
core/
├── BUSINESS-SOUL.md     # 业务主控台身份
├── ACTIVE_TASK.md       # 当前主战役
├── THIS_WEEK_TOP3.md    # 本周重点
├── SCOREBOARD.md        # 6层数字看板
├── TODO.md / DECISIONS.md / PEOPLE.md / INDEX.md / CHANGELOG.md
├── SOUL.md / USER.md / MEMORY.md
│
├── business/            # 业务文档（11个子目录）
├── runtime/daily/       # 每日日志（core/daily软链接兼容）
├── assets/              # 可复用资产（话术/SOP/模板/案例/朋友圈）
├── inbox/               # 原始素材
├── ARCHIVE/             # v2升级前的非业务文件
└── backups/             # 备份
```

---

*本文档合并自：HERMES-WSL2-运维方案.md + AI-OS重启恢复手册.md + HERMES-GIT-BACKUP.md + NOTION-RULES.md + COMMAND-TEMPLATES.md + 文档存档协议.md*
*已过时/已合并的源文件保留在 ARCHIVE/ 和 H:\Hermes\v2升级归档\*
