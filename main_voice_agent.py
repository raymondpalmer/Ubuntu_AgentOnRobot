
import os
from dotenv import load_dotenv

load_dotenv()

from utils.asr import transcribe_once
from utils.agent import call_agent
from utils.tts import speak

import requests
import json

ROUTER_BASE = os.getenv("ROUTER_BASE", "http://127.0.0.1:8008")


def maybe_execute_commands(cmds):
    for cmd in cmds:
        tool = cmd.get("tool")
        args = cmd.get("args", {})
        if tool == "move_joint":
            try:
                r = requests.post(f"{ROUTER_BASE}/move_joint", json=args, timeout=2)
                print("[Router]", r.status_code, r.text[:120])
            except Exception as e:
                print("[Router] move_joint 调用失败：", e)
        elif tool == "say":
            text = str(args.get("text", ""))
            speak(text)
        else:
            print("[Router] 未知工具：", tool, args)


def main_loop():
    print("=== Doubao Voice Agent Demo ===")
    print("Press Enter to talk (record 5s). Type 'q' then Enter to quit.\n")

    while True:
        line = input("[Ready] > ").strip().lower()
        if line == "q":
            break

        asr = transcribe_once()
        if not asr.text:
            print("[ASR] 没听到 / 输入为空")
            continue
        print(f"[ASR] {asr.text} ({asr.latency_ms:.0f} ms)")

        reply = call_agent(asr.text)
        print(f"[Agent] {reply.text}")
        speak(reply.text)

        if reply.commands:
            print("[Agent] 检测到命令：", reply.commands)
            maybe_execute_commands(reply.commands)


if __name__ == "__main__":
    main_loop()
