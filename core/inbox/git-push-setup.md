# Git Push 自动同步配置任务

## 背景
老板晚上用飞书跟你协作，产出的上下文第二天锋哥（Mac端WorkBuddy）看不到。需要你自动把关键文件push到GitHub，锋哥那边pull下来。

## 前置条件
- SSH密钥已复制到 `C:\Users\Administrator\.ssh\id_ed25519`
- Git仓库：`C:\Users\Administrator\.openclaw\workspace`，remote `git@github.com:rf2025up/aios.git`
- git config: user.name=锋哥, user.email=fengge@openclaw.ai

## 你需要做的

### Step 1: 验证SSH连接
```bash
ssh -T git@github.com
```
如果返回 `Hi rf2025up!` 就OK。如果失败，检查：
- `C:\Users\Administrator\.ssh\id_ed25519` 是否存在
- 文件权限是否正确（只有当前用户可读）

### Step 2: 首次pull测试
```bash
cd C:\Users\Administrator\.openclaw\workspace
git pull --rebase origin main
```

### Step 3: 创建git push脚本
在 `C:\Users\Administrator\.openclaw\scripts\` 下创建 `git-push.ps1`：

```powershell
# git-push.ps1 - 自动commit+push workspace变更
$ErrorActionPreference = "Continue"
$workspaceDir = "C:\Users\Administrator\.openclaw\workspace"

cd $workspaceDir

# pull first (rebase, 冲突不硬解)
git pull --rebase 2>&1 | Out-Null

# add关键目录
git add core/ daily/ MEMORY.md memory/ inbox/ 2>&1 | Out-Null

# 检查有没有变更
$status = git status --porcelain 2>&1
if ($status) {
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm"
    git commit -m "openclaw: auto-sync $timestamp" 2>&1 | Out-Null
    git push origin HEAD 2>&1
    Write-Host "PUSHED at $timestamp"
} else {
    Write-Host "NO CHANGES at $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
}
```

### Step 4: 创建cron任务
用 `openclaw cron add` 添加一个每小时执行的任务：

```
名称: git自动同步
Schedule: 每小时 (0 * * * *)
Prompt: 执行git-push.ps1脚本，将workspace的core/、daily/、MEMORY.md、memory/、inbox/目录自动commit和push到GitHub。先pull --rebase，再add/commit/push。不需要发飞书通知。
Target: isolated
Delivery: silent（不发消息）
```

或者如果cron不支持silent，prompt里写明"执行完不要发飞书消息"。

### Step 5: 手动测试一次
先运行一次git-push.ps1，确认能正常push。

## 注意事项
- 只push关键目录（core/, daily/, MEMORY.md, memory/, inbox/），不要全量add
- commit message格式：`openclaw: auto-sync YYYY-MM-DD HH:mm`
- pull冲突时不要force，记录日志即可
- 这个cron是🟢级别的（每小时，静默执行）

## 完成后
在飞书群发一条消息确认："git自动同步已配置完成，每小时push一次。"
