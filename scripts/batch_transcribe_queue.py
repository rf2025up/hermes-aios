"""批量Paraformer转写 - 后台队列版
用法: python3 batch_transcribe_queue.py
从 pending_transcription.txt 读取文件列表，逐个转写，保存原始md到 _文案 目录
"""
import os, sys, json, time, requests

os.environ["DASHSCOPE_API_KEY"] = "[DASHSCOPE_KEY_ENV]"

from dashscope.audio.asr import Transcription
from dashscope import Files

AUDIO_DIR = "/mnt/h/抖音直播录制/朋阳近期直播25年10月_音频/"
MD_DIR = "/mnt/h/抖音直播录制/朋阳近期直播25年10月/_文案/"
LOG_FILE = "/root/workspace/aios/scripts/transcription_log.json"
LIST_FILE = "/root/workspace/aios/scripts/pending_transcription.txt"
DONE_FILE = "/root/workspace/aios/scripts/done_transcription.txt"

def load_done():
    if os.path.exists(DONE_FILE):
        with open(DONE_FILE) as f:
            return set(line.strip() for line in f if line.strip())
    return set()

def save_done(done_set):
    with open(DONE_FILE, "w") as f:
        for path in sorted(done_set):
            f.write(path + "\n")

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
        }, None
        
    except Exception as e:
        return None, f"parse error: {e}"

def save_md(file_path, result):
    """保存转写结果为md文件"""
    fname = os.path.splitext(os.path.basename(file_path))[0]
    # 去掉 _full 后缀
    if fname.endswith("_full"):
        fname = fname[:-5]
    md_path = os.path.join(MD_DIR, f"{fname}.md")
    
    content = f"# {fname}\n\n"
    content += f"- 音频源: {os.path.basename(file_path)}\n"
    content += f"- 时长: {int(result['duration_min']//60)}小时{int(result['duration_min']%60)}分{result['duration_ms']%60000//1000}秒\n"
    content += f"- 字数: {len(result['text'])}\n"
    content += f"\n---\n\n"
    content += result['text']
    
    with open(md_path, "w", encoding="utf-8") as fp:
        fp.write(content)
    
    return md_path

if __name__ == "__main__":
    # 读取待转写列表
    with open(LIST_FILE) as f:
        all_files = [line.strip() for line in f if line.strip()]
    
    done = load_done()
    pending = [f for f in all_files if f not in done]
    
    print(f"总计: {len(all_files)}, 已完成: {len(done)}, 待处理: {len(pending)}")
    sys.stdout.flush()
    
    if not pending:
        print("全部完成!")
        sys.exit(0)
    
    os.makedirs(MD_DIR, exist_ok=True)
    
    t0 = time.time()
    ok_count = 0
    fail_count = 0
    
    for i, fpath in enumerate(pending, 1):
        if not os.path.exists(fpath):
            print(f"[{i}/{len(pending)}] NOT FOUND: {fpath}")
            fail_count += 1
            continue
        
        fname = os.path.basename(fpath)
        print(f"[{i}/{len(pending)}] {fname}", end=" ", flush=True)
        
        result, err = transcribe_one(fpath)
        if result:
            md_path = save_md(fpath, result)
            ok_count += 1
            done.add(fpath)
            print(f"OK ({result['duration_min']}min, {len(result['text'])}chars) -> {os.path.basename(md_path)}")
            # 每5个保存一次进度
            if ok_count % 5 == 0:
                save_done(done)
        else:
            fail_count += 1
            print(f"FAIL ({err})")
            # 失败也记录，避免重复尝试
            done.add(fpath)
            save_done(done)
        
        sys.stdout.flush()
    
    save_done(done)
    elapsed = time.time() - t0
    
    print(f"\n{'='*60}")
    print(f"BATCH COMPLETE: ok={ok_count}, fail={fail_count}, total={len(pending)}, time={elapsed/60:.1f}min")
