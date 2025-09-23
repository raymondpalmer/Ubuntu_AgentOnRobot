#!/usr/bin/env python3
"""
Dragon机器人WSL2语音控制演示
集成WSL2音频接口和Dragon机器人控制系统
"""

import os
import sys
import time
import threading
from typing import Dict, Any, Optional

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from wsl2_audio_interface import WSL2AudioInterface
from simple_voice_processor import DragonVoiceProcessor

class DragonWSL2VoiceController:
    """Dragon机器人WSL2语音控制器"""
    
    def __init__(self, audio_mode: str = 'mock'):
        """
        初始化控制器
        
        Args:
            audio_mode: 音频模式 ('mock', 'wslg', 'virtual')
        """
        self.running = False
        
        # 初始化音频接口
        self.audio_interface = WSL2AudioInterface(mode=audio_mode)
        self.audio_interface.set_audio_callback(self.handle_voice_command)
        
        # 初始化语音处理器
        self.voice_processor = DragonVoiceProcessor()
        
        # 机器人状态
        self.robot_state = {
            'position': {'x': 0, 'y': 0, 'z': 0},
            'orientation': 0,
            'joints': {f'joint_{i}': 0.0 for i in range(12)},
            'moving': False,
            'last_command': None,
            'command_count': 0
        }
        
        print("Dragon WSL2语音控制器初始化完成")
        print(f"音频模式: {self.audio_interface.mode}")
    
    def handle_voice_command(self, voice_text: str):
        """处理语音命令"""
        try:
            print(f"\n🎤 收到语音: '{voice_text}'")
            
            # 解析语音命令
            key_action = self.voice_processor.parse_voice_command(voice_text)
            
            if key_action:
                print(f"🎯 解析结果: {key_action}")
                
                # 执行机器人动作
                self.execute_robot_action(key_action, voice_text)
                
                # 语音反馈
                feedback = self.generate_feedback(key_action)
                self.audio_interface.play_audio(feedback)
                
            else:
                print("❌ 未识别的语音命令")
                self.audio_interface.play_audio("抱歉，我没有理解这个命令")
        
        except Exception as e:
            print(f"❌ 处理语音命令失败: {e}")
            self.audio_interface.play_audio("命令处理出错")
    
    def execute_robot_action(self, key_action: Dict[str, Any], original_command: str):
        """执行机器人动作"""
        action_type = key_action.get('action')
        params = key_action.get('params', {})
        
        # 更新机器人状态
        self.robot_state['last_command'] = original_command
        self.robot_state['command_count'] += 1
        self.robot_state['moving'] = True
        
        print(f"🤖 执行动作: {action_type}")
        
        if action_type == 'move':
            direction = params.get('direction')
            speed = params.get('speed', 1.0)
            self.simulate_movement(direction, speed)
            
        elif action_type == 'rotate':
            angle = params.get('angle', 90)
            self.simulate_rotation(angle)
            
        elif action_type == 'joint':
            joint_name = params.get('joint')
            action = params.get('action')
            self.simulate_joint_action(joint_name, action)
            
        elif action_type == 'stop':
            self.simulate_stop()
            
        elif action_type == 'speed':
            level = params.get('level', 1)
            self.simulate_speed_change(level)
        
        # 模拟执行时间
        time.sleep(0.5)
        self.robot_state['moving'] = False
        
        # 显示当前状态
        self.display_robot_status()
    
    def simulate_movement(self, direction: str, speed: float):
        """模拟移动动作"""
        movement_map = {
            'forward': (0, 1),
            'backward': (0, -1),
            'left': (-1, 0),
            'right': (1, 0)
        }
        
        if direction in movement_map:
            dx, dy = movement_map[direction]
            self.robot_state['position']['x'] += dx * speed
            self.robot_state['position']['y'] += dy * speed
            print(f"  移动方向: {direction}, 速度: {speed}")
    
    def simulate_rotation(self, angle: float):
        """模拟旋转动作"""
        self.robot_state['orientation'] = (self.robot_state['orientation'] + angle) % 360
        print(f"  旋转角度: {angle}°")
    
    def simulate_joint_action(self, joint_name: str, action: str):
        """模拟关节动作"""
        if joint_name in self.robot_state['joints']:
            if action == 'raise':
                self.robot_state['joints'][joint_name] = min(
                    self.robot_state['joints'][joint_name] + 30, 90
                )
            elif action == 'lower':
                self.robot_state['joints'][joint_name] = max(
                    self.robot_state['joints'][joint_name] - 30, -90
                )
            print(f"  关节动作: {joint_name} {action}")
    
    def simulate_stop(self):
        """模拟停止动作"""
        self.robot_state['moving'] = False
        print("  机器人停止")
    
    def simulate_speed_change(self, level: int):
        """模拟速度变化"""
        print(f"  速度调整到等级: {level}")
    
    def generate_feedback(self, key_action: Dict[str, Any]) -> str:
        """生成语音反馈"""
        action_type = key_action.get('action')
        params = key_action.get('params', {})
        
        feedback_map = {
            'move': f"正在{params.get('direction', '移动')}",
            'rotate': f"正在旋转{params.get('angle', 90)}度",
            'joint': f"正在{params.get('action', '移动')}{params.get('joint', '关节')}",
            'stop': "已停止",
            'speed': f"速度调整到{params.get('level', 1)}级"
        }
        
        return feedback_map.get(action_type, "收到命令")
    
    def display_robot_status(self):
        """显示机器人状态"""
        print("\n" + "="*50)
        print("🤖 Dragon机器人状态")
        print(f"位置: x={self.robot_state['position']['x']:.1f}, "
              f"y={self.robot_state['position']['y']:.1f}")
        print(f"朝向: {self.robot_state['orientation']:.1f}°")
        print(f"状态: {'移动中' if self.robot_state['moving'] else '静止'}")
        print(f"执行命令数: {self.robot_state['command_count']}")
        if self.robot_state['last_command']:
            print(f"最后命令: {self.robot_state['last_command']}")
        print("="*50)
    
    def start_voice_control(self):
        """开始语音控制"""
        if self.running:
            return
        
        self.running = True
        print("\n🎙️ 开始Dragon机器人语音控制")
        print("说出命令来控制机器人，如：")
        print("  - 前进、后退、向左、向右")
        print("  - 抬起左手、放下右手")
        print("  - 转身、停止")
        print("  - 快一点、慢一点")
        print("\n按 Ctrl+C 停止控制")
        
        try:
            self.audio_interface.start_recording()
            
            # 保持运行状态
            while self.running:
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n正在停止语音控制...")
        finally:
            self.stop_voice_control()
    
    def stop_voice_control(self):
        """停止语音控制"""
        if not self.running:
            return
        
        self.running = False
        self.audio_interface.stop_recording()
        print("语音控制已停止")
    
    def demo_mode(self):
        """演示模式"""
        print("\n🎯 开始Dragon机器人语音控制演示")
        
        # 演示命令列表
        demo_commands = [
            "前进",
            "向右转",
            "抬起左手",
            "后退",
            "放下左手",
            "向左转",
            "停止"
        ]
        
        print("自动执行演示命令...")
        for i, command in enumerate(demo_commands, 1):
            print(f"\n📢 演示命令 {i}/{len(demo_commands)}: {command}")
            self.handle_voice_command(command)
            time.sleep(2)
        
        print("\n🎉 演示完成！")
        print("机器人已执行所有演示命令")


def main():
    """主函数"""
    print("Dragon机器人WSL2语音控制系统")
    print("=" * 60)
    
    # 创建控制器
    controller = DragonWSL2VoiceController()
    
    # 检查可用音频模式
    available_modes = controller.audio_interface.get_available_modes()
    print(f"可用音频模式: {available_modes}")
    
    # 显示菜单
    while True:
        print("\n请选择操作:")
        print("1. 开始语音控制")
        print("2. 运行演示模式")
        print("3. 查看机器人状态")
        print("4. 测试音频系统")
        print("5. 退出")
        
        try:
            choice = input("输入选择 (1-5): ").strip()
            
            if choice == '1':
                controller.start_voice_control()
            elif choice == '2':
                controller.demo_mode()
            elif choice == '3':
                controller.display_robot_status()
            elif choice == '4':
                controller.audio_interface.test_audio()
            elif choice == '5':
                print("再见！")
                break
            else:
                print("无效选择，请重试")
                
        except KeyboardInterrupt:
            print("\n\n程序被中断")
            break
        except Exception as e:
            print(f"错误: {e}")


if __name__ == "__main__":
    main()
