
from utils.asr import transcribe_once

if __name__ == "__main__":
    res = transcribe_once()
    print(f"[ASR] {res.text}  (latency={res.latency_ms:.0f} ms)")
