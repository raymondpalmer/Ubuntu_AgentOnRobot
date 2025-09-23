import json
import os
from dataclasses import dataclass
from typing import List, Dict, Any

import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("DOUBAO_API_KEY", "")
BASE_URL = os.getenv("DOUBAO_BASE_URL", "")
MODEL = os.getenv("DOUBAO_MODEL", "doubao-lite")
FALLBACK = os.getenv("VOICE_FALLBACK", "1") == "1"

SYSTEM_PROMPT = """你是一个智能机器人助手，具备对话和机器人控制功能。

你的主要任务:
1. **智能对话** - 回答用户的问题、进行自然对话
2. **机器人控制** - 识别并执行机器人控制指令

交互规则:
- 普通对话: 直接用自然语言回答
- 机器人控制: 识别意图后生成对应的控制命令

机器人控制命令格式:
对于需要机器人控制的请求，你需要在回复中包含控制命令，格式为:
[ROBOT_CMD] 命令类型:参数

支持的命令:
- move_joint: 控制关节运动
  参数: {"joint_name": "关节名", "angle": 角度值}

示例:
用户: "抬起左手"
回复: "好的，我来抬起左手。[ROBOT_CMD] move_joint:{"joint_name": "left_shoulder", "angle": 90}"

用户: "放下右手"  
回复: "好的，我来放下右手。[ROBOT_CMD] move_joint:{"joint_name": "right_shoulder", "angle": 0}"

用户: "你好"
回复: "你好！我是你的机器人助手，可以和你聊天，也可以控制机器人。有什么需要帮助的吗？"
"""


@dataclass
class AgentReply:
    text: str
    commands: List[Dict[str, Any]]


def _fallback_agent(user_text: str) -> AgentReply:
    """本地模拟AI代理 - 简化版本"""
    text = f"收到：{user_text}。我会尽量帮你。"
    cmds = []
    
    # 简单的规则匹配
    if any(word in user_text for word in ['抬起左手', '举起左手']):
        cmds.append({"tool": "move_joint", "args": {"joint_name": "left_shoulder", "angle": 90}})
        text = "好的，抬起左手。"
    elif any(word in user_text for word in ['放下左手']):
        cmds.append({"tool": "move_joint", "args": {"joint_name": "left_shoulder", "angle": 0}})
        text = "好的，放下左手。"
    elif any(word in user_text for word in ['抬起右手', '举起右手']):
        cmds.append({"tool": "move_joint", "args": {"joint_name": "right_shoulder", "angle": 90}})
        text = "好的，抬起右手。"
    elif any(word in user_text for word in ['放下右手']):
        cmds.append({"tool": "move_joint", "args": {"joint_name": "right_shoulder", "angle": 0}})
        text = "好的，放下右手。"
    elif any(word in user_text for word in ['说话', '问候']):
        cmds.append({"tool": "say", "args": {"text": "你好，我是机器人"}})
        text = "我来说话。"
    elif any(word in user_text for word in ['你好', 'hello']):
        text = "你好！我是你的机器人助手，可以和你聊天，也可以控制机器人。有什么需要帮助的吗？"
    
    return AgentReply(text=text, commands=cmds)


def call_agent(user_text: str) -> AgentReply:
    """调用AI代理"""
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
        resp = requests.post(BASE_URL, headers=headers, data=json.dumps(payload), timeout=30)
        resp.raise_for_status()
        data = resp.json()

        content = ""
        if isinstance(data, dict) and "choices" in data and data["choices"]:
            content = data["choices"][0].get("message", {}).get("content", "")
        
        if not content:
            return _fallback_agent(user_text)

        text, cmds = _parse_robot_commands(content)
        return AgentReply(text=text, commands=cmds)

    except Exception as e:
        print(f"[Agent] 调用失败，使用本地模拟：{e}")
        return _fallback_agent(user_text)


def _parse_robot_commands(content: str):
    """从AI回复中解析机器人命令"""
    import re
    
    commands = []
    text = content
    
    # 查找 [ROBOT_CMD] 命令
    pattern = r'\[ROBOT_CMD\]\s*(\w+):\s*({.*?})'
    matches = re.findall(pattern, content)
    
    for cmd_type, args_str in matches:
        try:
            args = json.loads(args_str)
            commands.append({"tool": cmd_type, "args": args})
        except json.JSONDecodeError:
            continue
    
    # 移除命令部分，只保留文本
    text = re.sub(r'\[ROBOT_CMD\][^\]]*', '', content).strip()
    
    return text, commands
