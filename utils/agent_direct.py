import json
import os
from dataclasses import dataclass
from typing import List, Dict, Any

import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("ARK_API_KEY", "") or os.getenv("DOUBAO_API_KEY", "")
BASE_URL = os.getenv("DOUBAO_BASE_URL", "")
MODEL = os.getenv("DOUBAO_MODEL", "doubao-lite")
FALLBACK = os.getenv("VOICE_FALLBACK", "1") == "1"

SYSTEM_PROMPT = """你是一个直接回答问题的AI助手。

规则:
- 直接回答，不要说"我很乐意"、"这是个好问题"等客套话
- 用户问什么就直接回答什么，不要反问
- 回答要具体、详细、实用
- 如果是机器人控制，使用[ROBOT_CMD]格式

示例:
用户: "给我介绍一下刘备"
回复: "刘备（161-223年），字玄德，蜀汉开国皇帝。出身汉朝皇室后裔但家境贫寒，以卖草鞋为生。性格仁德，善于用人，三顾茅庐请诸葛亮，桃园三结义与关张结拜。建立蜀汉与曹魏东吴三分天下，在夷陵之战败给陆逊后病逝。"

用户: "给我讲个笑话"  
回复: "程序员去面试，面试官问会什么语言，程序员说Java Python C++，面试官说我问的是中文还是英文，程序员愣了说：我会HTML！"
"""

@dataclass
class AgentReply:
    text: str
    commands: List[Dict[str, Any]]

def _fallback_agent(user_text: str) -> AgentReply:
    """本地AI代理 - 直接回答版本"""
    text = ""
    cmds = []
    
    # 机器人控制
    if '抬起左手' in user_text or '举起左手' in user_text:
        cmds.append({"tool": "move_joint", "args": {"joint_name": "left_shoulder", "angle": 90}})
        text = "抬起左手。"
    elif '放下左手' in user_text:
        cmds.append({"tool": "move_joint", "args": {"joint_name": "left_shoulder", "angle": 0}})
        text = "放下左手。"
    elif '抬起右手' in user_text or '举起右手' in user_text:
        cmds.append({"tool": "move_joint", "args": {"joint_name": "right_shoulder", "angle": 90}})
        text = "抬起右手。"
    elif '放下右手' in user_text:
        cmds.append({"tool": "move_joint", "args": {"joint_name": "right_shoulder", "angle": 0}})
        text = "放下右手。"
    
    # 历史人物 - 刘备
    elif '刘备' in user_text or '玄德' in user_text:
        text = """刘备（161-223年），字玄德，蜀汉开国皇帝。

基本信息：汉朝皇室后裔，家境贫寒，年轻时卖草鞋为生。身长七尺五寸，双手过膝。

性格特点：仁德著称，善于收买人心，有坚韧意志，屡败屡战，善于用人，重义气。

主要成就：
• 桃园三结义，与关羽张飞结为兄弟
• 三顾茅庐请出诸葛亮
• 建立蜀汉政权，与曹魏东吴三分天下
• 在夷陵之战中败给陆逊，次年病逝

历史评价：仁德君主代表，军事才能一般，但政治眼光独到，靠个人魅力起家的乱世枭雄。"""
    
    # 历史人物 - 曹操  
    elif '曹操' in user_text or '孟德' in user_text:
        text = """曹操（155-220年），字孟德，政治家、军事家、文学家。

政治军事：统一北方，挟天子以令诸侯，用人唯才，建立屯田制，奠定曹魏基业。

文学成就：建安文学代表，《短歌行》"对酒当歌，人生几何"，《观沧海》展现胸怀。

历史争议："治世之能臣，乱世之奸雄"，《三国演义》塑造成反派，但历史上改革有前瞻性。

评价：既有政治谋略，又有文学才华，还有军事能力的复合型人才。"""
    
    # 历史人物 - 诸葛亮
    elif '诸葛亮' in user_text or '孔明' in user_text:
        text = """诸葛亮（181-234年），字孔明，蜀汉丞相，著名政治家、军事家。

成名经历：隐居隆中，刘备三顾茅庐请出山，提出《隆中对》战略规划。

主要功绩：
• 协助刘备建立蜀汉政权
• 六出祁山北伐曹魏
• 发明木牛流马、诸葛连弩等器械
• 治理蜀国井井有条

著名事迹：草船借箭、空城计、七擒孟获、挥泪斩马谡。

历史地位：中国历史上智慧的化身，"鞠躬尽瘁，死而后已"的忠臣典型。"""
    
    # 笑话
    elif '笑话' in user_text or '搞笑' in user_text or '幽默' in user_text:
        text = """程序员的三大谎言：
1. "我明天就修这个bug"
2. "这个功能很简单，一天搞定"  
3. "我绝对不会再熬夜写代码"

结果：bug还在，功能变成一周工程，又熬到凌晨三点。

另一个：程序员面试，面试官问会什么语言，程序员说Java Python C++，面试官说我问的是中文还是英文，程序员愣了：我会HTML！"""
    
    # 天气
    elif '天气' in user_text or '气温' in user_text:
        text = """我无法实时查看天气，建议：
• 看窗外天空和云朵
• 打开手机天气应用
• 关注天气预报

穿衣建议：早晚温差大带外套，阴天准备雨具，夏天防晒冬天保暖。"""
    
    # 问候
    elif '你好' in user_text or 'hello' in user_text:
        text = """你好！我是Dragon智能助手。

功能：讲历史故事、介绍历史人物、说笑话、聊天气生活、控制机器人、回答问题。"""
    
    else:
        # 默认回复 - 直接尝试回答
        text = f"关于{user_text}的问题，我需要更具体的信息才能给出准确回答。请告诉我你想了解的具体方面。"
    
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
        # 确保URL包含完整路径
        api_url = BASE_URL
        if not api_url.endswith('/chat/completions'):
            api_url = api_url.rstrip('/') + '/chat/completions'
            
        resp = requests.post(api_url, headers=headers, data=json.dumps(payload), timeout=30)
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
        print(f"[Agent] API调用失败，使用本地模拟：{e}")
        return _fallback_agent(user_text)

def get_agent_response(user_text: str) -> str:
    """获取AI代理回复（简化版本，只返回文本）"""
    reply = call_agent(user_text)
    return reply.text

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
