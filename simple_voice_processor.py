#!/usr/bin/env python3
"""
简化版Dragon机器人语音命令处理器
用于WSL2环境下的语音控制演示
"""

import re
from typing import Dict, Any, Optional

class DragonVoiceProcessor:
    """Dragon机器人语音命令处理器"""
    
    def __init__(self):
        """初始化语音命令处理器"""
        self.setup_command_patterns()
    
    def setup_command_patterns(self):
        """设置语音命令模式"""
        
        # 移动命令模式
        self.movement_patterns = {
            r'(前进|向前|往前)': {'action': 'move', 'params': {'direction': 'forward'}},
            r'(后退|向后|往后)': {'action': 'move', 'params': {'direction': 'backward'}},
            r'(向左|往左|左转)': {'action': 'move', 'params': {'direction': 'left'}},
            r'(向右|往右|右转)': {'action': 'move', 'params': {'direction': 'right'}},
        }
        
        # 旋转命令模式
        self.rotation_patterns = {
            r'(转身|掉头)': {'action': 'rotate', 'params': {'angle': 180}},
            r'(左转|向左转)': {'action': 'rotate', 'params': {'angle': -90}},
            r'(右转|向右转)': {'action': 'rotate', 'params': {'angle': 90}},
        }
        
        # 关节控制命令模式
        self.joint_patterns = {
            r'(抬起|举起|抬).*?(左手|左臂)': {'action': 'joint', 'params': {'joint': 'left_arm', 'action': 'raise'}},
            r'(放下|降下|落下).*?(左手|左臂)': {'action': 'joint', 'params': {'joint': 'left_arm', 'action': 'lower'}},
            r'(抬起|举起|抬).*?(右手|右臂)': {'action': 'joint', 'params': {'joint': 'right_arm', 'action': 'raise'}},
            r'(放下|降下|落下).*?(右手|右臂)': {'action': 'joint', 'params': {'joint': 'right_arm', 'action': 'lower'}},
            r'(抬起|举起|抬).*?(左腿|左脚)': {'action': 'joint', 'params': {'joint': 'left_leg', 'action': 'raise'}},
            r'(放下|降下|落下).*?(左腿|左脚)': {'action': 'joint', 'params': {'joint': 'left_leg', 'action': 'lower'}},
            r'(抬起|举起|抬).*?(右腿|右脚)': {'action': 'joint', 'params': {'joint': 'right_leg', 'action': 'raise'}},
            r'(放下|降下|落下).*?(右腿|右脚)': {'action': 'joint', 'params': {'joint': 'right_leg', 'action': 'lower'}},
        }
        
        # 控制命令模式
        self.control_patterns = {
            r'(停止|停下|暂停)': {'action': 'stop', 'params': {}},
            r'(快一点|快点|加速)': {'action': 'speed', 'params': {'level': 2}},
            r'(慢一点|慢点|减速)': {'action': 'speed', 'params': {'level': 1}},
            r'(蹲下|下蹲)': {'action': 'pose', 'params': {'pose': 'squat'}},
            r'(站起|起立|站立)': {'action': 'pose', 'params': {'pose': 'stand'}},
        }
        
        # 合并所有模式
        self.all_patterns = {}
        self.all_patterns.update(self.movement_patterns)
        self.all_patterns.update(self.rotation_patterns)
        self.all_patterns.update(self.joint_patterns)
        self.all_patterns.update(self.control_patterns)
    
    def parse_voice_command(self, voice_text: str) -> Optional[Dict[str, Any]]:
        """
        解析语音命令
        
        Args:
            voice_text: 语音识别文本
            
        Returns:
            解析后的命令字典，包含action和params
        """
        if not voice_text:
            return None
        
        # 清理输入文本
        voice_text = voice_text.strip().lower()
        
        # 尝试匹配所有模式
        for pattern, command in self.all_patterns.items():
            if re.search(pattern, voice_text):
                return command.copy()
        
        # 如果没有匹配到特定模式，尝试关键词匹配
        return self.fallback_keyword_match(voice_text)
    
    def fallback_keyword_match(self, voice_text: str) -> Optional[Dict[str, Any]]:
        """备用关键词匹配"""
        
        # 方向关键词
        if any(keyword in voice_text for keyword in ['前', '进']):
            return {'action': 'move', 'params': {'direction': 'forward'}}
        elif any(keyword in voice_text for keyword in ['后', '退']):
            return {'action': 'move', 'params': {'direction': 'backward'}}
        elif any(keyword in voice_text for keyword in ['左']):
            return {'action': 'move', 'params': {'direction': 'left'}}
        elif any(keyword in voice_text for keyword in ['右']):
            return {'action': 'move', 'params': {'direction': 'right'}}
        
        # 停止关键词
        elif any(keyword in voice_text for keyword in ['停', '止']):
            return {'action': 'stop', 'params': {}}
        
        # 手臂关键词
        elif '手' in voice_text or '臂' in voice_text:
            if '抬' in voice_text or '举' in voice_text:
                side = 'left' if '左' in voice_text else 'right'
                return {'action': 'joint', 'params': {'joint': f'{side}_arm', 'action': 'raise'}}
            elif '放' in voice_text or '下' in voice_text:
                side = 'left' if '左' in voice_text else 'right'
                return {'action': 'joint', 'params': {'joint': f'{side}_arm', 'action': 'lower'}}
        
        return None
    
    def get_command_help(self) -> str:
        """获取命令帮助信息"""
        help_text = """
Dragon机器人语音命令列表：

🚶 移动命令：
  - 前进、向前、往前
  - 后退、向后、往后  
  - 向左、往左、左转
  - 向右、往右、右转

🔄 旋转命令：
  - 转身、掉头
  - 左转、向左转
  - 右转、向右转

🤲 关节控制：
  - 抬起左手/右手
  - 放下左手/右手
  - 抬起左腿/右腿
  - 放下左腿/右腿

⚡ 控制命令：
  - 停止、停下、暂停
  - 快一点、加速
  - 慢一点、减速
  - 蹲下、下蹲
  - 站起、起立
        """
        return help_text
    
    def test_voice_commands(self):
        """测试语音命令解析"""
        test_commands = [
            "前进",
            "向右转", 
            "抬起左手",
            "放下右手",
            "后退",
            "停止",
            "快一点",
            "蹲下",
            "站起"
        ]
        
        print("语音命令解析测试：")
        print("=" * 40)
        
        for cmd in test_commands:
            result = self.parse_voice_command(cmd)
            print(f"输入: '{cmd}'")
            print(f"解析: {result}")
            print("-" * 30)


# 测试代码
if __name__ == "__main__":
    processor = DragonVoiceProcessor()
    processor.test_voice_commands()
    print(processor.get_command_help())
