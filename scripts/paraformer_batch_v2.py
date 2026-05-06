#!/usr/bin/env python3
"""Paraformer-v2 批量转写 - 健壮版（逐个保存，断点续传）
用法: python3 paraformer_batch_v2.py [directory]
自动扫描目录下所有m4a文件，跳过已完成的，每个结果立即保存。
"""
import os, sys, json, time, requests, glob

API_KEY = os.environ.get("DASHSCOPE_API_KEY", "sk-61ad5e6681a3414b8e660eaeaad1f957")
os.environ["DASHSCOPE_API_KEY"] = API_KEY

from dashscope.audio.asr import Transcription
from dashscope import Files

RESULTS_DIR = "/root/workspace/aios/scripts/transcription_results"
RESULTS_FILE = os.path.join(RESULTS_DIR, "paraformer_results_v2.json")

os.makedirs(RESULTS_DIR, exist_ok=True)

def load_results():
    """加载已有结果"""
    if os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_results(results):
    """保存结果到文件"""
    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

def transcribe_one(file_path):
    """单个文件转写"""
    fname = os.path.basename(file_path)
    fsize_mb = os.path.getsize(file_path) / 1024 / 1024
    
    # 1. Upload
    upload_resp = Files.upload(file_path=file_path, purpose='file-extract')
    if upload_resp.status_code != 200:
        return None, f"upload fail: {upload_resp.status_code}"
    file_id = upload_resp.output.get('uploaded_files', [{}])[0].get('file_id', '')
    if not file_id:
        return None, "no file_id"
    
    # 2. Get URL
    file_info = Files.get(file_id=file_id)
    file_url = file_info.output.get('url', '')
    if not file_url:
        return None, "no url"
    
    # 3. Submit
    task = Transcription.call(model='paraformer-v2', file_urls=[file_url])
    if task.status_code != 200:
        return None, f"submit fail: {task.status_code}"
    
    # 4. Wait
    result = Transcription.wait(task=task)
    if result.status_code != 200:
        return None, f"wait fail: {result.status_code}"
    
    status = result.output.get('task_status', '')
    if status != 'SUCCEEDED':
        msg = result.output.get('message', 'unknown')
        return None, f"task {status}: {msg}"
    
    # 5. Download & parse
    results = result.output.get('results', [])
    if not results:
        return None, "no results"
    
    turl = results[0].get('transcription_url', '')
    if not turl:
        return None, "no transcription_url"
    
    resp = requests.get(turl, timeout=120)
    if resp.status_code != 200:
        return None, f"download fail: {resp.status_code}"
    
    data = json.loads(resp.text)
    transcripts = data.get('transcripts', [])
    if not transcripts:
        return None, "no transcripts"
    
    text = transcripts[0].get('text', '')
    duration_ms = transcripts[0].get('content_duration_in_milliseconds', 0)
    
    return {
        'text': text,
        'duration_ms': duration_ms,
        'duration_min': round(duration_ms / 60000, 1),
        'file_size_mb': round(fsize_mb, 2),
        'char_count': len(text),
    }, None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        # 默认扫描朋阳目录
        directory = "/mnt/h/抖音直播录制/"
    else:
        directory = sys.argv[1]
    
    # 扫描所有m4a文件
    files = sorted(glob.glob(os.path.join(directory, "**/*.m4a"), recursive=True))
    if not files:
        print(f"ERROR: No .m4a files found in {directory}")
        sys.exit(1)
    
    print(f"Found {len(files)} m4a files in {directory}")
    
    # 加载已有结果
    results = load_results()
    done = set(results.keys())
    print(f"Already completed: {len(done)}")
    remaining = [f for f in files if os.path.basename(f) not in done]
    print(f"Remaining: {len(remaining)}")
    
    if not remaining:
        print("All files already transcribed!")
        sys.exit(0)
    
    # 逐个处理
    total = len(remaining)
    for i, f in enumerate(remaining, 1):
        fname = os.path.basename(f)
        t0 = time.time()
        print(f"[{i}/{total}] Starting: {fname} ({os.path.getsize(f)/1024/1024:.1f}MB)", flush=True)
        
        result, err = transcribe_one(f)
        elapsed = time.time() - t0
        
        if result:
            results[fname] = result
            save_results(results)  # 立即保存！
            print(f"  ✅ OK ({result['duration_min']}min, {result['char_count']}chars, {elapsed:.0f}s)", flush=True)
            # 同时保存单独的txt文件
            txt_path = os.path.join(RESULTS_DIR, f"{os.path.splitext(fname)[0]}.txt")
            with open(txt_path, "w", encoding="utf-8") as tf:
                tf.write(result['text'])
        else:
            print(f"  ❌ FAIL ({err}, {elapsed:.0f}s)", flush=True)
            # 不保存失败的结果
    
    # 最终统计
    print(f"\n{'='*60}")
    print(f"SUMMARY: total_files={len(files)}, completed={len(results)}, remaining={len(files)-len(results)}")
    print(f"Results: {RESULTS_FILE}")
