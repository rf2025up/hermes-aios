#!/usr/bin/env python3
"""测试DashScope ASR模型（使用新key）"""
import os, json, sys

# 从auth.json提取新key
with open("/root/.hermes/auth.json") as f:
    data = json.load(f)
new_key = None
for e in data.get("credential_pool", {}).get("custom:bailian", []):
    if e.get("label", "") == "bailian-backup-202605":
        new_key = e.get("access_token", "")
        break

if not new_key:
    print("ERROR: 新key未找到")
    sys.exit(1)

os.environ["DASHSCOPE_API_KEY"] = new_key
print(f"使用key: sk-...{new_key[-6:]}")

from dashscope.audio.asr import Transcription
from dashscope import Files

ASR_MODELS = [
    "paraformer-v2",
    "paraformer-v1",
    "paraformer-realtime-v2",
    "fun-asr-2025-11-07",
    "fun-asr-realtime-2025-09-15",
]

test_file = "/mnt/h/抖音直播录制/托管老司机_AmazingGrace02_音频/托管老司机_2026-03-01_23-27-21.m4a"

print("上传测试文件...")
resp = Files.upload(file_path=test_file, purpose="file-extract")
if resp.status_code != 200:
    print(f"上传失败: {resp.status_code} {getattr(resp, 'message', '')}")
    sys.exit(1)
file_id = resp.output.get("uploaded_files", [{}])[0].get("file_id", "")
print(f"上传成功: {file_id}")

info = Files.get(file_id=file_id)
file_url = info.output.get("url", "")
print(f"获取URL成功\n")

results = {}
for model in ASR_MODELS:
    print(f"--- 测试 {model} ---")
    try:
        task = Transcription.call(model=model, file_urls=[file_url])
        print(f"  提交: {task.status_code} {getattr(task, 'message', '')}")

        if task.status_code == 200:
            result = Transcription.wait(task=task)
            status = result.output.get("task_status", "")
            msg = result.output.get("message", "")
            if status == "SUCCEEDED":
                print(f"  结果: ✅ 成功")
                results[model] = "OK"
            else:
                print(f"  结果: ⚠️ {status} - {msg}")
                results[model] = f"WARN:{status}"
        else:
            err = getattr(task, 'message', '') or str(task.status_code)
            print(f"  结果: ❌ {err}")
            results[model] = "FAIL"
    except Exception as e:
        print(f"  结果: ❌ {e}")
        results[model] = "FAIL"
    print()

print("=" * 50)
print("模型排序建议（优先可用的）:")
ok_models = [m for m in ASR_MODELS if results.get(m) == "OK"]
warn_models = [m for m in ASR_MODELS if results.get(m, "").startswith("WARN")]
fail_models = [m for m in ASR_MODELS if results.get(m) == "FAIL"]
for m in ok_models:
    print(f"  ✅ {m}")
for m in warn_models:
    print(f"  ⚠️  {m}: {results[m]}")
for m in fail_models:
    print(f"  ❌ {m}")
