
import sys
from utils.agent import call_agent
from utils.tts import speak

def main():
    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
    else:
        text = input("[AgentBridge] 输入文本> ").strip()

    rep = call_agent(text)
    print("[Agent] 回复：", rep.text)
    speak(rep.text)
    if rep.commands:
        print("[Agent] 命令：", rep.commands)

if __name__ == "__main__":
    main()
