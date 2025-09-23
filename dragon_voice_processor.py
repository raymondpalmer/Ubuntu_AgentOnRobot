#!/usr/bin/env python3
"""
Dragon机器人语音控制扩展
在原有的PolicyDeploymentNode基础上添加语音控制功能
"""

import sys
import os
import time
import threading
import json
from typing import Dict, Any, Optional

# 添加语音AI路径
sys.path.append('/home/ray/agent/doubao_robot_voice_agent_starter')

# 语音AI导入
try:
    from utils.agent_ark_sdk import call_agent
    from utils.asr import transcribe_once  
    from utils.tts import speak
    VOICE_AI_AVAILABLE = True
    print("✅ 语音AI模块加载成功")
except ImportError as e:
    VOICE_AI_AVAILABLE = False
    print(f"❌ 语音AI模块加载失败: {e}")

class DragonVoiceCommandProcessor:
    """Dragon机器人语音命令处理器"""
    
    def __init__(self):
        """初始化语音命令处理器"""
        self.voice_enabled = VOICE_AI_AVAILABLE
        self.listening = False
        
        # 命令映射：语音指令 -> 键盘按键
        self.voice_to_key_mapping = {
            # 基础移动
            'forward': 'w',      # 向前
            'backward': 's',     # 向后  
            'left': 'a',         # 向左
            'right': 'd',        # 向右
            'turn_left': 'z',    # 左转
            'turn_right': 'x',   # 右转
            
            # 控制指令
            'stop': 'e',         # 停止/重置
            'start': 'q',        # 启动策略
            'mode_switch': 'm',  # 切换模式
            
            # 数据记录
            'save_position': '1', # 保存位置数据
            'save_motor': '2',    # 保存电机数据
        }
        
        # 速度级别映射
        self.speed_levels = {
            '慢': 0.3,
            '中': 0.5, 
            '快': 0.8,
            '默认': 0.5
        }
        
        # Dragon机器人专用命令词典
        self.command_patterns = {
            # 移动指令
            'move_forward': ['向前', '前进', '往前走', '向前走'],
            'move_backward': ['向后', '后退', '倒退', '往后走'],
            'move_left': ['向左', '左移', '往左走', '向左走'],
            'move_right': ['向右', '右移', '往右走', '向右走'],
            'turn_left': ['左转', '向左转', '转左'],
            'turn_right': ['右转', '向右转', '转右'],
            
            # 控制指令
            'stop': ['停止', '停下', '站住', '暂停', '重置'],
            'start_policy': ['开始', '启动', '开始行走', '开始策略'],
            'switch_mode': ['切换模式', '换模式', '模式切换'],
            
            # 数据记录
            'save_data': ['保存数据', '记录数据', '保存轨迹'],
            'save_motor_data': ['保存电机数据', '记录电机', '保存电机'],
            
            # 状态查询
            'status': ['状态', '当前状态', '机器人状态'],
            'help': ['帮助', '指令', '命令列表']
        }
        
        print("🎤 Dragon语音命令处理器初始化完成")
    
    def parse_voice_command(self, voice_text: str) -> Optional[Dict[str, Any]]:
        """
        解析语音文本为机器人命令
        
        Args:
            voice_text: 语音识别文本
            
        Returns:
            解析后的命令字典，包含command, key, speed等信息
        """
        text = voice_text.lower().strip()
        
        # 提取速度信息
        speed = 0.5  # 默认速度
        for speed_word, speed_value in self.speed_levels.items():
            if speed_word in text:
                speed = speed_value
                break
        
        # 匹配命令模式
        for command, patterns in self.command_patterns.items():
            if any(pattern in text for pattern in patterns):
                return self._create_command(command, speed, text)
        
        return None
    
    def _create_command(self, command: str, speed: float, original_text: str) -> Dict[str, Any]:
        """创建标准化的命令字典"""
        command_map = {
            'move_forward': {'key': 'w', 'type': 'movement', 'direction': 'forward'},
            'move_backward': {'key': 's', 'type': 'movement', 'direction': 'backward'},
            'move_left': {'key': 'a', 'type': 'movement', 'direction': 'left'}, 
            'move_right': {'key': 'd', 'type': 'movement', 'direction': 'right'},
            'turn_left': {'key': 'z', 'type': 'rotation', 'direction': 'left'},
            'turn_right': {'key': 'x', 'type': 'rotation', 'direction': 'right'},
            'stop': {'key': 'e', 'type': 'control', 'action': 'stop'},
            'start_policy': {'key': 'q', 'type': 'control', 'action': 'start'},
            'switch_mode': {'key': 'm', 'type': 'control', 'action': 'mode_switch'},
            'save_data': {'key': '1', 'type': 'data', 'action': 'save_position'},
            'save_motor_data': {'key': '2', 'type': 'data', 'action': 'save_motor'},
            'status': {'key': None, 'type': 'query', 'action': 'status'},
            'help': {'key': None, 'type': 'query', 'action': 'help'}
        }
        
        base_cmd = command_map.get(command, {})
        return {
            'command': command,
            'key': base_cmd.get('key'),
            'type': base_cmd.get('type', 'unknown'),
            'speed': speed,
            'original_text': original_text,
            'timestamp': time.time(),
            **base_cmd
        }
    
    def process_voice_input(self) -> Optional[Dict[str, Any]]:
        """
        处理语音输入并返回解析后的命令
        
        Returns:
            解析后的命令字典或None
        """
        if not self.voice_enabled:
            print("❌ 语音功能未启用")
            return None
        
        try:
            print("🎤 开始语音识别...")
            
            # 语音识别
            asr_result = transcribe_once()
            if not asr_result.text:
                print("❌ 未检测到语音输入")
                return None
            
            print(f"🗣️ 识别文本: '{asr_result.text}'")
            
            # 使用豆包AI增强理解
            try:
                enhanced_prompt = f"""
用户对Dragon机器人说: "{asr_result.text}"

请分析这是什么类型的控制指令，并简洁回复。

如果是移动控制（向前/后/左/右/转向），请回复: 好的，机器人准备[动作]
如果是控制指令（停止/启动/切换），请回复: 收到，正在[动作]  
如果是数据操作，请回复: 明白，开始[操作]
如果不是机器人指令，请回复: 我是Dragon机器人助手，请说出控制指令
"""
                
                ai_response = call_agent(enhanced_prompt)
                ai_text = ai_response.text
                print(f"🤖 AI增强理解: {ai_text}")
                
            except Exception as e:
                print(f"⚠️ AI增强处理失败: {e}")
                ai_text = f"收到指令: {asr_result.text}"
            
            # 解析为机器人命令
            command = self.parse_voice_command(asr_result.text)
            
            if command:
                print(f"✅ 解析成功: {command['command']} -> 按键'{command['key']}'")
                
                # 语音反馈
                self._provide_voice_feedback(command, ai_text)
                return command
            else:
                print(f"❌ 无法解析的指令: {asr_result.text}")
                speak("抱歉，我无法理解这个指令。请说出明确的控制命令，比如向前、向后、停止等。")
                return None
                
        except Exception as e:
            print(f"❌ 语音处理异常: {e}")
            speak("语音处理出现错误")
            return None
    
    def _provide_voice_feedback(self, command: Dict[str, Any], ai_text: str):
        """提供语音反馈"""
        try:
            # 使用AI增强的回复文本
            speak(ai_text)
        except Exception as e:
            print(f"⚠️ 语音反馈失败: {e}")
            # 备用简单反馈
            feedback_map = {
                'movement': f"开始{command.get('direction', '')}移动",
                'rotation': f"开始{command.get('direction', '')}转向", 
                'control': f"执行{command.get('action', '')}",
                'data': f"开始{command.get('action', '')}",
                'query': '查询完成'
            }
            backup_text = feedback_map.get(command['type'], '命令已接收')
            try:
                speak(backup_text)
            except:
                print(f"📢 {backup_text}")
    
    def get_help_text(self) -> str:
        """获取帮助文本"""
        help_text = """
Dragon机器人语音控制指令:

移动控制:
• 向前/前进/往前走 - 机器人向前移动
• 向后/后退/倒退 - 机器人向后移动  
• 向左/左移/往左走 - 机器人向左移动
• 向右/右移/往右走 - 机器人向右移动
• 左转/向左转 - 机器人左转
• 右转/向右转 - 机器人右转

控制指令:
• 停止/停下/暂停 - 停止当前动作
• 开始/启动 - 启动行走策略
• 切换模式 - 切换控制模式

数据记录:
• 保存数据 - 保存位置轨迹
• 保存电机数据 - 保存电机状态

查询指令:
• 状态 - 查询机器人状态
• 帮助 - 显示指令列表

速度控制:
在指令中加入"慢"、"中"、"快"来控制速度
例如: "慢慢向前" / "快速左转"
"""
        return help_text
    
    def start_listening(self):
        """开始语音监听"""
        self.listening = True
        print("🎤 语音监听已启动")
    
    def stop_listening(self):
        """停止语音监听"""
        self.listening = False
        print("🔇 语音监听已停止")
    
    def is_voice_available(self) -> bool:
        """检查语音功能是否可用"""
        return self.voice_enabled

# 使用示例和测试函数
def test_voice_processor():
    """测试语音处理器"""
    processor = DragonVoiceCommandProcessor()
    
    print("🧪 测试语音命令处理器")
    print("=" * 50)
    
    # 测试命令
    test_commands = [
        "向前走",
        "慢慢向后", 
        "快速左转",
        "停止",
        "启动策略",
        "保存数据",
        "查看状态",
        "帮助"
    ]
    
    for cmd_text in test_commands:
        print(f"\n测试指令: '{cmd_text}'")
        command = processor.parse_voice_command(cmd_text)
        if command:
            print(f"  ✅ 解析结果: {command}")
        else:
            print(f"  ❌ 解析失败")
    
    # 显示帮助信息
    print("\n" + processor.get_help_text())

if __name__ == '__main__':
    test_voice_processor()
