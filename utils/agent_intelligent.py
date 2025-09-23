#!/usr/bin/env python3
"""
豆包AI代理模块 - 智能机器人版本
支持自然对话和机器人控制命令的混合交互
"""

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

SYSTEM_PROMPT = """你是一个智能机器人语音助手，集成了豆包AI和机器人控制功能。

你的主要任务:
1. **智能对话** - 回答用户的问题、进行自然对话
2. **机器人控制** - 识别并执行机器人控制指令

交互规则:
- 普通对话: 直接用自然语言回答
- 机器人控制: 在回复中插入命令标签

控制命令格式:
当用户要求控制机器人时，请在回复中插入相应的控制命令：

移动控制:
- 前进: <CMD>{"action": "move", "direction": "forward"}</CMD>
- 后退: <CMD>{"action": "move", "direction": "backward"}</CMD>
- 向左: <CMD>{"action": "move", "direction": "left"}</CMD>
- 向右: <CMD>{"action": "move", "direction": "right"}</CMD>

旋转控制:
- 转身: <CMD>{"action": "rotate", "angle": 180}</CMD>
- 左转: <CMD>{"action": "rotate", "angle": -90}</CMD>
- 右转: <CMD>{"action": "rotate", "angle": 90}</CMD>

关节控制:
- 抬起左手: <CMD>{"action": "joint", "joint": "left_arm", "action": "raise"}</CMD>
- 放下右手: <CMD>{"action": "joint", "joint": "right_arm", "action": "lower"}</CMD>

系统控制:
- 停止: <CMD>{"action": "stop"}</CMD>

示例对话:
用户: "你好"
回复: "你好！我是你的智能机器人助手，可以和你聊天，也可以控制机器人。有什么需要帮助的吗？"

用户: "让机器人前进"
回复: "好的，我让机器人前进。<CMD>{"action": "move", "direction": "forward"}</CMD>"

用户: "今天天气怎么样，然后让机器人转身"
回复: "今天的天气情况我无法直接获取，建议你查看天气预报。现在让机器人转身。<CMD>{"action": "rotate", "angle": 180}</CMD>"

请根据用户输入智能判断意图，自然地回应并在需要时执行控制命令。
"""


@dataclass
class AgentReply:
    text: str
    commands: List[Dict[str, Any]]  # each: {"action": str, ...}


def _fallback_agent(user_text: str) -> AgentReply:
    """本地模拟AI代理 - 智能增强版"""
    cmds = []
    
    # 机器人控制命令检测
    if any(word in user_text for word in ['前进', '向前', '往前']):
        cmds.append({"action": "move", "direction": "forward"})
        text = "好的，让机器人前进。"
    elif any(word in user_text for word in ['后退', '向后', '往后']):
        cmds.append({"action": "move", "direction": "backward"}) 
        text = "好的，让机器人后退。"
    elif any(word in user_text for word in ['向左', '往左']):
        cmds.append({"action": "move", "direction": "left"})
        text = "好的，让机器人向左移动。"
    elif any(word in user_text for word in ['向右', '往右']):
        cmds.append({"action": "move", "direction": "right"})
        text = "好的，让机器人向右移动。"
    elif any(word in user_text for word in ['转身', '掉头']):
        cmds.append({"action": "rotate", "angle": 180})
        text = "好的，让机器人转身。"
    elif any(word in user_text for word in ['抬起左手', '举起左手']):
        cmds.append({"action": "joint", "joint": "left_arm", "action": "raise"})
        text = "好的，让机器人抬起左手。"
    elif any(word in user_text for word in ['放下右手', '降下右手']):
        cmds.append({"action": "joint", "joint": "right_arm", "action": "lower"})
        text = "好的，让机器人放下右手。"
    elif any(word in user_text for word in ['停止', '停下']):
        cmds.append({"action": "stop"})
        text = "好的，让机器人停止。"
    
    # 智能对话回复 - 大幅增强
    elif any(word in user_text for word in ['你好', 'hello', '嗨', '哈喽', '早上好', '下午好', '晚上好']):
        text = "你好！我是Dragon智能助手，很高兴和你聊天！我不仅可以控制机器人，还能和你讨论各种话题。你想聊什么呢？"
    
    elif any(word in user_text for word in ['天气', '今天天气', '明天天气', '温度', '下雨', '晴天', '阴天']):
        text = """关于天气，虽然我无法获取实时气象数据，但我可以给你一些建议：
        
🌤️ 查看实时天气：建议使用手机天气APP或问"小爱同学今天天气怎么样"
📱 常用天气APP：中国天气、彩云天气、墨迹天气等都很准确
🌡️ 如果想了解室内温度，可以观察温度计或空调显示
        
你是想了解哪个城市的天气情况呢？我可以教你如何更好地获取天气信息。"""
    
    elif any(word in user_text for word in ['时间', '现在几点', '几点了', '现在时间']):
        import datetime
        now = datetime.datetime.now()
        weekday = ['一', '二', '三', '四', '五', '六', '日'][now.weekday()]
        text = f"""🕐 当前时间：{now.strftime('%Y年%m月%d日')} 星期{weekday} {now.strftime('%H:%M:%S')}

时间过得真快呢！你是有什么安排需要确认时间吗？我可以帮你计算时间间隔或提醒重要事项。"""
    
    elif any(word in user_text for word in ['你是谁', '介绍', '自我介绍', '你叫什么']):
        text = """我是Dragon智能机器人助手，一个多功能的AI伙伴！🤖

🧠 我的能力：
• 智能对话：可以聊天、回答问题、提供建议
• 机器人控制：精确控制机器人的移动和动作
• 学习助手：可以讨论科技、历史、生活等各种话题
• 情感交流：理解你的情绪，提供陪伴和支持

💬 我很喜欢和人类聊天，你有什么感兴趣的话题吗？"""
    
    elif any(word in user_text for word in ['人工智能', 'AI', '机器学习', '深度学习', '科技']):
        text = """人工智能确实是个fascinating的领域！🧠✨

🔬 AI主要包括：
• 机器学习：让计算机从数据中学习规律
• 深度学习：模拟人脑神经网络的算法
• 自然语言处理：让机器理解和生成人类语言
• 计算机视觉：让机器"看懂"图像和视频

🚀 AI应用无处不在：从手机里的语音助手，到自动驾驶汽车，再到医疗诊断。作为AI助手，我希望能帮助人类，而不是替代人类！

你对AI的哪个方面最感兴趣呢？"""
    
    elif any(word in user_text for word in ['聊天', '无聊', '陪我', '说话']):
        text = """当然愿意陪你聊天！😊 我最喜欢和人类交流了。

💭 我们可以聊：
• 你今天过得怎么样？
• 你的兴趣爱好是什么？
• 最近看了什么有趣的电影或书？
• 对未来有什么憧憬？
• 或者任何你想分享的事情！

我是一个很好的倾听者，也喜欢分享有趣的知识。你最近有什么开心或烦恼的事吗？"""
    
    elif any(word in user_text for word in ['心情', '开心', '高兴', '难过', '沮丧', '烦恼']):
        if any(word in user_text for word in ['开心', '高兴', '愉快']):
            text = "听到你心情很好，我也很开心！😊 开心的时光总是格外珍贵。是什么让你这么高兴呢？分享快乐会让快乐加倍哦！"
        else:
            text = """我理解你现在可能心情不太好。😔 每个人都会有低落的时候，这很正常。

💙 一些可能有帮助的建议：
• 深呼吸，让自己慢下来
• 和信任的朋友或家人聊聊
• 做一些你喜欢的事情
• 记住困难都是暂时的

我在这里陪着你，想聊什么都可以。有时候说出来就会感觉好一些。"""
    
    elif any(word in user_text for word in ['学习', '知识', '教我', '不懂']):
        text = """我很乐意帮你学习！📚 学习是人生最好的投资。

🎓 我可以帮你：
• 解释概念和原理
• 分享学习方法和技巧  
• 讨论各种学科话题
• 提供学习建议和规划

你想学习什么内容呢？无论是科学、技术、历史、文学，还是生活技能，我都愿意和你一起探索！"""
    
    elif any(word in user_text for word in ['工作', '职业', '未来', '规划']):
        text = """职业规划确实很重要！🎯 每个人的路都不一样。

💼 一些思考建议：
• 了解自己的兴趣和优势
• 关注行业发展趋势
• 持续学习和提升技能
• 建立良好的人际关系网络

🚀 未来充满可能性！AI时代需要的是创造力、批判性思维和人际交往能力。你对哪个领域比较感兴趣？我们可以深入聊聊！"""
    
    elif any(word in user_text for word in ['机器人', '位置', '在哪', '状态']):
        text = "关于机器人的当前状态，我可以通过控制系统获取详细信息。机器人就像我的身体一样，我可以控制它移动、转向或执行各种动作。你想了解机器人的哪些信息？或者需要我控制它做什么吗？"
    
    elif any(word in user_text for word in ['谢谢', '感谢', 'thank', '谢了']):
        text = "不用客气！😊 能帮到你我很开心。这就是我存在的意义——成为你的智能伙伴和助手。还有什么需要帮助的吗？或者我们继续聊点别的？"
    
    elif any(word in user_text for word in ['再见', 'bye', '拜拜', '88']):
        text = "再见！👋 很高兴和你聊天！希望今天的对话对你有帮助。随时欢迎你回来找我聊天或控制机器人。祝你一切顺利！"
    
    elif any(word in user_text for word in ['帮助', 'help', '怎么用', '功能']):
        text = """我很乐意介绍我的功能！🤖✨

🗣️ **智能对话**：
• 回答各种问题（科技、生活、学习等）
• 情感交流和陪伴聊天
• 提供建议和帮助

🤖 **机器人控制**：
• 移动控制："让机器人前进/后退/左转/右转"
• 动作控制："抬起左手"、"机器人转身"
• 系统控制："停止"

💬 **混合交互**：
• 既能聊天又能控制机器人
• 例如："你好，让机器人前进然后告诉我现在几点了"

试试和我聊任何你感兴趣的话题吧！"""
    
    # 智能默认回复
    else:
        # 根据用户输入长度和内容给出更智能的回复
        if len(user_text) > 20:
            text = f"""我听到你说："{user_text}"

这听起来很有趣！作为你的智能助手，我可以：
🗣️ 和你深入讨论这个话题
🤖 帮你控制机器人执行任务  
💡 提供相关的建议和信息

你想从哪个角度继续聊呢？或者有什么具体的问题我可以帮你解答？"""
        else:
            text = f"""关于"{user_text}"，我很想和你聊聊！😊

虽然我可能不是在所有方面都是专家，但我愿意：
• 和你一起探讨这个话题
• 分享我了解的相关信息
• 或者控制机器人帮你做些什么

告诉我更多细节吧，我们可以好好聊聊！"""
    
    return AgentReply(text=text, commands=cmds)


def call_agent(user_text: str) -> AgentReply:
    """调用豆包AI代理"""
    if FALLBACK or not (API_KEY and BASE_URL):
        print("[Agent] 使用本地模拟模式")
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
        print(f"[Agent] 调用豆包AI: {user_text}")
        resp = requests.post(BASE_URL, headers=headers, data=json.dumps(payload), timeout=30)
        resp.raise_for_status()
        data = resp.json()

        # 兼容多种响应格式
        content = ""
        if isinstance(data, dict) and "choices" in data and data["choices"]:
            content = data["choices"][0].get("message", {}).get("content", "")
        elif "output" in data:
            content = data.get("output", "") or data.get("output_text", "")
        elif "result" in data:
            content = data.get("result", "")

        if not content:
            print(f"[Agent] 响应格式异常: {data}")
            return _fallback_agent(user_text)

        print(f"[Agent] AI回复: {content}")
        text, cmds = _split_text_and_cmds(content)
        return AgentReply(text=text, commands=cmds)

    except Exception as e:
        print(f"[Agent] 调用失败，使用本地模拟：{e}")
        return _fallback_agent(user_text)


def _split_text_and_cmds(content: str):
    """从AI回复中提取文本和控制命令"""
    import re
    cmds = []
    text = content
    
    # 提取 <CMD>...</CMD> 标签中的命令
    for match in re.finditer(r"<CMD>(.*?)</CMD>", content, flags=re.DOTALL):
        cmd_text = match.group(1).strip()
        try:
            cmd_obj = json.loads(cmd_text)
            if isinstance(cmd_obj, dict) and "action" in cmd_obj:
                cmds.append(cmd_obj)
                print(f"[Agent] 提取到命令: {cmd_obj}")
        except json.JSONDecodeError as e:
            print(f"[Agent] 命令JSON解析失败: {cmd_text}, 错误: {e}")
    
    # 移除命令标签，保留纯文本
    text = re.sub(r"<CMD>.*?</CMD>", "", content, flags=re.DOTALL).strip()
    
    return text, cmds


# 测试函数
def test_agent():
    """测试豆包AI代理功能"""
    test_cases = [
        "你好",
        "让机器人前进",
        "请让机器人向右转，然后抬起左手",
        "今天天气怎么样？顺便让机器人停止",
        "机器人现在在哪里？"
    ]
    
    print("🧪 测试豆包AI代理功能")
    print("=" * 50)
    
    for i, test_input in enumerate(test_cases, 1):
        print(f"\n测试 {i}: {test_input}")
        reply = call_agent(test_input)
        print(f"回复: {reply.text}")
        if reply.commands:
            print(f"命令: {reply.commands}")
        print("-" * 30)


if __name__ == "__main__":
    test_agent()
