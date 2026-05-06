# Hermes Git仓库备份配置

> 创建时间：2026-05-06
> 用途：备份整个 `/root/workspace/aios/` 目录到GitHub

---

## 配置信息

| 项目 | 内容 |
|------|------|
| 备份目录 | `/root/workspace/aios/` |
| 备份范围 | 整个目录（core/、scripts/、daily/、inbox/、backups/等全部子目录） |
| 同步频率 | 待定（建议每日自动推送或关键变更后手动推送） |
| GitHub Token | `[已存储到WSL环境变量，不写入文件]` |

## Git配置命令

```bash
# 设置用户名和邮箱（如未配置）
git config --global user.name "rf2025up"
git config --global user.email "（待补充邮箱）"

# 添加远程仓库（如未添加）
cd /root/workspace/aios
git remote add origin https://rf2025up:[GITHUB_TOKEN_ENV]@github.com/rf2025up/hermes-aios.git

# 首次推送
git add .
git commit -m "init: Hermes AIOS full backup"
git branch -M main
git push -u origin main

# 后续推送
git add .
git commit -m "daily: 2026-05-06 update"
git push
```

## .gitignore建议

```gitignore
# 敏感信息
.env
*.env
*secret*

# 临时文件
__pycache__/
*.pyc
.cache/

# 系统文件
.DS_Store
Thumbs.db

# 大型缓存
/hermes-agent/
```

## 注意事项

1. Token已保存在MEMORY.md和本文档中
2. 首次推送需要先创建GitHub仓库 `hermes-aios`
3. 建议设置cron定时自动推送（每日一次）
9. 飞书云文档不同步到Git，只同步本地md文件
