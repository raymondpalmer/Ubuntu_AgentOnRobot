
import asyncio
import base64
import os
import time
from dataclasses import dataclass

import sounddevice as sd
import websockets
from dotenv import load_dotenv

load_dotenv()

ASR_WS_URL = os.getenv("ASR_WS_URL", "")
FALLBACK = os.getenv("VOICE_FALLBACK", "1") == "1"
SAMPLE_RATE = int(os.getenv("SAMPLE_RATE", "16000"))
RECORD_SECONDS = int(os.getenv("RECORD_SECONDS", "5"))


@dataclass
class ASRResult:
    text: str
    latency_ms: float


def record_pcm(seconds: int = RECORD_SECONDS, samplerate: int = SAMPLE_RATE) -> bytes:
    """Record mono PCM 16 kHz 16-bit and return raw bytes."""
    print(f"[ASR] Recording {seconds}s @ {samplerate} Hz ...")
    audio = sd.rec(int(seconds * samplerate), samplerate=samplerate, channels=1, dtype="int16")
    sd.wait()
    return audio.tobytes()


async def asr_via_ws(pcm_bytes: bytes) -> str:
    """Generic WS sender: base64 PCM frames -> incremental results.
    NOTE: 具体协议字段请根据豆包 ASR 文档调整，这里仅给出常见结构示意。
    """
    if not ASR_WS_URL:
        raise RuntimeError("ASR_WS_URL not set")

    async with websockets.connect(ASR_WS_URL, max_size=16*1024*1024) as ws:
        # 1) 发送开始帧（根据实际协议调整）
        start_payload = {"type": "start", "format": "pcm16", "sample_rate": 16000}
        await ws.send(to_json(start_payload))

        # 2) 发送音频分片（简单一次性，也可分片循环发送）
        frame_payload = {"type": "audio", "data": base64.b64encode(pcm_bytes).decode()}
        await ws.send(to_json(frame_payload))

        # 3) 发送结束帧
        await ws.send(to_json({"type": "end"}))

        # 4) 等待最终识别
        text = ""
        async for msg in ws:
            try:
                import json
                data = json.loads(msg)
                if "final" in data:
                    text = data.get("final", "")
                    break
                if "result" in data:
                    text = data.get("result", "")
            except Exception:
                pass
        return text.strip()


def to_json(obj) -> str:
    import json
    return json.dumps(obj, ensure_ascii=False)


def transcribe_once() -> ASRResult:
    """统一入口：优先云端，失败则降级为手动输入"""
    t0 = time.time()
    if FALLBACK or not ASR_WS_URL:
        text = input("[ASR-Fallback] 请输入你的话（模拟识别）> ").strip()
        return ASRResult(text=text, latency_ms=(time.time() - t0) * 1000)

    # 录音 + WS 发送
    pcm = record_pcm()
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    try:
        text = loop.run_until_complete(asr_via_ws(pcm))
    except Exception as e:
        print(f"[ASR] WS 调用失败，降级为手动输入：{e}")
        text = input("[ASR-Fallback] 请输入你的话> ").strip()

    return ASRResult(text=text, latency_ms=(time.time() - t0) * 1000)
