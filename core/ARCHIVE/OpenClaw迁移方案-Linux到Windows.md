# OpenClaw 迁移方案：笔记本(Linux) → 新电脑(Windows)

## 环境信息
- **旧机**：rf@192.168.1.109，Ubuntu Linux，用户 `rf`
- **新机**：Windows（全新），用户名待确认（WorkBuddy知道）
- **数据总量**：~7GB（FunASR模型缓存占2.1G，虚拟环境5.2G）

## Phase 1：新机环境准备

### 1.1 安装 Node.js（通过nvm）
```powershell
# 打开PowerShell，安装nvm-windows
# 下载地址：https://github.com/coreybutler/nvm-windows/releases
# 安装nvm-setup.exe后：
nvm install 22
nvm use 22
node --version   # 应该显示 v22.x.x
npm --version
```

### 1.2 安装 OpenClaw
```powershell
npm install -g openclaw
openclaw setup
openclaw --version
```

### 1.3 安装 Python（FunASR需要）
```powershell
# 下载Python 3.11+：https://www.python.org/downloads/
# 安装时勾选 "Add to PATH"
python --version
pip --version
```

## Phase 2：从旧机打包数据

SSH到笔记本执行（WorkBuddy已配好SSH，直接连）：

```bash
ssh rf@192.168.1.109

# 停掉openclaw，避免数据不一致
openclaw gateway stop
pkill -f chrome 2>/dev/null

# 打包核心数据（排除funasr-env虚拟环境，Windows不能直接用）
cd ~
tar czf /tmp/openclaw-migrate.tar.gz \
  .openclaw/openclaw.json \
  .openclaw/clawpanel.json \
  .openclaw/exec-approvals.json \
  .openclaw/agents/ \
  .openclaw/extensions/ \
  .openclaw/workspace/ \
  .openclaw/workspace-edu/ \
  .openclaw/browser/

# 单独打包FunASR模型缓存（跨平台通用，不需要重新下载）
tar czf /tmp/openclaw-models.tar.gz \
  .cache/modelscope/

# 看下大小
ls -lh /tmp/openclaw-migrate.tar.gz
ls -lh /tmp/openclaw-models.tar.gz
```

## Phase 3：传到Windows

在WorkBuddy那边scp到Windows（假设Windows IP是NEW_IP）：
```bash
scp rf@192.168.1.109:/tmp/openclaw-migrate.tar.gz ~/openclaw-migrate.tar.gz
scp rf@192.168.1.109:/tmp/openclaw-models.tar.gz ~/openclaw-models.tar.gz
```

## Phase 4：在Windows上解压

```powershell
# 创建.openclaw目录
mkdir $env:USERPROFILE\.openclaw

# 解压核心数据（用tar，Windows 10+自带）
cd $env:USERPROFILE
tar xzf openclaw-migrate.tar.gz

# 解压模型缓存
mkdir $env:USERPROFILE\.cache
cd $env:USERPROFILE\.cache
tar xzf ..\openclaw-models.tar.gz

# 验证
dir $env:USERPROFILE\.openclaw\openclaw.json
dir $env:USERPROFILE\.openclaw\workspace\SOUL.md
dir $env:USERPROFILE\.openclaw\workspace-edu
```

## Phase 5：修改配置中的路径（关键！）

旧机路径是 `/home/rf/...`，Windows要改成 `C:/Users/WIN_USERNAME/...`

```powershell
cd $env:USERPROFILE\.openclaw

# 先看当前用户名
$USER = $env:USERNAME
$HOME_PATH = "C:/Users/$USER"

# 替换openclaw.json中的路径
(Get-Content openclaw.json) -replace '/home/rf', $HOME_PATH | Set-Content openclaw.json

# 替换agents下的session历史文件
Get-ChildItem -Path agents -Filter "*.jsonl" -Recurse | ForEach-Object {
    (Get-Content $_.FullName -Raw) -replace '/home/rf', $HOME_PATH | Set-Content $_.FullName
}

# 替换exec-approvals.json
if (Test-Path exec-approvals.json) {
    (Get-Content exec-approvals.json) -replace '/home/rf', $HOME_PATH | Set-Content exec-approvals.json
}

# 验证：不应该再有 /home/rf
Select-String -Path openclaw.json -Pattern "/home/rf"
# 应该返回空
```

## Phase 6：安装 FunASR（Windows版）

FunASR是纯Python，Windows原生支持。虚拟环境不能从Linux直接拷贝，需要重建：

```powershell
# 创建Python虚拟环境
python -m venv $env:USERPROFILE\.openclaw\funasr-env

# 激活
.\$env:USERPROFILE\.openclaw\funasr-env\Scripts\Activate.ps1

# 安装依赖
pip install funasr modelscope torch torchaudio

# 测试
python -c "from funasr import AutoModel; print('FunASR OK')"
```

> **注意**：如果Windows是NVIDIA显卡且有CUDA，PyTorch会自动用GPU加速，转写速度更快。
> 安装CUDA版PyTorch：`pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121`

> **模型权重已经通过Phase 3拷贝过来了**，放在 `~/.cache/modelscope/`，首次运行不需要重新下载。

## Phase 7：修改FunASR脚本路径

锋哥workspace里有抖音转写脚本，路径需要更新：

```powershell
# 检查scripts目录
dir $env:USERPROFILE\.openclaw\workspace\scripts\

# 脚本里的FunASR Python路径需要改
# Linux: ~/.openclaw/funasr-env/bin/python3
# Windows: ~/openclaw/funasr-env/Scripts/python.exe
```

转写脚本中所有 `~/.openclaw/funasr-env/bin/python3` 需要改成：
```powershell
$env:USERPROFILE\.openclaw\funasr-env\Scripts\python.exe
```

## Phase 8：启动OpenClaw

```powershell
# 检查配置
openclaw status

# 启动
openclaw gateway start

# 验证飞书连接
openclaw gateway status
```

## Phase 9：验证清单

- [ ] 飞书私聊发消息给锋哥 → 能正常回复
- [ ] 群"小龙的卓越之路" @小园老师 → 能响应
- [ ] `openclaw agents list` → 显示 main + edu
- [ ] 浏览器功能正常（`openclaw browser` 相关）
- [ ] FunASR转写测试通过

## 注意事项

| 项目 | 说明 |
|------|------|
| **路径分隔符** | openclaw.json里用的是 `/`，Windows也认，不用改成 `\` |
| **Chrome profile** | browser目录下的登录态可能需要重新登录（抖音等） |
| **ffmpeg** | 转写脚本依赖ffmpeg，Windows需要单独安装：`winget install ffmpeg` 或从 https://ffmpeg.org/download.html 下载 |
| **代理** | 如果用clash等代理，确保端口一致（当前配置的是127.0.0.1:7897） |
| **开机自启** | Windows下可以设为计划任务或启动项：`shell:startup` 放一个 `openclaw gateway start` 的bat |
| **cron任务** | OpenClaw的cron跟着config走，不用重新设置 |
| **旧机停服** | 迁移成功后，笔记本上 `openclaw gateway stop`，避免两个实例同时连飞书 |

## 旧机清理（迁移成功后）

```bash
# 在笔记本上
openclaw gateway stop
rm -f /tmp/openclaw-migrate.tar.gz /tmp/openclaw-models.tar.gz
```
