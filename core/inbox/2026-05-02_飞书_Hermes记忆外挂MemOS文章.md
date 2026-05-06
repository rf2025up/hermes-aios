# 给Hermes装记忆外挂（MemOS）— 知乎文章存档

> **来源**：锋哥飞书发送（知乎链接）
> **日期**：2026-05-02
> **原文链接**：https://zhuanlan.zhihu.com/p/2030666840830128388
> **作者**：逛逛GitHub
> **发布时间**：2026-04-23

## 核心内容

文章介绍了MemTensor团队为Hermes Agent开发的MemOS本地记忆插件（memos-local-plugin），解决Hermes的记忆管理问题。

## 关键能力

1. **记忆去重**：自动识别重复/更新/新内容，用LLM判断而非简单文本比对
2. **混合检索**：全文搜索 + 向量语义搜索，解决关键词搜不到的问题
3. **多模型配置**：Embedding/摘要/技能生成可独立配置不同模型
4. **多Agent协同**：同机器共享公共记忆，跨机器用Hub-Client架构
5. **Web管理面板**：7个管理页面，密码保护，本地访问（端口18799）

## 三个项目关系

- usememos/memos：开源备忘录工具（存储后端）
- MemTensor/MemOS：AI记忆操作系统（管理大脑）
- MemOS/memos-local-plugin：为OpenClaw写的桥接插件（已安装在锋哥机器上）

## 完整原文

本地文件：C:\Users\Administrator\zhihu_article.txt（7764字节）
