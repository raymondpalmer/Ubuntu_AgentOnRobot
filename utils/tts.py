
import asyncio
import base64
import os
import subprocess

import websockets
from dotenv import load_dotenv

load_dotenv()

TTS_WS_URL = os.getenv("TTS_WS_URL", "")
TTS_VOICE = os.getenv("TTS_VOICE", "default")
FALLBACK = os.getenv("VOICE_FALLBACK", "1") == "1"


async def _tts_via_ws(text: str) -> bytes:
    """连接云端 TTS，返回合成后的 PCM/WAV。具体协议以文档为准，这里给出常见流程示意。"""
    if not TTS_WS_URL:
        raise RuntimeError("TTS_WS_URL not set")

    async with websockets.connect(TTS_WS_URL, max_size=16*1024*1024) as ws:
        start = {"type": "start", "voice": TTS_VOICE, "format": "wav"}
        await ws.send(_json(start))
        await ws.send(_json({"type": "text", "data": text}))
        await ws.send(_json({"type": "end"}))

        audio = b""
        async for msg in ws:
            try:
                import json
                data = json.loads(msg)
                if "audio" in data:
                    audio += base64.b64decode(data["audio"])
                if data.get("final"):
                    break
            except Exception:
                pass
        return audio


def _json(obj) -> str:
    import json
    return json.dumps(obj, ensure_ascii=False)


def speak(text: str):
    """统一入口：优先云端，失败则降级到 espeak-ng"""
    if not text:
        return
    if FALLBACK or not TTS_WS_URL:
        try:
            subprocess.run(["espeak-ng", text], check=False)
        except FileNotFoundError:
            print(f"[TTS-Fallback] {text}")
        return

    try:
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        audio = loop.run_until_complete(_tts_via_ws(text))

        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(audio)
            path = f.name
        subprocess.run(["aplay", path], check=False)
    except Exception as e:
        print(f"[TTS] 云端失败，降级 espeak-ng：{e}")
        try:
            subprocess.run(["espeak-ng", text], check=False)
        except FileNotFoundError:
            print(f"[TTS-Fallback] {text}")
