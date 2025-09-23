
import sys
from utils.tts import speak

if __name__ == "__main__":
    text = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else input("[TTS] 文本> ")
    speak(text)
