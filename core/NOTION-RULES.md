# Notion 配置与规则

> 2026-04-20 | 交由OpenClaw负责Notion操作，锋哥不再管

---

## API认证

| 项目 | 值 |
|------|-----|
| **Token** | `[NOTION_TOKEN_ENV]` |
| **API版本** | `2022-06-28`（⚠️ 必须用此版本，新版2025-09-03返回0个属性） |
| **Base URL** | `https://api.notion.com/v1` |

---

## 数据库ID

| 数据库 | ID | 用途 |
|--------|-----|------|
| 支出库（内联数据库） | `56ae3f43-3d0f-4673-95af-21b1ea96121d` | 记录所有支出 |
| 营业账户页面 | `6738db90-adb0-40d9-925a-0f964a2c9054` | 默认关联账户 |
| 个人账户页面 | `b473ec6a-a343-4089-8c26-ad6b943bb49b` | 个人消费 |

---

## 写入规则

### 记账
- **默认账户**：营业账户，除非明确说"个人消费"
- **收到就记**，秒级完成
- **调用方式**：POST `/v1/pages` 创建新行

### 字段映射

| Notion字段名 | 类型 | 说明 |
|-------------|------|------|
| 項目 | title | 项目名称 |
| 花费 | number | 金额 |
| 种类 | select | 分类（见下方选项） |
| 日期 | date | 消费日期 |
| 对应账户 | relation | 关联账户页面 |
| 花費理由 | rich_text | 备注说明 |

### 种类选项

食材 / 学习用品 / 日用 / 活动材料 / 教辅资料 / 办公材料 / 营销费用 / 水电房租 / 工资 / 个人消费 / 房租 / 餐饮

---

## API调用示例

### 创建支出记录

```python
import requests

NOTION_TOKEN = "[NOTION_TOKEN_ENV]"
NOTION_VERSION = "2022-06-28"
DATABASE_ID = "56ae3f43-3d0f-4673-95af-21b1ea96121d"
BUSINESS_ACCOUNT_ID = "6738db90-adb0-40d9-925a-0f964a2c9054"

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": NOTION_VERSION,
    "Content-Type": "application/json"
}

# 示例：记一笔食材支出
payload = {
    "parent": {"database_id": DATABASE_ID},
    "properties": {
        "項目": {"title": [{"text": {"content": "白菜萝卜排骨"}}]},
        "花费": {"number": 45.5},
        "种类": {"select": {"name": "食材"}},
        "日期": {"date": {"start": "2026-04-20"}},
        "对应账户": {"relation": [{"id": BUSINESS_ACCOUNT_ID}]},
        "花費理由": {"rich_text": [{"text": {"content": "午餐食材"}}]}
    }
}

response = requests.post("https://api.notion.com/v1/pages", headers=headers, json=payload)
```

---

## ⚠️ 已知坑

1. **必须用 Notion-Version: 2022-06-28**，新版API返回空属性
2. ~~个人账户页面未共享给集成~~（2026-04-21已修复，可正常关联）
3. **种类是select类型**，必须使用已存在的选项，不能随意写新的
4. **項目是title类型**，字段名是繁体"項目"不是简体"项目"

---

## OpenClaw职责

- 老板在飞书/微信说"XX花了XX元"→ OpenClaw自动记到Notion
- 默认营业账户，说"个人消费"才用个人账户
- 记完回复确认
