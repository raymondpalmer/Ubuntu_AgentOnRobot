#!/usr/bin/env python3
"""
Dragon机器人WSLg语音控制直接启动
自动使用WSLg模式进行真实语音控制
"""

import os
import sys
import time

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from wsl2_audio_interface import WSL2AudioInterface
    from simple_voice_processor import DragonVoiceProcessor
except ImportError as e:
    print(f"❌ 导入模块失败: {e}")
    sys.exit(1)

class DragonWSLGDirectController:
    """Dragon机器人WSLg直接控制器"""
    
    def __init__(self):
        """初始化WSLg控制器"""
        print("🎤 Dragon机器人WSLg语音控制系统")
        print("=" * 50)
        
        # 强制使用WSLg模式
        print("🔄 正在初始化WSLg音频模式...")
        self.audio_interface = WSL2AudioInterface(mode='wslg')
        self.voice_processor = DragonVoiceProcessor()
        
        # 设置音频回调
        self.audio_interface.set_audio_callback(self.handle_voice_command)
        
        # 机器人状态
        self.robot_state = {
            'position': {'x': 0.0, 'y': 0.0},
            'orientation': 0.0,
            'status': '待命',
            'command_count': 0,
            'running': False
        }
        
        print("✅ WSLg模式初始化完成")
        self.test_audio_system()
    
    def test_audio_system(self):
        """测试音频系统"""
        print("\n🧪 测试WSLg音频系统...")
        
        try:
            # 测试播放
            print("🔊 测试音频播放...")
            self.audio_interface.play_audio("Dragon机器人语音控制系统已就绪")
            
            # 检测音频设备
            try:
                import sounddevice as sd
                devices = sd.query_devices()
                
                input_count = sum(1 for d in devices if d['max_input_channels'] > 0)
                output_count = sum(1 for d in devices if d['max_output_channels'] > 0)
                
                print(f"✅ 检测到 {input_count} 个输入设备, {output_count} 个输出设备")
                
                if input_count == 0:
                    print("⚠️  未检测到音频输入设备")
                    print("💡 将使用键盘输入模拟语音命令")
                    self.audio_interface.mode = 'mock'
                
            except Exception as e:
                print(f"❌ 音频设备检测失败: {e}")
                
        except Exception as e:
            print(f"❌ 音频测试失败: {e}")
    
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
            self.audio_interface.play_audio("抱歉，没有理解您的指令")
    
    def execute_robot_action(self, action_result):
        """执行机器人动作"""
        action = action_result.get('action')
        params = action_result.get('params', {})
        
        # 更新状态
        self.robot_state['command_count'] += 1
        
        if action == 'move':
            direction = params.get('direction', 'forward')
            speed = params.get('speed', 1.0)
            
            # 模拟移动
            if direction == 'forward':
                self.robot_state['position']['y'] += speed
            elif direction == 'backward':
                self.robot_state['position']['y'] -= speed
            elif direction == 'left':
                self.robot_state['position']['x'] -= speed
            elif direction == 'right':
                self.robot_state['position']['x'] += speed
            
            self.robot_state['status'] = f'移动({direction})'
            
        elif action == 'rotate':
            angle = params.get('angle', 90)
            self.robot_state['orientation'] = (self.robot_state['orientation'] + angle) % 360
            self.robot_state['status'] = f'旋转({angle}°)'
            
        elif action == 'joint':
            joint = params.get('joint', 'unknown')
            action_type = params.get('action', 'move')
            self.robot_state['status'] = f'关节控制({joint}-{action_type})'
            
        elif action == 'stop':
            self.robot_state['status'] = '停止'
        
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
            'speed': f"速度调整到{params.get('level', 1)}级"
        }
        
        return feedback_map.get(action, "收到命令")
    
    def display_robot_status(self):
        """显示机器人状态"""
        print("\n" + "="*40)
        print("🤖 Dragon机器人状态")
        print(f"位置: x={self.robot_state['position']['x']:.1f}, y={self.robot_state['position']['y']:.1f}")
        print(f"朝向: {self.robot_state['orientation']:.1f}°")
        print(f"状态: {self.robot_state['status']}")
        print(f"执行命令数: {self.robot_state['command_count']}")
        print("="*40)
    
    def show_commands_help(self):
        """显示命令帮助"""
        print("\n🎤 支持的语音命令:")
        print("🚶 移动命令: 前进、后退、向左、向右")
        print("🔄 旋转命令: 转身、左转、右转")
        print("🤲 关节控制: 抬起左手、放下右手、抬起左腿、放下右腿")
        print("⚡ 控制命令: 停止、快一点、慢一点、蹲下、站起")
        print("🎯 示例: '前进'、'抬起左手'、'转身'、'停止'")
    
    def start_voice_control(self):
        """启动语音控制"""
        self.robot_state['running'] = True
        
        print("\n🎮 Dragon机器人WSLg语音控制已启动！")
        self.show_commands_help()
        print("\n🎤 开始语音控制...")
        print("⌨️  按 Ctrl+C 退出")
        
        if self.audio_interface.mode == 'mock':
            print("\n📝 当前使用模拟模式 - 请输入语音命令:")
        else:
            print("\n🎤 正在监听您的语音命令...")
        
        try:
            # 开始录音
            self.audio_interface.start_recording()
            
            # 保持运行
            while self.robot_state['running']:
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n\n🛑 正在停止语音控制...")
        finally:
            self.stop_voice_control()
    
    def stop_voice_control(self):
        """停止语音控制"""
        self.robot_state['running'] = False
        
        if self.audio_interface:
            self.audio_interface.stop_recording()
        
        print("👋 Dragon机器人语音控制已停止")
        self.display_robot_status()


def main():
    """主函数"""
    try:
        # 创建控制器
        controller = DragonWSLGDirectController()
        
        # 启动语音控制
        controller.start_voice_control()
        
    except Exception as e:
        print(f"❌ 程序启动失败: {e}")
        print("\n💡 可能的解决方案:")
        print("  1. 检查WSLg环境是否正确配置")
        print("  2. 运行音频诊断: python3 wsl2_audio_diagnostic.py")
        print("  3. 尝试模式切换器: python3 dragon_mode_switcher.py")


if __name__ == "__main__":
    main()
