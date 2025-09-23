#!/usr/bin/env python3
"""
Dragon机器人真实语音控制
使用真实麦克风输入和语音识别
"""

import os
import sys
import signal
from wsl2_audio_interface import WSL2AudioInterface
from simple_voice_processor import DragonVoiceProcessor

class DragonRealVoiceController:
    """Dragon机器人真实语音控制器"""
    
    def __init__(self):
        """初始化真实语音控制器"""
        print("🎤 Dragon机器人真实语音控制系统")
        print("=" * 50)
        
        # 强制使用WSLg模式
        print("🔄 正在初始化真实语音模式...")
        self.audio_interface = WSL2AudioInterface(mode='wslg')
        self.voice_processor = DragonVoiceProcessor()
        
        # 设置音频回调
        self.audio_interface.set_audio_callback(self.handle_voice_command)
        
        # 机器人状态
        self.robot_x = 0.0
        self.robot_y = 0.0
        self.robot_orientation = 0.0
        self.robot_status = '待命'
        self.command_count = 0
        
        print("✅ 真实语音模式初始化完成")
    
    def handle_voice_command(self, voice_text: str):
        """处理语音命令"""
        print(f"\n🎤 收到语音: '{voice_text}'")
        
        # 解析命令
        result = self.voice_processor.parse_voice_command(voice_text)
        
        if result:
            print(f"🎯 解析结果: {result}")
            
            # 执行机器人动作
            self.execute_robot_action(result)
            
            # 语音反馈
            feedback = self.generate_feedback(result)
            print(f"🔊 反馈: {feedback}")
            self.audio_interface.play_audio(feedback)
            
        else:
            print("❓ 未识别的命令")
            feedback = f"抱歉，没有理解指令: {voice_text}"
            print(f"🔊 反馈: {feedback}")
            self.audio_interface.play_audio(feedback)
    
    def execute_robot_action(self, action_result):
        """执行机器人动作"""
        action = action_result.get('action')
        params = action_result.get('params', {})
        
        # 更新状态
        self.command_count += 1
        
        if action == 'move':
            direction = params.get('direction', 'forward')
            speed = params.get('speed', 1.0)
            
            # 模拟移动
            if direction == 'forward':
                self.robot_y += speed
            elif direction == 'backward':
                self.robot_y -= speed
            elif direction == 'left':
                self.robot_x -= speed
            elif direction == 'right':
                self.robot_x += speed
            
            self.robot_status = f'移动({direction})'
            
        elif action == 'rotate':
            angle = params.get('angle', 90)
            self.robot_orientation = (self.robot_orientation + angle) % 360
            self.robot_status = f'旋转({angle}°)'
            
        elif action == 'joint':
            joint = params.get('joint', 'unknown')
            action_type = params.get('action', 'move')
            self.robot_status = f'关节控制({joint}-{action_type})'
            
        elif action == 'stop':
            self.robot_status = '停止'
        
        # 显示状态
        self.display_robot_status()
    
    def generate_feedback(self, action_result):
        """生成语音反馈"""
        action = action_result.get('action')
        params = action_result.get('params', {})
        
        feedback_map = {
            'move': f"正在{params.get('direction', '移动')}",
            'rotate': f"正在旋转{params.get('angle', 90)}度",
            'joint': f"正在{params.get('action', '移动')}{params.get('joint', '关节')}",
            'stop': "已停止",
            'speed': f"调整速度到{params.get('level', 1)}",
            'pose': f"正在{params.get('pose', '动作')}"
        }
        
        return feedback_map.get(action, f"执行{action}")
    
    def display_robot_status(self):
        """显示机器人状态"""
        print("\n" + "=" * 40)
        print("🤖 Dragon机器人状态")
        print(f"位置: x={self.robot_x}, y={self.robot_y}")
        print(f"朝向: {self.robot_orientation}°")
        print(f"状态: {self.robot_status}")
        print(f"执行命令数: {self.command_count}")
        print("=" * 40)
    
    def test_audio_system(self):
        """测试音频系统"""
        print("🧪 测试真实语音系统...")
        test_result = self.audio_interface.test_audio()
        print(test_result)
        
        if test_result and "失败" in test_result:
            print("❌ 音频系统测试失败，无法启动真实语音控制")
            return False
        
        return True
    
    def start(self):
        """启动语音控制"""
        # 测试音频系统
        if not self.test_audio_system():
            return
        
        print("\n🎮 Dragon机器人真实语音控制已启动！")
        
        # 显示支持的命令
        print("\n🎤 支持的语音命令:")
        print("🚶 移动命令: 前进、后退、向左、向右")
        print("🔄 旋转命令: 转身、左转、右转") 
        print("🤲 关节控制: 抬起左手、放下右手、抬起左腿、放下右腿")
        print("⚡ 控制命令: 停止、快一点、慢一点、蹲下、站起")
        print("🎯 示例: '前进'、'抬起左手'、'转身'、'停止'")
        
        # 检查ASR配置
        asr_url = os.getenv("ASR_WS_URL", "")
        if asr_url:
            print(f"\n🌐 使用云端语音识别: {asr_url[:50]}...")
        else:
            print(f"\n⌨️ ASR_WS_URL未配置，将使用键盘输入模式")
            print("💡 提示: 配置ASR_WS_URL环境变量以启用真实语音识别")
        
        print("\n🎤 开始语音控制...")
        print("⌨️  按 Ctrl+C 退出")
        
        # 开始录音循环
        self.audio_interface.start_recording()
        
        # 保持程序运行
        while True:
            try:
                import time
                time.sleep(1)
            except KeyboardInterrupt:
                break
    
    def stop(self):
        """停止语音控制"""
        try:
            self.audio_interface.stop_recording()
        except:
            pass
        
        print("\n👋 Dragon机器人语音控制已停止")
        self.display_robot_status()

def signal_handler(sig, frame):
    """处理Ctrl+C信号"""
    print("\n🛑 正在停止语音控制...")
    sys.exit(0)

def main():
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    
    controller = None
    try:
        # 创建控制器
        controller = DragonRealVoiceController()
        
        # 启动语音控制
        controller.start()
    
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        print("🔄 请检查音频环境配置")
    
    finally:
        # 清理资源
        if controller:
            controller.stop()

if __name__ == "__main__":
    main()
