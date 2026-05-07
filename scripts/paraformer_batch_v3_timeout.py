#!/usr/bin/env python3
"""Wrapper that adds timeout to paraformer_batch_v3.py Transcription.wait()""

import threading
import sys
import os

_orig_wait = None

def wait_with_timeout(cls, task, api_key=None, workspace=None, timeout=600, **kwargs):
    result = [None]
    exception = [None]
    def worker():
        try:
            result[0] = _orig_wait(task, api_key=api_key, workspace=workspace, **kwargs)
        except Exception as e:
            exception[0] = e
    t = threading.Thread(target=worker, daemon=True)
    t.start()
    t.join(timeout=timeout)
    if t.is_alive():
        from dashscope.api_entities.dashscope_response import TranscriptionResponse
        print(f"    WARNING Transcription.wait() timed out after {timeout}s", flush=True)
        fake = type("obj", (), {
            "status_code": 408,
            "output": {"task_status": "FAILED", "message": f"Timeout after {timeout}s"},
            "message": f"Timeout after {timeout}s",
            "code": "Timeout",
        })()
        return TranscriptionResponse.from_api_response(fake)
    if exception[0]:
        raise exception[0]
    return result[0]

from dashscope.audio.asr import Transcription
_orig_wait = Transcription.wait
Transcription.wait = classmethod(wait_with_timeout)
print("[timeout-patch] Transcription.wait() patched with 600s timeout", flush=True)

exec(open("/root/workspace/aios/scripts/paraformer_batch_v3.py").read())
