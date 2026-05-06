#!/usr/bin/env python3
"""批量Paraformer转写脚本 v2 - 带音频预处理和分片"""
import os, sys, time, traceback, subprocess, tempfile, glob
from datetime import datetime

AUDIO_DIR = "/mnt/h/抖音直播录制/朋阳近期直播25年10月_音频/"
MD_DIR = "/mnt/h/抖音直播录制/朋阳近期直播25年10月/_文案/"
LOG_FILE = "/root/workspace/aios/core/daily/transcription_batch.log"
TEMP_DIR = "/tmp/transcribe_temp/"

os.makedirs(MD_DIR, exist_ok=True)
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def get_transcribed_names():
    names = set()
    if os.path.isdir(MD_DIR):
        for f in os.listdir(MD_DIR):
            if f.endswith(".md") and not f.endswith("_结构化.md"):
                name = f.replace(".md", "")
                if name.endswith("_full"):
                    name = name[:-5]
                names.add(name)
    return names

def get_audio_files():
    audios = {}
    for f in os.listdir(AUDIO_DIR):
        if f.endswith(".m4a"):
            base = os.path.splitext(f)[0]
            key = base[:-5] if base.endswith("_full") else base
            size = os.path.getsize(os.path.join(AUDIO_DIR, f))
            if key not in audios or size > audios[key][1]:
                audios[key] = (f, size)
    return audios

def preprocess_audio(input_path, output_path):
    """ffmpeg: m4a → 16kHz mono wav"""
    cmd = [
        "ffmpeg", "-y", "-i", input_path,
        "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le",
        output_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {result.stderr[:200]}")
    return os.path.getsize(output_path)

def transcribe_chunked(model, wav_path, chunk_s=600):
    """分片转写大音频文件"""
    # 获取时长
    probe = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "csv=p=0", wav_path],
        capture_output=True, text=True, timeout=30
    )
    duration = float(probe.stdout.strip()) if probe.stdout.strip() else 0
    
    if duration <= 0:
        return model.generate(input=wav_path, batch_size_s=300)
    
    # 分片
    texts = []
    start = 0
    while start < duration:
        end = min(start + chunk_s, duration)
        chunk_path = os.path.join(TEMP_DIR, f"chunk_{int(start)}_{int(end)}.wav")
        
        cmd = [
            "ffmpeg", "-y", "-i", wav_path,
            "-ss", str(start), "-t", str(end - start),
            "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le",
            chunk_path
        ]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if r.returncode != 0:
            log(f"  chunk ffmpeg error: {r.stderr[:100]}")
            start = end
            continue
        
        try:
            res = model.generate(input=chunk_path, batch_size_s=300)
            if res and len(res) > 0:
                if isinstance(res[0], dict):
                    t = res[0].get("text", "")
                else:
                    t = str(res[0])
                if t:
                    texts.append(t)
        except Exception as e:
            log(f"  chunk transcribe error at {start}-{end}s: {e}")
        
        # 清理
        try:
            os.remove(chunk_path)
        except:
            pass
        
        start = end
    
    if texts:
        full_text = "\n".join(texts)
        return [{"text": full_text}]
    return []

def main():
    log("=" * 60)
    log("批量转写v2启动 (带音频预处理+分片)")
    log("=" * 60)

    from funasr import AutoModel
    log("加载Paraformer模型...")
    model = AutoModel(model='paraformer-zh', model_revision='v2.0.4', device='cpu')
    log("模型加载完成")

    transcribed = get_transcribed_names()
    audios = get_audio_files()
    todo = {k: v for k, v in audios.items() if k not in transcribed}

    log(f"总音频: {len(audios)}, 已转写: {len(transcribed)}, 待转写: {len(todo)}")
    log(f"待转写总大小: {sum(v[1] for v in todo.values())/1024/1024:.0f}MB")

    success = 0
    failed = 0
    skipped = 0
    total_start = time.time()

    for i, (name, (filename, size)) in enumerate(sorted(todo.items()), 1):
        md_path = os.path.join(MD_DIR, f"{name}.md")
        audio_path = os.path.join(AUDIO_DIR, filename)

        if size < 100 * 1024:
            log(f"[{i}/{len(todo)}] SKIP {name} (文件太小: {size/1024:.0f}KB)")
            skipped += 1
            continue

        log(f"[{i}/{len(todo)}] 开始: {name} ({size/1024/1024:.1f}MB)")
        start = time.time()

        try:
            # Step 1: 预处理为16kHz mono wav
            wav_path = os.path.join(TEMP_DIR, f"{name}.wav")
            log(f"  ffmpeg预处理...")
            wav_size = preprocess_audio(audio_path, wav_path)
            log(f"  预处理完成: {wav_size/1024/1024:.1f}MB wav")

            # Step 2: 分片转写（>10分钟的音频分片处理）
            probe = subprocess.run(
                ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
                 "-of", "csv=p=0", wav_path],
                capture_output=True, text=True, timeout=30
            )
            duration = float(probe.stdout.strip()) if probe.stdout.strip() else 0
            
            if duration > 600:  # >10分钟
                log(f"  音频{duration/60:.0f}分钟，启用分片模式")
                res = transcribe_chunked(model, wav_path, chunk_s=600)
            else:
                res = model.generate(input=wav_path, batch_size_s=300)

            elapsed = time.time() - start
            os.remove(wav_path)

            if res and len(res) > 0:
                text = ""
                if isinstance(res[0], dict):
                    text = res[0].get("text", "")
                elif isinstance(res[0], str):
                    text = res[0]
                else:
                    text = str(res[0])

                if text and len(text.strip()) > 10:
                    with open(md_path, "w", encoding="utf-8") as f:
                        f.write(f"# {name}\n\n")
                        f.write(f"> 转写时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
                        f.write(f"> 音频文件: {filename}\n")
                        f.write(f"> 文件大小: {size/1024/1024:.1f}MB\n")
                        f.write(f"> 音频时长: {duration/60:.1f}分钟\n")
                        f.write(f"> 转写耗时: {elapsed:.0f}秒\n\n")
                        f.write("---\n\n")
                        f.write(text)
                    success += 1
                    log(f"[{i}/{len(todo)}] ✅ {name} ({elapsed:.0f}s, {len(text)}字)")
                else:
                    failed += 1
                    log(f"[{i}/{len(todo)}] ⚠️ 转写为空: {name}")
            else:
                failed += 1
                log(f"[{i}/{len(todo)}] ⚠️ 无结果: {name}")

        except Exception as e:
            failed += 1
            log(f"[{i}/{len(todo)}] ❌ {name}: {e}")
            traceback.print_exc()
            # 清理临时文件
            for p in glob.glob(os.path.join(TEMP_DIR, f"{name}*")):
                try:
                    os.remove(p)
                except:
                    pass

    total_elapsed = time.time() - total_start
    log("=" * 60)
    log(f"批量转写完成! 成功: {success}, 失败: {failed}, 跳过: {skipped}")
    log(f"总耗时: {total_elapsed/3600:.1f}小时")
    log(f"日志: {LOG_FILE}")
    log("=" * 60)

if __name__ == "__main__":
    main()
