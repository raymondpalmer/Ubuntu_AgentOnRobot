import json
import os
from dataclasses import dataclass
from typing import List, Dict, Any

from dotenv import load_dotenv

load_dotenv()

# 使用火山引擎官方SDK
try:
    from volcenginesdkarkruntime import Ark
    ARK_AVAILABLE = True
except ImportError:
    ARK_AVAILABLE = False
    print("[Warning] 火山引擎SDK未安装，请运行: pip install 'volcengine-python-sdk[ark]'")

# 支持多种API Key环境变量名称
API_KEY = os.getenv("ARK_API_KEY") or os.getenv("DOUBAO_API_KEY", "")
BASE_URL = os.getenv("DOUBAO_BASE_URL", "")
MODEL = os.getenv("DOUBAO_MODEL", "doubao-lite")
FALLBACK = os.getenv("VOICE_FALLBACK", "1") == "1"

SYSTEM_PROMPT = """你是一个服务于人形机器人的语音助手。

当需要执行"控制命令"（例如移动某个关节、回到安全位、停止等）时：
- 请 **仅** 在回复中额外插入一段 `<CMD>{...}</CMD>`，JSON 模式如下：
  {
    "tool": "move_joint",
    "args": {"joint": "r_elbow", "position_deg": 30.0, "speed": 0.5}
  }
- 其它正常对话请直接用自然语言回答。
- 严禁在未确认安全的情况下执行危险命令；必要时请先复述并让用户确认。
"""


@dataclass
class AgentReply:
    text: str
    commands: List[Dict[str, Any]]  # each: {"tool": str, "args": {...}}


def _fallback_agent(user_text: str) -> AgentReply:
    """本地模拟：当输入包含类似 '抬右肘30度' 时，生成一条 move_joint 命令"""
    text = f"收到：{user_text}。我会尽量帮你。"
    cmds = []
    if "抬右肘" in user_text:
        cmds.append({"tool": "move_joint", "args": {"joint": "r_elbow", "position_deg": 30.0, "speed": 0.5}})
        text += "（准备抬右肘 30 度）"
    elif "抬左肘" in user_text:
        cmds.append({"tool": "move_joint", "args": {"joint": "l_elbow", "position_deg": 30.0, "speed": 0.5}})
        text += "（准备抬左肘 30 度）"
    elif "挥手" in user_text:
        cmds.append({"tool": "move_joint", "args": {"joint": "r_wrist", "position_deg": 45.0, "speed": 0.8}})
        text += "（准备挥手）"
    return AgentReply(text=text, commands=cmds)


def call_agent_with_ark_sdk(user_text: str) -> AgentReply:
    """使用火山引擎官方SDK调用豆包Agent"""
    if FALLBACK or not ARK_AVAILABLE or not (API_KEY and MODEL):
        return _fallback_agent(user_text)
    
    try:
        # 初始化Ark客户端
        client = Ark(
            api_key=API_KEY,
            base_url=BASE_URL if BASE_URL else None  # 如果没有设置base_url，使用默认值
        )
        
        # 构建消息
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text},
        ]
        
        # 调用Chat Completions接口
        completion = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.3,
            max_tokens=1000
        )
        
        # 提取回复内容
        content = completion.choices[0].message.content
        if not content:
            print("[Agent] SDK返回空内容，使用本地模拟")
            return _fallback_agent(user_text)
        
        # 解析文本和命令
        text, cmds = _split_text_and_cmds(content)
        return AgentReply(text=text, commands=cmds)
        
    except Exception as e:
        print(f"[Agent] SDK调用失败，使用本地模拟：{e}")
        return _fallback_agent(user_text)


def call_agent_with_requests(user_text: str) -> AgentReply:
    """使用requests库调用豆包Agent（原有方法）"""
    if FALLBACK or not (API_KEY and BASE_URL):
        return _fallback_agent(user_text)

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text},
        ],
        "temperature": 0.3,
    }
    try:
        import requests
        resp = requests.post(BASE_URL, headers=headers, data=json.dumps(payload), timeout=30)
        resp.raise_for_status()
        data = resp.json()

        # 兼容 OpenAI 风格的 choices
        content = ""
        if isinstance(data, dict) and "choices" in data and data["choices"]:
            content = data["choices"][0].get("message", {}).get("content", "")

        if not content and "output" in data:
            content = data.get("output", "") or data.get("output_text", "")

        text, cmds = _split_text_and_cmds(content)
        return AgentReply(text=text, commands=cmds)

    except Exception as e:
        print(f"[Agent] 调用失败，使用本地模拟：{e}")
        return _fallback_agent(user_text)


def call_agent(user_text: str) -> AgentReply:
    """主调用函数：优先使用官方SDK，失败时回退到requests"""
    # 优先尝试使用官方SDK
    if ARK_AVAILABLE:
        try:
            return call_agent_with_ark_sdk(user_text)
        except Exception as e:
            print(f"[Agent] SDK方法失败，尝试requests方法：{e}")
    
    # 回退到requests方法
    return call_agent_with_requests(user_text)


def _split_text_and_cmds(content: str):
    """从模型回复中截取 <CMD>{...}</CMD> 段落，可出现多次"""
    import re
    cmds = []
    text = content
    for m in re.finditer(r"<CMD>(.*?)</CMD>", content, flags=re.DOTALL):
        block = m.group(1)
        try:
            obj = json.loads(block)
            if isinstance(obj, dict) and "tool" in obj:
                cmds.append(obj)
        except Exception:
            pass
    text = re.sub(r"<CMD>.*?</CMD>", "", content, flags=re.DOTALL).strip()
    return text, cmds
