#!/usr/bin/env python3
"""批量生成朋阳AI知识卡片 — 基于knowledge-production工作流"""
import json, glob, os, sys, time, requests, re
from pathlib import Path

# 配置
RESULTS_FILE = '/root/workspace/aios/scripts/transcription_results/paraformer_results_v2.json'
OUTPUT_DIR = '/mnt/h/抖音直播录制/Hermes/朋阳'
PROGRESS_FILE = '/root/workspace/aios/scripts/knowledge_cards_progress.json'
API_BASE = 'https://open.bigmodel.cn/api/coding/paas/v4'
API_KEY = '1146ff2f5e784c6f944d43caaa6e534d.HMEbFg2wmYpl12UW'
MODEL = 'glm-5-turbo'
MAX_TOKENS = 16000
TIMEOUT = 300

# 加载转写数据
with open(RESULTS_FILE, encoding='utf-8') as f:
    transcriptions = json.load(f)

# 加载进度
if os.path.exists(PROGRESS_FILE):
    with open(PROGRESS_FILE, encoding='utf-8') as f:
        progress = json.load(f)
else:
    progress = {'completed': {}, 'failed': {}, 'total': 0}

# 已结构化的文件
structured = glob.glob(os.path.join(OUTPUT_DIR, '*_结构化.md'))
struct_basenames = {os.path.basename(s).replace('_结构化.md','') for s in structured}

# 朋阳m4a去重
pengyang_m4a = glob.glob('/mnt/h/抖音直播录制/朋阳近期直播25年10月_音频/**/*.m4a', recursive=True)
pengyang_fnames = {os.path.basename(f) for f in pengyang_m4a}

# 去掉_full重复
unique_fnames = set()
for fn in pengyang_fnames:
    if '_full' in fn:
        base = fn.replace('_full', '')
        if base not in pengyang_fnames:
            unique_fnames.add(fn)
    else:
        unique_fnames.add(fn)

# 构建待处理列表
todo = []
for fn in sorted(unique_fnames):
    fn_base = fn.replace('.m4a', '')
    # 检查已结构化
    matched = any(sb in fn_base or fn_base in sb for sb in struct_basenames)
    if matched:
        continue
    # 检查进度
    if fn in progress['completed']:
        continue
    # 检查转写文本
    if fn not in transcriptions:
        continue
    text = transcriptions[fn].get('text', '')
    if len(text) < 200:
        continue
    todo.append((fn, text))

print(f'待处理: {len(todo)} 个文件')
print(f'已完成(进度文件): {len(progress["completed"])} 个')
print(f'已有结构化md: {len(struct_basenames)} 个')

if not todo:
    print('没有待处理文件!')
    sys.exit(0)

PROMPT_TEMPLATE = """你是托管行业知识沉淀专家。请对以下直播转写稿进行去噪清洗、核心观点提炼和结构化整理。

要求：
1. 去噪：去掉直播互动（打招呼/要关注/点赞）、营销催单、口水话、重复内容
2. 保留：核心观点、方法论、工作流程、判断标准、数据案例、话术模板
3. 不要编造原文没有的内容，不确定的标注【待复核】
4. 按以下模板输出完整结构化文档：

# {title}

## 0. 文档元信息
- 来源：朋阳直播
- 讲师：朋阳
- 时间：（从内容推断）
- 内容类型：（招生策略/交付管理/教师管理/产品设计/团队组织/校长经营）
- 适用对象：托管机构校长/老师
- 适用场景：
- 核心问题：
- 关键词：
- 知识状态：初稿

## 1. AI 速读卡
### 这篇内容解决什么问题？
### 什么时候应该引用这篇？
### 不适合用于什么问题？
### 一句话结论

## 2. 核心结论
（5-10条判断句）

## 3. 知识地图
（4-8个知识模块）

## 4. 模块详解
每个模块含：解决的问题/核心观点/操作方法/判断标准/常见错误/可复用内容

## 5. 可执行工具
### SOP
### 检查表
### 话术模板

## 6. AI 使用说明
### 可回答的问题
### 不应过度推断的内容

## 7. AI 知识卡片（3-5张）
每张卡片格式：
### 卡片：标题
- 所属系统：（招生增长/托管交付/教师管理/产品项目/团队组织/校长经营）
- 所属年度节点：（几月什么节点）
- 解决的问题：
- 核心结论：
- 操作步骤：
- 判断标准：
- 常见错误：
- AI调用场景：
- 使用边界：

---
以下是转写稿原文：
"""

os.makedirs(OUTPUT_DIR, exist_ok=True)

success = 0
failed = 0
total = len(todo)

for i, (fn, text) in enumerate(todo):
    title = fn.replace('.m4a', '').replace('_full', '')
    print(f'\n[{i+1}/{total}] {title} ({len(text)}字)...', flush=True)

    prompt = PROMPT_TEMPLATE.format(title=title)
    user_msg = prompt + text

    try:
        t0 = time.time()
        resp = requests.post(
            f'{API_BASE}/chat/completions',
            headers={
                'Authorization': f'Bearer {API_KEY}',
                'Content-Type': 'application/json'
            },
            json={
                'model': MODEL,
                'messages': [{'role': 'user', 'content': user_msg}],
                'max_tokens': MAX_TOKENS,
                'temperature': 0.3
            },
            timeout=TIMEOUT
        )
        elapsed = time.time() - t0

        if resp.status_code != 200:
            err_text = resp.text[:300]
            print(f'  ❌ API错误 {resp.status_code}: {err_text}')
            # GLM Coding Plan 限流（1113/429）→ 保存进度，等明晚继续
            if resp.status_code in (429, 400) and ('1113' in err_text or 'rate' in err_text.lower() or 'limit' in err_text.lower() or '资源包' in err_text):
                print('  ⚠️ GLM限流，保存进度，等明晚继续')
                with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
                    json.dump(progress, f, ensure_ascii=False, indent=2)
                break
            progress['failed'][fn] = f'API {resp.status_code}: {err_text[:100]}'
            failed += 1
            continue

        result = resp.json()
        content = result['choices'][0]['message']['content']

        # 保存
        out_name = f'{title}_结构化.md'
        out_path = os.path.join(OUTPUT_DIR, out_name)
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(content)

        # 同步到H盘
        win_path = os.path.join('/mnt/h/Hermes/朋阳', out_name)
        os.makedirs(os.path.dirname(win_path), exist_ok=True)
        with open(win_path, 'w', encoding='utf-8') as f:
            f.write(content)

        progress['completed'][fn] = {
            'output': out_name,
            'size': len(content),
            'api_time': round(elapsed, 1),
            'timestamp': time.strftime('%Y-%m-%d %H:%M')
        }
        success += 1
        print(f'  ✅ {len(content)}字, {elapsed:.0f}s')

        # 每5个保存一次进度
        if (i + 1) % 5 == 0:
            with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
                json.dump(progress, f, ensure_ascii=False, indent=2)
            print(f'  [进度已保存: {success}/{total}]')

    except requests.exceptions.Timeout:
        print(f'  ❌ 超时({TIMEOUT}s)')
        progress['failed'][fn] = 'timeout'
        failed += 1
    except Exception as e:
        print(f'  ❌ 异常: {e}')
        progress['failed'][fn] = str(e)[:100]
        failed += 1

# 最终保存进度
progress['total'] = len(progress['completed']) + len(progress['failed'])
with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
    json.dump(progress, f, ensure_ascii=False, indent=2)

print(f'\n===== 完成 =====')
print(f'成功: {success}')
print(f'失败: {failed}')
print(f'总进度文件: {PROGRESS_FILE}')
