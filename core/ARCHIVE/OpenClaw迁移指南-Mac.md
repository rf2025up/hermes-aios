# OpenClaw 迁移指南：笔记本(rf) → Mac(win)

## 环境信息
- **旧机器**：rf@192.168.1.109，Ubuntu Linux，用户 `rf`
- **新机器**：Mac，用户 `win`
- **数据总量**：~7GB（FunASR占5.2GB）
- **Mac已有**：nvm + node v22 + openclaw

## Step 0: 确认SSH连通性

在Mac上测试能否SSH到笔记本：
```bash
ssh -i ~/.ssh/id_ed25519 rf@192.168.1.109 "whoami && hostname"
```
如果失败，先在笔记本上添加Mac的公钥到 `~/.ssh/authorized_keys`。

## Step 1: 在旧机器（笔记本）上打包

SSH到笔记本执行：
```bash
ssh -i ~/.ssh/id_ed25519 rf@192.168.1.109

# 先停掉openclaw gateway，避免数据不一致
openclaw gateway stop || true
pkill -f chrome || true

# 打包（排除funasr-env的模型缓存，节省空间）
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

# 看下大小
ls -lh /tmp/openclaw-migrate.tar.gz
# 预期：~500MB（不含FunASR）
```

**如果也要带FunASR**（新机器需要跑本地语音识别，32G内存跑起来很爽）：
```bash
tar czf /tmp/openclaw-migrate-full.tar.gz \
  .openclaw/
ls -lh /tmp/openclaw-migrate-full.tar.gz
# 预期：~2-3GB（压缩后）
```

## Step 2: 传到Mac

在Mac上执行（笔记本IP=192.168.1.109）：
```bash
# 传到Mac（局域网应该很快，几分钟）
scp -i ~/.ssh/id_ed25519 \
  rf@192.168.1.109:/tmp/openclaw-migrate-full.tar.gz \
  ~/Desktop/openclaw-migrate-full.tar.gz
```

如果传输中断，支持断点续传（需要笔记本装rsync）：
```bash
rsync -avP --partial \
  -e "ssh -i ~/.ssh/id_ed25519" \
  rf@192.168.1.109:/tmp/openclaw-migrate-full.tar.gz \
  ~/Desktop/openclaw-migrate-full.tar.gz
```

## Step 3: 在Mac上解压

```bash
# 备份Mac上已有的openclaw数据（如果有的话）
[ -d ~/.openclaw ] && mv ~/.openclaw ~/.openclaw.backup.$(date +%Y%m%d)

# 解压到home目录
cd ~
tar xzf ~/Desktop/openclaw-migrate-full.tar.gz

# 验证
ls -la ~/.openclaw/openclaw.json
ls -la ~/.openclaw/workspace/SOUL.md
ls -la ~/.openclaw/workspace-edu/SOUL.md
```

## Step 4: 修改配置中的路径（关键！）

旧机器用户是 `rf`，Mac用户是 `win`，需要替换路径：

```bash
# 用sed替换 ~/.openclaw/openclaw.json 中的路径
cd ~/.openclaw
sed -i '' 's|/home/rf|/Users/win|g' openclaw.json

# 也处理agents目录下的session文件（历史记录，不改也行但不影响运行）
find agents/ -name "*.jsonl" -exec sed -i '' 's|/home/rf|/Users/win|g' {} +

# 处理exec-approvals.json
sed -i '' 's|/home/rf|/Users/win|g' exec-approvals.json 2>/dev/null

# 验证替换结果
grep -r "home/rf" ~/.openclaw/openclaw.json
# 应该返回空（无匹配）

grep -c "Users/win" ~/.openclaw/openclaw.json
# 应该 > 0
```

## Step 5: 处理FunASR环境（如果带了）

FunASR的Python虚拟环境是Linux x86_64编译的，**不能直接在Mac（ARM）上用**。需要重新创建：

```bash
# 删除Linux版本
rm -rf ~/.openclaw/funasr-env

# 在Mac上重新创建（需要python3 + venv）
python3 -m venv ~/.openclaw/funasr-env
source ~/.openclaw/funasr-env/bin/activate
pip install funasr modelscope torch torchaudio

# 测试
python3 -c "from funasr import AutoModel; print('OK')"
```

如果Mac是Apple Silicon（M系列），PyTorch会自动用MPS加速，比笔记本快很多。

## Step 6: 在Mac上启动OpenClaw

```bash
# 检查版本
openclaw --version
# 应该显示 OpenClaw 2026.4.15 或更新

# 启动gateway
openclaw gateway start

# 检查状态
openclaw gateway status
```

## Step 7: 验证

1. **飞书发消息给锋哥** — 应该能正常回复
2. **飞书群"小龙的卓越之路"** — @小园老师应该能响应
3. **检查agent绑定**：
```bash
openclaw agents list
# 应该显示 main + edu
```

## Step 8: 更新飞书回调（如果用公网）

如果飞书事件回调是通过frp转发到笔记本的，需要：
1. 在Mac上安装frpc并配置指向Mac
2. 或者改用Mac上的gateway端口
3. 飞书开发者后台改回调URL（如果域名/端口变了）

## 注意事项

| 项目 | 说明 |
|------|------|
| **FunASR模型缓存** | `~/.cache/modelscope/` 约2.1G，如果是同架构可直接拷贝，否则在新机器上首次运行会自动下载 |
| **Chrome profile** | 浏览器登录态在browser目录下，跨平台不一定能用，可能需要重新登录抖音 |
| **cron任务** | OpenClaw的cron是gateway内部管理的，会跟着配置走，不用重新设置 |
| **SSH密钥** | 笔记本上的 `~/.ssh/` 目录没打包（包含VPS私钥），需要单独拷贝 |
| **日志/历史** | agents下的session jsonl文件较大（历史对话），可以删掉节省空间 |
| **代理配置** | Mac上需要确保clash-verge或其他代理工具运行在 `127.0.0.1:7897` |

## 可选：清理旧机器

迁移验证成功后，在笔记本上：
```bash
# 停止旧机器的openclaw（避免两个实例同时连飞书）
openclaw gateway stop
# 删除打包文件
rm -f /tmp/openclaw-migrate*.tar.gz
```

## 故障排查

**Q: 飞书连不上？**
```bash
openclaw gateway status
# 检查飞书配置
cat ~/.openclaw/openclaw.json | grep -A5 "feishu"
```

**Q: 模型报错？**
```bash
# 检查模型provider配置
cat ~/.openclaw/openclaw.json | python3 -m json.tool | grep -A3 "zhipu"
# apiKey可能被sed误改了，检查一下
```

**Q: edu agent不响应？**
```bash
# 检查绑定
openclaw agents list
# 检查edu workspace路径是否正确
ls ~/.openclaw/workspace-edu/SOUL.md
```
