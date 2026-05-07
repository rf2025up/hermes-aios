#!/usr/bin/env python3
"""测试更多DashScope ASR模型"""
import os, json, sys

# 提取新key
with open("/root/.hermes/auth.json") as f:
    data = json.load(f)
new_key = None
for e in data.get("credential_pool", {}).get("custom:bailian", []):
    if e.get("label", "") == "bailian-backup-202605":
        new_key = e.get("access_token", "")
        break
if not new_key:
    print("ERROR: key not found"); sys.exit(1)

os.environ["DASHSCOPE_API_KEY"] = new_key
from dashscope.audio.asr import Transcription
from dashscope import Files

# 排除TTS模型
ALL_MODELS = [
    "sambert-zhinan-v1",
    "qwen3-asr-flash-realtime-2026-02-10",
    "qwen3-asr-flash-2026-02-10",
    "sambert-zhide-v1",
    "sambert-zhida-v1",
    "sambert-zhishu-v1",
    "sambert-zhiyue-v1",
    "sambert-eva-v1",
    "paraformer-realtime-8k-v2",
    "sambert-beth-v1",
    "sambert-zhiye-v1",
    "sambert-zhiya-v1",
    "sambert-indah-v1",
    "sambert-zhiying-v1",
    "qwen3-asr-flash",
]

# 排除TTS
TTS_NAMES = ["tts", "instruct"]
MODELS = [m for m in ALL_MODELS if not any(t in m for t in TTS_NAMES)]

test_file = "/mnt/h/抖音直播录制/托管老司机_AmazingGrace02_音频/托管老司机_2026-03-01_23-27-21.m4a"

print(f"使用key: sk-...{new_key[-6:]}")
print(f"测试 {len(MODELS)} 个模型\n")

# 上传一次
print("上传测试文件...")
resp = Files.upload(file_path=test_file, purpose="file-extract")
if resp.status_code != 200:
    print(f"上传失败: {resp.status_code}"); sys.exit(1)
file_id = resp.output.get("uploaded_files", [{}])[0].get("file_id", "")
info = Files.get(file_id=file_id)
file_url = info.output.get("url", "")
print(f"上传成功, URL已获取\n")

ok, warn, fail = [], [], []
for model in MODELS:
    print(f"--- {model} ---", end=" ", flush=True)
    try:
        task = Transcription.call(model=model, file_urls=[file_url])
        if task.status_code != 200:
            err = getattr(task, 'message', str(task.status_code))
            print(f"❌ 提交失败: {err[:80]}")
            fail.append(model)
            continue

        result = Transcription.wait(task=task)
        status = result.output.get("task_status", "")
        msg = result.output.get("message", "")

        if status == "SUCCEEDED":
            print("✅ 成功")
            ok.append(model)
        elif "URL" in str(msg) or "url" in str(msg):
            print(f"❌ URL不兼容: {msg[:60]}")
            fail.append(model)
        else:
            print(f"⚠️ {status}: {msg[:60]}")
            warn.append(model)
    except Exception as e:
        print(f"❌ {str(e)[:80]}")
        fail.append(model)

print(f"\n{'='*50}")
print(f"✅ 可用 ({len(ok)}): {', '.join(ok)}")
print(f"⚠️ 异常 ({len(warn)}): {', '.join(warn)}")
print(f"❌ 不可用 ({len(fail)}): {', '.join(fail)}")
