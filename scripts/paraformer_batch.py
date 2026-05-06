"""Paraformer-v2 录音文件识别 - 批量脚本"""
# -*- coding: utf-8 -*-
import os, sys, json, time, requests

os.environ["DASHSCOPE_API_KEY"] = "[DASHSCOPE_KEY_ENV]"

from dashscope.audio.asr import Transcription
from dashscope import Files

def transcribe_one(file_path):
    """单个文件转写: upload -> get_url -> submit -> wait -> parse json"""
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
    
    # 5. Download & parse transcription JSON
    results = result.output.get('results', [])
    if not results:
        return None, "no results"
    
    turl = results[0].get('transcription_url', '')
    if not turl:
        return None, "no transcription_url"
    
    try:
        resp = requests.get(turl, timeout=60)
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
        }, None
        
    except Exception as e:
        return None, f"parse error: {e}"


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python paraformer_batch.py <file1> [file2 ...]")
        sys.exit(1)
    
    files = sys.argv[1:]
    total = len(files)
    ok = 0
    fail = 0
    all_results = {}
    
    t0 = time.time()
    
    for i, f in enumerate(files, 1):
        if not os.path.exists(f):
            print(f"[{i}/{total}] NOT FOUND: {f}")
            fail += 1
            continue
        
        fname = os.path.basename(f)
        print(f"[{i}/{total}] {fname}", end=" ", flush=True)
        
        result, err = transcribe_one(f)
        if result:
            ok += 1
            all_results[fname] = result
            print(f"OK ({result['duration_min']}min, {len(result['text'])}chars)")
            # Print first 200 chars preview
            preview = result['text'][:200] + ("..." if len(result['text']) > 200 else "")
            print(f"  >> {preview}")
        else:
            fail += 1
            print(f"FAIL ({err})")
    
    elapsed = time.time() - t0
    
    print(f"\n{'='*60}")
    print(f"SUMMARY: ok={ok}, fail={fail}, total={total}, time={elapsed:.1f}s")
    
    # Save results
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "paraformer_results.json")
    with open(out_path, "w", encoding="utf-8") as fp:
        json.dump(all_results, fp, ensure_ascii=False, indent=2)
    print(f"Results saved: {out_path}")
