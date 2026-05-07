# Hermes WSL2：换 Key、Fallback、Gateway 保活、ClawMem 完整运维方案

最后更新：2026-05-07

> 目标：以后更换 GLM / 阿里百炼 Key、调整模型 fallback、重启 Gateway、启用 ClawMem 时，有一份不泄露密钥、可回滚、可验证的标准操作文档。

---

## 0. 当前架构总览

机器：

```text
Windows 主机：WIN-RBARICJ02HS
Tailscale IP：100.68.184.107
WSL 发行版：Ubuntu-22.04
WSL 用户：root
Hermes Home：/root/.hermes
Hermes 项目：/root/.hermes/hermes-agent
```

核心路径：

```text
Hermes 配置：/root/.hermes/config.yaml
Hermes 密钥：/root/.hermes/.env
Gateway 日志：/root/.hermes/gateway.log
Hermes 错误日志：/root/.hermes/logs/errors.log
Gateway 启动脚本：/root/hermes_run.sh
Windows 重启脚本：C:\Users\Administrator\hermes_restart.ps1
外部 Agent 入口：C:\Users\Administrator\hermes_restart.bat
Windows 开机自启：C:\Users\Administrator\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\hermes_gateway.bat
Windows 登录任务：HermesGatewayWSL2
ClawMem CLI：/usr/local/bin/clawmem
ClawMem 索引库：/root/.cache/clawmem/index.sqlite
ClawMem 配置：/root/.config/clawmem/index.yml
```

关键原则：

- 真实 API Key 只写入 `/root/.hermes/.env`，不要写进 `config.yaml`、文档、飞书、Notion、Git。
- 改 key 前必须备份 `.env`。
- 改模型结构前必须备份 `config.yaml`。
- 只改 `.env` 不会自动影响已经运行中的 Gateway；要让新 key 生效，需要在合适时间重启 Gateway。
- 外部 Agent 重启 Gateway 必须通过 Windows `schtasks`，不要直接 SSH 后运行 bat。
- ClawMem 当前推荐使用 BM25 检索；不要直接拿 DashScope embedding 做批量向量化，除非 ClawMem 已修复 batch input 兼容。

---

## 1. 标准 SSH 入口

从 Mac / 外部机器进入 Windows：

```bash
ssh Administrator@100.68.184.107
```

进入 WSL：

```powershell
wsl -d Ubuntu-22.04 -u root
```

如果只是执行一条 WSL 命令：

```powershell
wsl -d Ubuntu-22.04 -u root -- bash -lc "你的命令"
```

复杂脚本不要塞进一行命令，先写到 `C:\Temp\xxx.sh`，再用：

```powershell
wsl -d Ubuntu-22.04 -u root -- bash /mnt/c/Temp/xxx.sh
```

---

## 2. Key 管理总原则

### 2.1 哪些 Key 在哪里

```text
GLM_API_KEY：智谱 / GLM，主模型 zai / glm-5-turbo 使用
DASHSCOPE_API_KEY：阿里百炼，Qwen / DeepSeek fallback 和手动切换使用
FEISHU_APP_ID / FEISHU_APP_SECRET：飞书 Gateway 使用
CLAWMEM_*：ClawMem 插件和检索服务使用
```

全部放在：

```text
/root/.hermes/.env
```

权限应为：

```bash
chmod 600 /root/.hermes/.env
```

### 2.2 改 Key 前备份

进入 WSL 后执行：

```bash
STAMP="$(date +%F-%H%M%S)"
cp -a /root/.hermes/.env "/root/.hermes/.env.bak.$STAMP"
chmod 600 /root/.hermes/.env
ls -l "/root/.hermes/.env.bak.$STAMP" /root/.hermes/.env
```

### 2.3 不要这样改 Key

不要把真实 key 写在命令行里，例如不要这样：

```bash
hermes config set DASHSCOPE_API_KEY "真实key"
```

也不要这样：

```bash
echo "DASHSCOPE_API_KEY=真实key" >> /root/.hermes/.env
```

原因：命令历史、进程列表、远程日志里都可能留下密钥。

推荐使用下面的交互式方式。

---

## 3. 更换或新增阿里百炼 Key

适用场景：

- 上一个阿里百炼账号欠费。
- 要换新的百炼 API Key。
- Qwen / DeepSeek fallback 401、欠费、余额不足、认证失败。

当前推荐做法：

- 如果旧 key 下个月还会恢复，不要直接删除旧 key。
- 新 key 加入 Hermes credential pool，并把新 key 排在第一位。
- 旧 key 保留在池子里，等新 key 也限流或下月旧 key 恢复时可继续使用。
- `DASHSCOPE_API_KEY` 可以继续保留旧 key；真正运行时优先使用 credential pool。

当前机器已配置为：

```text
custom:bailian:
1. bailian-backup-202605  当前优先
2. bailian-primary-env    旧 key 备用

alibaba:
1. bailian-backup-202605  当前优先
2. DASHSCOPE_API_KEY      旧 key 备用
```

### 3.1 先用新 Key 做临时测试，不改配置

进入 WSL：

```bash
read -rsp "Paste NEW DASHSCOPE_API_KEY: " NEW_DASHSCOPE_API_KEY
echo
export NEW_DASHSCOPE_API_KEY
```

测试 Qwen：

```bash
curl -sS https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions \
  -H "Authorization: Bearer $NEW_DASHSCOPE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen3.6-plus",
    "messages": [
      {"role": "user", "content": "只回复 OK"}
    ]
  }'
```

测试 DeepSeek V4 Flash：

```bash
curl -sS https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions \
  -H "Authorization: Bearer $NEW_DASHSCOPE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deepseek-v4-flash",
    "messages": [
      {"role": "user", "content": "只回复 OK"}
    ],
    "enable_thinking": false
  }'
```

成功标准：

```text
HTTP 返回 200
response_model 为 qwen3.6-plus / deepseek-v4-flash
内容里出现 OK
```

如果这里失败，不要写入 `.env`，先检查百炼账号余额、模型权限、地域和 Key 是否复制完整。

### 3.2 推荐：把新 Key 加入 credential pool

确认临时测试成功后，进入 Hermes 运行环境：

```bash
source /root/.hermes/hermes-agent/venv/bin/activate
hermes auth add custom:bailian --type api-key --label bailian-backup-YYYYMM
hermes auth add alibaba --type api-key --label bailian-backup-YYYYMM
```

命令会安全提示输入 key。不要把真实 key 直接写在命令行参数里。

然后把新 key 调整为优先级第一，旧 key 保留第二：

```bash
STAMP="$(date +%F-%H%M%S)"
cp -a /root/.hermes/auth.json "/root/.hermes/auth.json.bak.$STAMP"

python3 - <<'PY'
import json, os, time
from pathlib import Path

path = Path("/root/.hermes/auth.json")
data = json.loads(path.read_text(encoding="utf-8"))

for provider in ["custom:bailian", "alibaba"]:
    entries = data.get("credential_pool", {}).get(provider, [])
    for entry in entries:
        label = entry.get("label", "")
        if label.startswith("bailian-backup-"):
            entry["priority"] = 0
            entry["last_status"] = None
            entry["last_status_at"] = None
            entry["last_error_code"] = None
            entry["last_error_reason"] = None
            entry["last_error_message"] = None
            entry["last_error_reset_at"] = None
        elif label in ("DASHSCOPE_API_KEY", "bailian-primary-env"):
            entry["priority"] = 1
    entries.sort(key=lambda e: (e.get("priority", 999), e.get("label", "")))

data["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
os.chmod(path, 0o600)
PY
```

确认只显示 label，不显示真实 key：

```bash
hermes auth list
```

### 3.3 改 Key 后什么时候需要重启

`auth.json`、`.env`、Hermes 代码补丁都只会被新进程稳定读取。当前正在运行的 Hermes Gateway 不会自动重新加载完整运行时。

所以：

- 如果当前飞书对话正在跑任务，先不要重启。
- 配完新 key 后，新的 CLI 临时会话可以立刻验证。
- 要让新 key 对飞书 Gateway 生效，需要计划重启 Gateway。

重启方式见第 6 节。

### 3.4 回滚 Key

如果新 key 写错了：

```bash
cp -a /root/.hermes/.env.bak.具体时间戳 /root/.hermes/.env
chmod 600 /root/.hermes/.env
```

然后在合适时间重启 Gateway。

---

## 4. 更换 GLM_API_KEY

GLM 是主模型 `zai / glm-5-turbo` 使用的 key。

流程和百炼一致，只是变量名不同。

进入 WSL 后：

```bash
read -rsp "Paste NEW GLM_API_KEY: " NEW_GLM_API_KEY
echo
export NEW_GLM_API_KEY
```

写入：

```bash
STAMP="$(date +%F-%H%M%S)"
cp -a /root/.hermes/.env "/root/.hermes/.env.bak.$STAMP"

python3 - <<'PY'
import os
from pathlib import Path

path = Path("/root/.hermes/.env")
new_key = os.environ["NEW_GLM_API_KEY"].strip()
lines = path.read_text(encoding="utf-8", errors="replace").splitlines()

out = []
seen = False
for line in lines:
    if line.startswith("GLM_API_KEY="):
        out.append(f"GLM_API_KEY={new_key}")
        seen = True
    else:
        out.append(line)

if not seen:
    if out and out[-1].strip():
        out.append("")
    out.append(f"GLM_API_KEY={new_key}")

path.write_text("\n".join(out).rstrip() + "\n", encoding="utf-8")
PY

unset NEW_GLM_API_KEY
chmod 600 /root/.hermes/.env
```

改完后也需要计划重启 Gateway 才会影响飞书正在使用的 Gateway 进程。

---

## 5. 模型配置与 Fallback

### 5.1 推荐 config.yaml 结构

`/root/.hermes/config.yaml` 里不要放真实 key。

关键结构应类似：

```yaml
model:
  provider: zai
  default: glm-5-turbo
  base_url: https://open.bigmodel.cn/api/coding/paas/v4

providers:
  zai:
    model: glm-5-turbo
    base_url: https://open.bigmodel.cn/api/coding/paas/v4

custom_providers:
  - name: bailian
    base_url: https://dashscope.aliyuncs.com/compatible-mode/v1
    key_env: DASHSCOPE_API_KEY
    api_mode: chat_completions

fallback_providers:
  - provider: custom:bailian
    model: qwen3.6-plus
  - provider: custom:bailian
    model: deepseek-v4-flash

model_aliases:
  glm:
    provider: zai
    model: glm-5-turbo
  qwen:
    provider: custom:bailian
    model: qwen3.6-plus
  deepseek:
    provider: custom:bailian
    model: deepseek-v4-flash
  deepseek-flash:
    provider: custom:bailian
    model: deepseek-v4-flash
```

### 5.2 修改 config 前备份

```bash
STAMP="$(date +%F-%H%M%S)"
cp -a /root/.hermes/config.yaml "/root/.hermes/config.yaml.bak.$STAMP"
```

### 5.3 验证 fallback

```bash
source /root/.hermes/hermes-agent/venv/bin/activate
hermes fallback list
```

期望看到：

```text
Primary: glm-5-turbo (via zai)
Fallback chain:
1. qwen3.6-plus
2. deepseek-v4-flash
```

已额外补丁：

```text
agent/auxiliary_client.py：named custom provider 优先读取 credential pool
run_agent.py：fallback 激活后把 fallback provider 的 credential pool 带入当前 agent
```

这解决的是：Hermes 原版在 fallback 到 `custom:bailian` 时可能仍读 `.env` 的旧 `DASHSCOPE_API_KEY`，没有真正走两把 key 自动轮换。

### 5.4 验证别名

这些命令会开短命 CLI 会话，不影响飞书 Gateway：

```bash
source /root/.hermes/hermes-agent/venv/bin/activate
hermes chat -q "只回复 OK" -m qwen --ignore-rules --max-turns 1 -Q
hermes chat -q "只回复 OK" -m deepseek-v4-flash --provider custom:bailian --ignore-rules --max-turns 1 -Q
```

成功标准：都回复 `OK`。

验证 `/model deepseek` 别名解析：

```bash
source /root/.hermes/hermes-agent/venv/bin/activate
python3 - <<'PY'
from hermes_cli.env_loader import load_hermes_dotenv
load_hermes_dotenv()
from hermes_cli.config import load_config
from hermes_cli.model_switch import switch_model
cfg = load_config()
r = switch_model(
    "deepseek",
    current_provider="zai",
    current_model="glm-5-turbo",
    custom_providers=cfg.get("custom_providers"),
)
print(r.success, r.target_provider, r.new_model, r.resolved_via_alias)
PY
```

期望输出类似：

```text
True custom:bailian deepseek-v4-flash deepseek
```

### 5.5 飞书里手动切模型

当前会话临时切 DeepSeek V4 Flash：

```text
/model deepseek
```

完整写法：

```text
/model deepseek-v4-flash --provider custom:bailian
```

当前 Hermes 版本不要依赖 `/model custom:bailian:deepseek-v4-flash` 这种冒号串联写法；源码里 `/model` 使用 `--provider` 指定 provider，冒号主要保留给模型变体后缀。

切 Qwen：

```text
/model qwen
```

切回 GLM：

```text
/model glm
```

注意：

- `/model` 只影响当前会话。
- 正在执行中的任务可能不能中途切；先等当前轮结束。
- 如果加 `--global` 才会写全局默认，一般不建议在飞书里加。

---

## 6. Gateway 保活与重启

### 6.1 为什么不用 nohup / screen / systemd

当前 WSL 内核为 5.10.x，且 WSL 实例在没有 Windows 侧持有者时会关闭。

这些方案不可靠：

```text
nohup：只能防 SIGHUP，不能防 WSL 实例关闭
screen/tmux：WSL 关闭时一起被清理
systemd：这台机器上不是可靠控制面
SSH 里直接后台启动：SSH 断开后仍可能影响子进程链路
```

最终方案：

```text
Windows 计划任务 / 登录任务
  -> hermes_restart.bat
    -> hermes_restart.ps1
      -> Start-Process wsl.exe
        -> /root/hermes_run.sh
          -> /root/.hermes/hermes-agent/venv/bin/hermes gateway run --replace
```

### 6.2 /root/hermes_run.sh

内容应为：

```bash
#!/usr/bin/env bash
set -euo pipefail
cd /root/.hermes/hermes-agent
exec /root/.hermes/hermes-agent/venv/bin/hermes gateway run --replace >> /root/.hermes/gateway.log 2>&1
```

权限：

```bash
chmod 755 /root/hermes_run.sh
```

### 6.3 /etc/wsl.conf

内容应为：

```ini
[user]
default=root

[boot]
systemd=false
```

### 6.4 Windows 重启脚本

`C:\Users\Administrator\hermes_restart.ps1` 应负责：

- 杀旧 Gateway。
- `Start-Process wsl.exe` 启动独立 WSL 进程。
- WSL 内运行 `/root/hermes_run.sh`。
- 8 秒后检查 Gateway 进程。
- 写日志到 `C:\Users\Administrator\hermes_gateway_start.log`。

### 6.5 外部 Agent 正确重启方式

通过 SSH 到 Windows 后，不要直接运行 bat。

正确方式：

```powershell
schtasks /Create /TN HermesRestartOnce /TR "C:\Users\Administrator\hermes_restart.bat" /SC ONCE /ST 23:59 /F
schtasks /Run /TN HermesRestartOnce
```

等待 10-20 秒后检查：

```powershell
wsl -d Ubuntu-22.04 -u root -- bash -lc "ps aux | grep '[h]ermes gateway'"
```

检查飞书连接日志：

```powershell
wsl -d Ubuntu-22.04 -u root -- bash -lc "tail -30 /root/.hermes/gateway.log"
```

如输出里有 `connected to wss://msg-frontier.feishu.cn/...`，说明飞书 WebSocket 已连接。

### 6.6 冷启动验收

只有在允许中断 Gateway 时执行：

```powershell
wsl --shutdown
schtasks /Create /TN HermesRestartOnce /TR "C:\Users\Administrator\hermes_restart.bat" /SC ONCE /ST 23:59 /F
schtasks /Run /TN HermesRestartOnce
```

等待 20 秒：

```powershell
wsl -d Ubuntu-22.04 -u root -- bash -lc "date -Is; ps aux | grep '[h]ermes gateway'; tail -30 /root/.hermes/gateway.log"
```

成功标准：

```text
Gateway 进程存在
日志出现 Hermes Gateway Starting
日志出现 Lark / Feishu WebSocket connected
```

---

## 7. ClawMem 完整方案

### 7.1 当前定位

ClawMem 是 Hermes 的记忆检索外挂。

当前推荐工作模式：

```text
BM25 关键词检索：启用，已验证
REST API：由 Hermes 插件 managed 模式自动拉起
向量 embedding：暂不启用
watch 守护：暂不启用，新增文档后手动 clawmem update
```

为什么先不用 embedding：

- 当前只有几十到一百级别 Markdown 文档，BM25 已能精准命中。
- DashScope embedding 对 batch input 兼容存在风险。
- `clawmem query` 依赖本地 LLM 扩展查询，默认连 `http://localhost:8089/v1/chat/completions`；该服务没开时会 ConnectionRefused。
- 不启用 embedding 不影响 `clawmem search`、REST `/retrieve`、Hermes `clawmem_retrieve`。

### 7.2 ClawMem 二进制

应存在：

```bash
/root/.bun/bin/clawmem
/usr/local/bin/clawmem
```

如果 `/usr/local/bin/clawmem` 不存在：

```bash
ln -sfn /root/.bun/bin/clawmem /usr/local/bin/clawmem
```

验证：

```bash
command -v clawmem
clawmem help
```

### 7.3 Hermes .env 中的 ClawMem 配置

`/root/.hermes/.env` 应包含：

```text
CLAWMEM_BIN=/usr/local/bin/clawmem
CLAWMEM_SERVE_MODE=managed
CLAWMEM_SERVE_PORT=7438
CLAWMEM_PROFILE=balanced
```

含义：

```text
CLAWMEM_BIN：Hermes 插件用这个绝对路径找 clawmem
CLAWMEM_SERVE_MODE=managed：Hermes 插件启动时自动拉起 clawmem serve
CLAWMEM_SERVE_PORT=7438：REST API 端口
CLAWMEM_PROFILE=balanced：检索策略平衡模式
```

### 7.4 Hermes config.yaml 中的 ClawMem 配置

关键结构：

```yaml
memory:
  memory_enabled: true
  user_profile_enabled: true
  memory_char_limit: 2200
  user_char_limit: 1375
  provider: clawmem
  clawmem_serve_mode: managed

plugins:
  enabled:
    - clawmem
  disabled: []
```

### 7.5 ClawMem 索引配置

`/root/.config/clawmem/index.yml`：

```yaml
collections:
  aios-core:
    path: /root/workspace/aios/core
    pattern: "**/*.md"
```

### 7.6 初始化或刷新索引

手动刷新：

```bash
clawmem update
```

验证状态：

```bash
clawmem status
clawmem doctor
```

成功标准：

```text
Database 存在
Documents 大于 0
Collection 指向 /root/workspace/aios/core
doctor 显示 All checks passed
```

示例：

```bash
clawmem search 记忆 -n 3
clawmem search 音频 -n 3
clawmem search Hermes -n 3
```

如果能返回 `aios-core/...md` 文档，BM25 已经工作。

### 7.7 REST API 验证

如果 Gateway 没有运行，或只是想临时验证：

```bash
clawmem serve --host 127.0.0.1 --port 7438
```

另一个终端测试：

```bash
curl -sS http://127.0.0.1:7438/health
```

检索：

```bash
curl -sS http://127.0.0.1:7438/retrieve \
  -H "Content-Type: application/json" \
  -d '{"query":"记忆","limit":3,"compact":true}'
```

如果 Gateway 已经运行且 ClawMem managed 模式生效，不要再手动启动同一个 7438 端口，避免端口冲突。

### 7.8 Hermes 插件验证

Gateway 重启后，检查是否由 Hermes managed 模式拉起：

```bash
ps aux | grep '[c]lawmem.*serve'
ss -ltn | awk 'NR==1 || /:7438/'
```

检查日志：

```bash
rg 'clawmem:' /root/.hermes/gateway.log /root/.hermes/logs
```

理想日志：

```text
clawmem: managed serve ready
clawmem: session-bootstrap returned ...
clawmem: registered ... tools
```

飞书侧识别：

- 问 Hermes “查一下记忆里关于音频转写的记录”。
- 如果它使用 `clawmem_retrieve` / `clawmem_get` 工具，并返回 `/root/workspace/aios/core` 里的文档，说明插件真正接上。

### 7.9 ClawMem 常见误区

`clawmem search`：

```text
BM25 关键词搜索，不需要 embedding，不需要 LLM。
当前推荐主要用这个。
```

`clawmem query`：

```text
混合检索 + 查询扩展 + 可能用向量/LLM。
如果本地 LLM http://localhost:8089 没开，可能 ConnectionRefused。
当前不建议作为验收依据。
```

`clawmem embed`：

```text
生成向量索引。
如果接 DashScope embedding，需注意 ClawMem 可能批量发送 input 数组，而 DashScope 兼容性不一定满足。
当前不建议启用。
```

`clawmem watch`：

```text
文件变化自动更新索引。
当前不是必须。新增文档后手动 clawmem update 即可。
```

---

## 8. 新增文档后的日常维护

如果 `/root/workspace/aios/core` 里新增或修改了 Markdown：

```bash
clawmem update
clawmem search 关键词 -n 5
```

如果只是少量文档，通常 1-2 秒到几十秒内完成。

如果 `clawmem update` 输出 LLM 8089 ConnectionRefused：

```text
这是高级增强层失败，不代表 BM25 不可用。
只要 status 文档数更新、search 能搜到，就说明基础记忆检索可用。
```

---

## 9. 完整验收清单

### 9.1 Key 与模型

```bash
grep -E '^(GLM_API_KEY|DASHSCOPE_API_KEY)=' /root/.hermes/.env | sed 's/=.*/=present/'
source /root/.hermes/hermes-agent/venv/bin/activate
hermes auth list
hermes fallback list
hermes chat -q "只回复 OK" -m qwen --ignore-rules --max-turns 1 -Q
hermes chat -q "只回复 OK" -m deepseek-v4-flash --provider custom:bailian --ignore-rules --max-turns 1 -Q
```

如果要验证自动 fallback，临时指定一个不存在的 GLM 模型：

```bash
hermes chat -q "只回复 OK" -m definitely-not-a-real-model --provider zai --ignore-rules --max-turns 1 -Q
```

成功标准：最终仍回复 `OK`，日志里出现 `Fallback activated ... qwen3.6-plus (custom:bailian)`。

### 9.2 Gateway

```bash
ps aux | grep '[h]ermes gateway'
tail -30 /root/.hermes/gateway.log
```

### 9.3 ClawMem

```bash
command -v clawmem
clawmem doctor
clawmem status
clawmem search 记忆 -n 3
```

Gateway 重启后再查：

```bash
ps aux | grep '[c]lawmem.*serve'
ss -ltn | awk 'NR==1 || /:7438/'
```

---

## 10. 一键诊断脚本

进入 WSL 后可执行：

```bash
cat > /tmp/hermes_stack_check.sh <<'EOF'
#!/usr/bin/env bash
set +e

echo "== time =="
date -Is

echo "== gateway =="
ps aux | grep '[h]ermes gateway' || true

echo "== keys =="
grep -E '^(GLM_API_KEY|DASHSCOPE_API_KEY|CLAWMEM_BIN|CLAWMEM_SERVE_MODE|CLAWMEM_SERVE_PORT|CLAWMEM_PROFILE)=' /root/.hermes/.env | sed 's/=.*/=present/'

echo "== fallback =="
source /root/.hermes/hermes-agent/venv/bin/activate
hermes fallback list 2>/dev/null || true

echo "== clawmem =="
command -v clawmem || true
clawmem status 2>/dev/null || true
clawmem search 记忆 -n 3 2>/dev/null | sed -n '1,60p'

echo "== ports =="
ss -ltn | awk 'NR==1 || /:7438/'

echo "== logs =="
tail -20 /root/.hermes/gateway.log 2>/dev/null | sed -E 's/access_key=[^& ]+/access_key=[REDACTED]/g; s/ticket=[^& ]+/ticket=[REDACTED]/g; s/conn_id=[^]]+/conn_id=[REDACTED]/g'
EOF

bash /tmp/hermes_stack_check.sh
```

---

## 11. 回滚策略

### 11.1 回滚 `.env`

```bash
ls -lt /root/.hermes/.env.bak.* | head
cp -a /root/.hermes/.env.bak.目标时间戳 /root/.hermes/.env
chmod 600 /root/.hermes/.env
```

回滚后，计划重启 Gateway。

### 11.2 回滚 `config.yaml`

```bash
ls -lt /root/.hermes/config.yaml.bak.* | head
cp -a /root/.hermes/config.yaml.bak.目标时间戳 /root/.hermes/config.yaml
```

回滚后，计划重启 Gateway。

### 11.3 Gateway 重启失败时

先看 Windows 启动日志：

```powershell
Get-Content C:\Users\Administrator\hermes_gateway_start.log -Tail 80
```

再看 WSL 日志：

```powershell
wsl -d Ubuntu-22.04 -u root -- bash -lc "tail -80 /root/.hermes/gateway.log"
```

最后手动短跑测试：

```powershell
wsl -d Ubuntu-22.04 -u root -- bash -lc "cd /root/.hermes/hermes-agent && timeout 20s /root/.hermes/hermes-agent/venv/bin/hermes gateway run --replace"
```

短跑能连上飞书，说明 Hermes 本身没坏，问题在 Windows 保活启动链路。

---

## 12. 建议的日常操作顺序

换阿里百炼 Key：

```text
1. 用 NEW_DASHSCOPE_API_KEY 临时 curl 测 qwen3.6-plus
2. 用 NEW_DASHSCOPE_API_KEY 临时 curl 测 deepseek-v4-flash
3. 备份 auth.json
4. 把新 key 加入 custom:bailian 和 alibaba credential pool
5. 把新 key label 调整为 priority 0，旧 key 保留 priority 1
6. hermes auth list + hermes fallback list
7. 用短命 CLI 验证 qwen3.6-plus / deepseek-v4-flash
8. 等当前飞书任务空闲
9. 用 schtasks 重启 Gateway
10. 飞书发 /model qwen 或 /model deepseek 验证
```

ClawMem 日常：

```text
1. 新增/修改 core 文档
2. clawmem update
3. clawmem search 关键词 -n 5
4. Gateway 下次重启后，Hermes 插件会 managed 拉起 clawmem serve
```

Gateway 保活：

```text
1. 不直接 SSH 后台启动
2. 一律 schtasks 触发 C:\Users\Administrator\hermes_restart.bat
3. 检查 ps aux 是否有 hermes gateway
4. 检查 gateway.log 是否有 Feishu WebSocket connected
```
