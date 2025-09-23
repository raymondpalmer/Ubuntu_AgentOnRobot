import os
import uuid
try:
    import pyaudio  # type: ignore
    PA_INT16 = pyaudio.paInt16
    PA_FLOAT32 = pyaudio.paFloat32
except Exception:
    PA_INT16 = 8
    PA_FLOAT32 = 1
from dotenv import load_dotenv

load_dotenv()

# 配置信息
ws_connect_config = {
    "base_url": os.getenv("DOUBAO_WS_BASE_URL", "wss://openspeech.bytedance.com/api/v3/realtime/dialogue"),
    "headers": {
        # 环境变量优先；若未设置则回退到历史默认值（用于快速恢复运行）
        "X-Api-App-ID": os.getenv("DOUBAO_API_APP_ID", "3618281145"),
        "X-Api-Access-Key": os.getenv("DOUBAO_API_ACCESS_KEY", "JLBO_LeiDxgcYsXYKSTrpoqEkNnXpDKF"),
        "X-Api-Resource-Id": os.getenv("DOUBAO_API_RESOURCE_ID", "volc.speech.dialog"),
        "X-Api-App-Key": os.getenv("DOUBAO_API_APP_KEY", "PlgvMymc7f3tQnJ6"),
        "X-Api-Connect-Id": os.getenv("DOUBAO_API_CONNECT_ID", str(uuid.uuid4())),
    }
}

start_session_req = {
    "asr": {
        "extra": {
            "end_smooth_window_ms": 1500,
        },
    },
    "tts": {
        "speaker": "zh_male_yunzhou_jupiter_bigtts",
        "audio_config": {
            "channel": 1,
            "format": "pcm",
            "sample_rate": 24000
        },
    },
    "dialog": {
        "bot_name": "豆包",
        "system_role": "你使用活泼灵动的女声，性格开朗，热爱生活。",
        "speaking_style": "你的说话风格简洁明了，语速适中，语调自然。",
        "location": {
          "city": "北京",
        },
        "extra": {
            "strict_audit": False,
            "audit_response": "支持客户自定义安全审核回复话术。"
        }
    }
}

input_audio_config = {
    "chunk": 3200,
    "format": "pcm",
    "channels": 1,
    "sample_rate": 16000,
    "bit_size": PA_INT16
}

output_audio_config = {
    "chunk": 3200,
    "format": "pcm",
    "channels": 1,
    "sample_rate": 24000,
    "bit_size": PA_FLOAT32
}
