# RF-Lenovo Hermes 安装指南（Agent执行版）

> **目标机器**：RF-Lenovo，Ubuntu 22.04.5 LTS Server（刚装好）
> **硬件**：i5 CPU，8GB RAM，120GB SSD（系统盘）+ 1TB 工作盘（待挂载）
> **执行者**：VPS运维Agent，通过SSH操作
> **执行时间**：2026年5月
> **目的**：测试RF机器稳定性，作为Windows Hermes的备选迁移目标

---

## 阶段零：前置确认（执行前必须拿到）

在开始安装之前，确认以下信息已就绪：

| 信息 | 来源 | 备注 |
|------|------|------|
| RF机器SSH地址（IP + 端口 + 用户名密码） | 锋哥提供 | 例如 `root@192.168.x.x` |
| 新飞书Bot的 App ID 和 App Secret | 锋哥在飞书开放平台创建 | **必须新建一个Bot，不能复用Windows的** |
| 大模型API Key（GLM-5 / ZAI） | 复用Windows的key | 如果Windows config能读到的话 |
| 阿里云 DashScope API Key（转写用） | 复用Windows的key | 如果Windows config能读到的话 |
| Windows Hermes的 config.yaml 内容 | 从 `C:\Users\Administrator\.hermes\config.yaml` 读取 | 提取模型配置、飞书配置、memory配置 |

⚠️ **如果以上任何一条缺失，先暂停，向锋哥索要，不要猜测或跳过。**

---

## 阶段一：系统基础配置（SSH连接后立即执行）

### 1.1 确认系统版本和状态

```bash
uname -r
# 预期：6.8.x（Ubuntu 22.04 LTS标准内核）

lsb_release -a
# 预期：Ubuntu 22.04.x LTS

free -h
# 确认内存 ≈ 8GB

df -h
# 确认系统盘和1TB工作盘都在
```

### 1.2 系统更新

```bash
sudo apt update && sudo apt upgrade -y
```

### 1.3 安装基础依赖

```bash
sudo apt install -y curl wget git build-essential python3 python3-pip python3-venv \
    nodejs npm ffmpeg tmux ufw unzip
```

### 1.4 确认关键版本

```bash
python3 --version    # 3.10+
node --version       # 18+（如果低于18需要升级）
ffmpeg -version      # 确认可用
git --version
```

### 1.5 Node.js 版本升级（如果低于18）

```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
node --version       # 确认 ≥ 20
npm --version
```

### 1.6 挂载1TB工作盘（如果还没挂载）

```bash
# 查看磁盘
lsblk
# 找到1TB盘（可能是 /dev/sdb 或 /dev/sda2）
# 假设是 /dev/sdb：

sudo mkfs.ext4 /dev/sdb
sudo mkdir -p /data
sudo mount /dev/sdb /data
echo '/dev/sdb /data ext4 defaults 0 2' | sudo tee -a /etc/fstab

# 创建目录结构
sudo chown -R $(whoami):$(whoami) /data
mkdir -p /data/audio       # 音视频原始文件
mkdir -p /data/transcripts # 转写结果
mkdir -p /data/docs        # 清洗后的文档
mkdir -p /data/workspace   # AIOS工作区
```

⚠️ **如果 /dev/sdb 不对，用 lsblk 看清楚再操作。不要格式化系统盘！**

### 1.7 配置防火墙（仅放行SSH）

```bash
sudo ufw allow OpenSSH
sudo ufw --force enable
sudo ufw status
```

---

## 阶段二：安装 Hermes Agent

### 2.1 安装

```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

安装完成后验证：

```bash
hermes --version
hermes doctor
```

### 2.2 配置模型（GLM-5 via ZAI）

```bash
# 设置模型
hermes config set model.default glm-5-turbo
hermes config set model.provider zai

# 设置API Key（从Windows config或锋哥处获取）
hermes config set model.api_key "GLM_API_KEY_HERE"
```

⚠️ **API Key 必须是真实值，不要用占位符。** 如果不知道key，从Windows的 `~/.hermes/.env` 或 `~/.hermes/config.yaml` 中读取。

### 2.3 启用必要工具

```bash
hermes tools enable terminal
hermes tools enable file
hermes tools enable web
hermes tools enable memory
hermes tools enable session_search
hermes tools enable cronjob
hermes tools enable delegation
hermes tools enable todo
hermes tools enable vision
```

### 2.4 验证安装

```bash
hermes chat -q "你好，回复一句话确认你能正常工作"
# 预期：正常返回回复
```

---

## 阶段三：配置飞书通道（新建Bot）

⚠️ **核心规则：必须新建一个飞书Bot应用，不能复用Windows上的Bot。**

两个Bot同时连接飞书会导致消息被随机分配，对话撕裂。

### 3.1 锋哥需要在飞书开放平台创建新Bot

告诉锋哥去 https://open.feishu.cn/ 创建一个新的企业自建应用：
- 应用名称：`Hermes-Linux`（或任意名称，和Windows的区分开）
- 权限：跟Windows的Bot一样（消息收发、文档读写等）
- 事件订阅：接收消息
- 创建完后获取：App ID、App Secret

### 3.2 等锋哥提供 App ID 和 App Secret 后执行

```bash
hermes gateway setup
# 选择 feishu（飞书）
# 输入 App ID 和 App Secret
# 选择要监听的群（或先不选，后面在群里加bot）
```

### 3.3 配置 gateway 后台运行（确保SSH断开不会停）

```bash
# 方法1：systemd（推荐，如果支持）
hermes gateway install
hermes gateway start
hermes gateway status

# 方法2：如果 systemd 不可用，用 tmux
tmux new-session -d -s hermes 'hermes gateway run'
```

### 3.4 验证飞书连接

```bash
hermes gateway status
# 确认 feishu 状态是 connected
```

在飞书群里 @这个新bot 发一条消息，确认能回复。

---

## 阶段四：工作区和记忆迁移（基础版）

> 目的：让RF机器上的Hermes有基本的锋哥上下文，不需要从零开始。
> 完整记忆迁移（memos插件等）在RF稳定后再做。

### 4.1 从Windows拷贝workspace文件

在Windows上执行（或让VPS agent通过SSH到Windows执行）：

```bash
# Windows路径 → RF机器
# workspace目录
scp -r "C:/Program Files/Git/workspace/aios" user@RF_IP:/data/workspace/

# SOUL/USER/IDENTITY（如果不在workspace里，在~/.hermes/下）
scp ~/.hermes/SOUL.md user@RF_IP:/data/workspace/aios/ 2>/dev/null
scp ~/.hermes/USER.md user@RF_IP:/data/workspace/aios/ 2>/dev/null
```

⚠️ **如果Windows terminal坏了没法scp，可以从GitHub仓库拉，或者用飞书传文件。**

### 4.2 在RF机器上配置workspace路径

```bash
# 设置Hermes的工作目录
hermes config set terminal.cwd /data/workspace
```

### 4.3 确认文件就位

```bash
ls /data/workspace/aios/core/
# 预期看到：SOUL.md USER.md TOPICS.md 人机协作指南.md 等文件
```

---

## 阶段五：安装 memos 记忆插件（可选，完整迁移时做）

> 测试期可以先跳过这步。等确认RF稳定后再装。

### 5.1 安装插件

```bash
npm install -g @memtensor/memos-local-plugin
```

### 5.2 部署到Hermes

```bash
# Linux上直接用install.sh（不需要像Windows那样用PowerShell）
~/.hermes/plugins/memos-local-plugin/install.sh --agent hermes
```

如果install.sh不可用，手动部署：

```bash
mkdir -p ~/.hermes/plugins/memos-local-plugin
cp -r /usr/local/lib/node_modules/@memtensor/memos-local-plugin/* ~/.hermes/plugins/memos-local-plugin/
```

### 5.3 安装npm依赖

```bash
cd ~/.hermes/plugins/memos-local-plugin
npm install
```

### 5.4 创建wrapper __init__.py

```bash
cat > ~/.hermes/plugins/memos-local-plugin/__init__.py << 'EOF'
from __future__ import annotations
import importlib.util, sys
from pathlib import Path

_ADAPTER_DIR = Path(__file__).resolve().parent / "adapters" / "hermes" / "memos_provider"
if str(_ADAPTER_DIR.parent) not in sys.path:
    sys.path.insert(0, str(_ADAPTER_DIR.parent))

_spec = importlib.util.spec_from_file_location(
    "memos_provider", str(_ADAPTER_DIR / "__init__.py")
)
_mod = importlib.util.module_from_spec(_spec)
sys.modules["memos_provider"] = _mod
_spec.loader.exec_module(_mod)
MemTensorProvider = _mod.MemTensorProvider
MemoryProvider = getattr(_mod, "MemoryProvider", object)

def register(ctx):
    ctx.register_memory_provider(MemTensorProvider())
EOF
```

### 5.5 复制plugin.yaml

```bash
cp ~/.hermes/plugins/memos-local-plugin/adapters/hermes/plugin.yaml \
   ~/.hermes/plugins/memos-local-plugin/plugin.yaml
```

### 5.6 配置

```bash
# 创建运行时目录
mkdir -p ~/.hermes/memos-plugin/data

# 创建配置文件
cat > ~/.hermes/memos-plugin/config.yaml << 'EOF'
version: 1
viewer:
  port: 18800
embedding:
  provider: local
llm:
  provider: openai_compatible
  endpoint: "https://open.bigmodel.cn/api/paas/v4"
  apiKey: "GLM_API_KEY_HERE"
  model: "glm-4-flash"
  temperature: 0
  fallbackToHost: false
  timeoutMs: 45000
  maxRetries: 3
hub:
  enabled: false
telemetry:
  enabled: false
logging:
  level: info
EOF
```

⚠️ **把 `GLM_API_KEY_HERE` 替换为真实key。**

### 5.7 配置Hermes使用memos

```bash
hermes config set memory.memory_enabled true
hermes config set memory.user_profile_enabled true
hermes config set memory.provider memos-local-plugin
```

### 5.8 验证memos

```bash
cd ~/.hermes/plugins/memos-local-plugin
echo '{"jsonrpc":"2.0","id":1,"method":"core.health","params":{}}' | \
  timeout 10 node_modules/.bin/tsx bridge.cts --agent=hermes 2>&1
# 预期看到 pipeline.ready 和 {"ok":true}
```

---

## 阶段六：安装转写工具链（可选）

### 6.1 FFmpeg（阶段一已装，确认可用）

```bash
ffmpeg -version
```

### 6.2 Python + 阿里云Paraformer SDK

```bash
python3 -m venv ~/transcribe-env
source ~/transcribe-env/bin/activate
pip install dashscope requests

# 验证
python3 -c "import dashscope; print('OK')"
```

### 6.3 拷贝转写脚本

从Windows拷贝 `paraformer_batch.py` 到RF：

```bash
scp "C:/Users/Administrator/.openclaw/workspace-ops/paraformer_batch.py" \
    user@RF_IP:/data/workspace/
```

---

## 阶段七：稳定性测试（装完后自动跑3天）

### 7.1 基础功能验证清单

安装完成后，逐项验证并记录结果：

| # | 测试项 | 命令 | 预期结果 |
|---|--------|------|---------|
| 1 | terminal可用 | `hermes chat -q "echo hello"` | 正常返回 |
| 2 | 文件读写 | `hermes chat -q "创建/tmp/test.txt写入hello然后读取"` | 正常 |
| 3 | 网络访问 | `hermes chat -q "访问百度首页"` | 正常 |
| 4 | 飞书连通 | 在飞书群@bot发消息 | bot回复 |
| 5 | 长时间运行 | gateway跑24小时不崩 | 无崩溃 |
| 6 | 内存稳定性 | 运行24小时后 `free -h` | 无泄漏 |
| 7 | FFmpeg | `ffmpeg -i test.mp4 -vn test.m4a` | 正常转换 |

### 7.2 设置监控（每天自动检查一次）

在RF机器上设置cron，每天8:00检查一次并输出状态：

```bash
crontab -e
# 添加：
0 8 * * * echo "$(date) | $(free -h | grep Mem | awk '{print $3"/"$2}') | $(df -h / | tail -1 | awk '{print $5}') | $(hermes gateway status 2>&1 | head -3)" >> /data/hermes-health.log
```

### 7.3 判断标准

**3天内如果出现以下情况，说明RF机器不稳定：**
- 系统死机/卡死（需要硬重启）
- 系统自动重启
- gateway崩溃超过2次
- 内存持续增长不释放

**3天稳定后，可以推进完整迁移：**
- 装memos插件（阶段五）
- 迁移完整记忆数据
- 配置所有飞书通道
- 迁移转写任务

---

## 附录A：如果出问题了

### A.1 gateway启动失败

```bash
# 查看日志
hermes gateway status
cat ~/.hermes/logs/gateway.log | tail -50

# 常见原因：
# - 端口被占用：lsof -i :端口号
# - config.yaml格式错误：hermes config check
# - 依赖缺失：hermes doctor --fix
```

### A.2 飞书连接失败

```bash
# 检查网络能否访问飞书API
curl -s https://open.feishu.cn/

# 检查App ID/Secret是否正确
hermes gateway setup  # 重新配置
```

### A.3 memos bridge启动失败

```bash
# 手动测试bridge
cd ~/.hermes/plugins/memos-local-plugin
npm install  # 重新安装依赖
echo '{"jsonrpc":"2.0","id":1,"method":"core.health","params":{}}' | \
  timeout 10 node_modules/.bin/tsx bridge.cts --agent=hermes 2>&1
```

---

## 附录B：完整迁移时的数据搬迁清单

> 等RF稳定确认后，从Windows搬到RF需要拷贝的数据。

```
从Windows拷贝到RF：
├── ~/.hermes/config.yaml          → 模型/飞书/memory配置
├── ~/.hermes/.env                 → API Keys
├── ~/.hermes/plugins/             → memos插件（重装node_modules）
├── ~/.hermes/memos-plugin/        → memos数据（SQLite + 配置）
├── ~/.hermes/skills/              → 已安装的skills
├── ~/workspace/aios/              → 完整workspace
│   ├── SOUL.md
│   ├── USER.md
│   ├── IDENTITY.md
│   ├── TOPICS.md
│   ├── SCOREBOARD.md
│   └── core/（全部文档）
├── H盘音视频文件                   → /data/audio/
├── 转写结果                       → /data/transcripts/
└── 清洗文档                       → /data/docs/
```

**迁移后需要修改的配置项：**
1. config.yaml中所有Windows路径 → Linux路径
2. cron jobs中的workdir路径
3. .env文件中的路径（如果有）
4. SOUL.md/USER.md中引用的路径
5. GitHub备份仓库的remote URL（如果有代理配置差异）

---

*本指南由Hermes Agent（Windows）生成，供VPS运维Agent在RF-Lenovo机器上执行。*
*如有疑问，通过飞书群向锋哥的主agent（Windows）确认。*
