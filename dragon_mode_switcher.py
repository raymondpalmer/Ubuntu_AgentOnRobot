#!/usr/bin/env python3
"""
Dragon机器人音频模式切换器
支持在不同音频模式间动态切换
"""

import os
import sys
import time
import subprocess
from typing import Dict, Any

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from wsl2_audio_interface import WSL2AudioInterface
    from simple_voice_processor import DragonVoiceProcessor
except ImportError as e:
    print(f"❌ 导入模块失败: {e}")
    print("请确保在正确的目录中运行此脚本")
    sys.exit(1)

class DragonModeSwitcher:
    """Dragon机器人音频模式切换器"""
    
    def __init__(self):
        """初始化模式切换器"""
        self.current_mode = 'mock'
        self.audio_interface = None
        self.voice_processor = None
        self.robot_state = {
            'position': {'x': 0.0, 'y': 0.0},
            'orientation': 0.0,
            'status': '待命',
            'command_count': 0
        }
        
        print("🔧 Dragon机器人音频模式切换器")
        print("=" * 50)
        
        # 检测最佳可用模式
        self.current_mode = self._detect_best_mode()
        print(f"🎯 自动选择最佳模式: {self.current_mode}")
        
        self._initialize_components()
    
    def _detect_best_mode(self) -> str:
        """检测最佳可用模式"""
        # 优先级: wslg > virtual > mock
        
        # 检查WSLg
        available, message = self.check_mode_availability('wslg')
        if available:
            print(f"✅ WSLg模式可用: {message}")
            return 'wslg'
        
        # 检查Virtual
        available, message = self.check_mode_availability('virtual')
        if available:
            print(f"✅ 虚拟模式可用: {message}")
            return 'virtual'
        
        # 默认Mock
        print("📝 使用模拟模式作为默认")
        return 'mock'
    
    def _initialize_components(self):
        """初始化音频组件"""
        try:
            self.audio_interface = WSL2AudioInterface(mode=self.current_mode)
            self.voice_processor = DragonVoiceProcessor()
            print(f"✅ 初始化完成，当前模式: {self.current_mode}")
        except Exception as e:
            print(f"❌ 初始化失败: {e}")
    
    def get_available_modes(self) -> Dict[str, str]:
        """获取可用音频模式"""
        modes = {
            'mock': '模拟音频模式 (键盘输入模拟语音)',
            'wslg': 'WSLg音频模式 (真实语音，需要Windows 11)',
            'virtual': '虚拟音频设备模式 (用于测试)'
        }
        return modes
    
    def check_mode_availability(self, mode: str) -> tuple:
        """检查模式可用性"""
        if mode == 'mock':
            return True, "模拟模式始终可用"
        
        elif mode == 'wslg':
            # 检查WSLg环境
            try:
                # 检查是否在WSL环境
                with open('/proc/version', 'r') as f:
                    if 'microsoft' not in f.read().lower():
                        return False, "不是WSL环境"
                
                # 检查WSLg相关文件
                wslg_indicators = [
                    '/mnt/wslg',
                    '/mnt/wslg/PulseServer'
                ]
                
                for indicator in wslg_indicators:
                    if os.path.exists(indicator):
                        return True, "WSLg环境可用"
                
                return False, "WSLg环境不可用，但可以尝试"
                
            except Exception as e:
                return False, f"WSLg检查失败: {e}"
        
        elif mode == 'virtual':
            # 检查PulseAudio
            try:
                result = subprocess.run(['which', 'pulseaudio'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    return True, "PulseAudio可用"
                else:
                    return False, "PulseAudio未安装"
            except Exception as e:
                return False, f"虚拟模式检查失败: {e}"
        
        return False, "未知模式"
    
    def switch_mode(self, new_mode: str) -> bool:
        """切换音频模式"""
        if new_mode not in self.get_available_modes():
            print(f"❌ 无效模式: {new_mode}")
            return False
        
        if new_mode == self.current_mode:
            print(f"ℹ️  已经是 {new_mode} 模式")
            return True
        
        # 检查目标模式可用性
        available, message = self.check_mode_availability(new_mode)
        print(f"🔍 模式检查: {message}")
        
        if not available:
            choice = input(f"⚠️  {new_mode} 模式可能不可用，是否继续尝试? (y/n): ").strip().lower()
            if choice != 'y':
                return False
        
        print(f"🔄 切换模式: {self.current_mode} → {new_mode}")
        
        try:
            # 停止当前音频接口
            if self.audio_interface and hasattr(self.audio_interface, 'stop_recording'):
                self.audio_interface.stop_recording()
            
            # 创建新的音频接口
            old_mode = self.current_mode
            self.current_mode = new_mode
            self.audio_interface = WSL2AudioInterface(mode=new_mode)
            
            print(f"✅ 成功切换到 {new_mode} 模式")
            return True
            
        except Exception as e:
            print(f"❌ 切换失败: {e}")
            # 恢复到原模式
            self.current_mode = old_mode
            try:
                self.audio_interface = WSL2AudioInterface(mode=old_mode)
                print(f"🔄 已恢复到 {old_mode} 模式")
            except:
                print("❌ 恢复原模式也失败了")
            return False
    
    def test_current_mode(self):
        """测试当前音频模式"""
        print(f"\n🧪 测试 {self.current_mode} 模式...")
        
        try:
            if self.current_mode == 'mock':
                print("📝 模拟模式测试:")
                print("  - 输入模拟语音命令")
                test_input = input("请输入测试命令: ").strip()
                if test_input:
                    print(f"🔊 模拟TTS播放: 收到命令 '{test_input}'")
                    
                    # 测试语音处理
                    result = self.voice_processor.parse_voice_command(test_input)
                    if result:
                        print(f"🎯 命令解析结果: {result}")
                    else:
                        print("❓ 未识别的命令")
                else:
                    print("🔊 模拟TTS播放: 测试音频播放功能")
                
            elif self.current_mode == 'wslg':
                print("🎤 WSLg模式测试:")
                print("  正在测试真实音频设备...")
                
                # 测试音频播放
                print("🔊 测试音频播放...")
                self.audio_interface.play_audio("WSLg音频测试")
                
                # 提示录音测试
                print("🎤 准备测试录音 (3秒)...")
                input("按Enter开始录音测试...")
                
                try:
                    self.audio_interface.start_recording()
                    print("🎤 正在录音... (请说话)")
                    time.sleep(3)
                    self.audio_interface.stop_recording()
                    print("✅ 录音测试完成")
                except Exception as e:
                    print(f"❌ 录音测试失败: {e}")
                
            elif self.current_mode == 'virtual':
                print("🔧 虚拟模式测试:")
                print("  - 检查虚拟音频设备")
                
                try:
                    # 尝试列出音频设备
                    result = subprocess.run(['pactl', 'list', 'short', 'sinks'], 
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        print("✅ 虚拟音频设备可用")
                        print(f"设备列表:\n{result.stdout}")
                    else:
                        print("⚠️  无法列出音频设备")
                        
                    # 测试播放
                    print("🔊 测试虚拟音频播放...")
                    self.audio_interface.play_audio("虚拟音频测试")
                    
                except Exception as e:
                    print(f"❌ 虚拟模式测试失败: {e}")
            
            print("✅ 音频模式测试完成")
            
        except Exception as e:
            print(f"❌ 测试失败: {e}")
    
    def run_voice_demo(self):
        """运行语音控制演示"""
        print(f"\n🎮 启动 {self.current_mode} 模式语音控制演示")
        print("🎤 说出语音命令控制机器人")
        print("⌨️  按 Ctrl+C 停止\n")
        
        try:
            if self.current_mode == 'mock':
                self._run_mock_demo()
            else:
                self._run_real_demo()
                
        except KeyboardInterrupt:
            print("\n👋 演示结束")
        except Exception as e:
            print(f"❌ 演示失败: {e}")
    
    def _run_mock_demo(self):
        """运行模拟模式演示"""
        print("📝 模拟模式 - 请输入语音命令:")
        
        while True:
            try:
                command = input("\n🎤 语音命令 (输入'quit'退出): ").strip()
                
                if command.lower() == 'quit':
                    break
                
                if command:
                    print(f"🎤 收到: '{command}'")
                    self._process_command(command)
                
            except KeyboardInterrupt:
                break
    
    def _run_real_demo(self):
        """运行真实音频模式演示"""
        print(f"🎤 {self.current_mode.upper()}模式 - 真实语音控制")
        
        # 设置音频回调
        self.audio_interface.set_audio_callback(self._process_command)
        
        # 开始录音
        self.audio_interface.start_recording()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            self.audio_interface.stop_recording()
    
    def _process_command(self, command: str):
        """处理语音命令"""
        # 解析命令
        result = self.voice_processor.parse_voice_command(command)
        
        if result:
            print(f"🎯 解析结果: {result}")
            
            # 执行机器人动作
            self._execute_robot_action(result)
            
            # 语音反馈
            feedback = self._generate_feedback(result)
            print(f"🔊 反馈: {feedback}")
            self.audio_interface.play_audio(feedback)
            
        else:
            print("❓ 未识别的命令")
            self.audio_interface.play_audio("抱歉，没有理解您的指令")
    
    def _execute_robot_action(self, action_result: Dict[str, Any]):
        """执行机器人动作"""
        action = action_result.get('action')
        params = action_result.get('params', {})
        
        # 更新机器人状态
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
        self._display_robot_status()
    
    def _generate_feedback(self, action_result: Dict[str, Any]) -> str:
        """生成语音反馈"""
        action = action_result.get('action')
        params = action_result.get('params', {})
        
        feedback_map = {
            'move': f"正在{params.get('direction', '移动')}",
            'rotate': f"正在旋转",
            'joint': f"正在{params.get('action', '移动')}{params.get('joint', '关节')}",
            'stop': "已停止",
            'speed': f"速度调整到{params.get('level', 1)}级"
        }
        
        return feedback_map.get(action, "收到命令")
    
    def _display_robot_status(self):
        """显示机器人状态"""
        print("\n" + "="*40)
        print("🤖 Dragon机器人状态")
        print(f"位置: x={self.robot_state['position']['x']:.1f}, y={self.robot_state['position']['y']:.1f}")
        print(f"朝向: {self.robot_state['orientation']:.1f}°")
        print(f"状态: {self.robot_state['status']}")
        print(f"执行命令数: {self.robot_state['command_count']}")
        print("="*40)
    
    def show_mode_info(self):
        """显示模式信息"""
        print(f"\n📊 当前音频模式: {self.current_mode}")
        
        modes = self.get_available_modes()
        print("\n📋 所有可用模式:")
        
        for mode_key, mode_desc in modes.items():
            available, message = self.check_mode_availability(mode_key)
            status = "✓ 当前" if mode_key == self.current_mode else ("✅ 可用" if available else "❌ 不可用")
            print(f"  {mode_key}: {mode_desc}")
            print(f"    状态: {status} - {message}")
        print()
    
    def interactive_menu(self):
        """交互式菜单"""
        while True:
            print("\n🎵 Dragon机器人音频模式切换器")
            print("=" * 50)
            self.show_mode_info()
            
            print("📋 操作菜单:")
            print("  1. 切换音频模式")
            print("  2. 测试当前模式")
            print("  3. 运行语音控制演示")
            print("  4. 显示模式信息")
            print("  5. 退出")
            
            try:
                choice = input("\n请选择操作 (1-5): ").strip()
                
                if choice == '1':
                    self._handle_mode_switch()
                elif choice == '2':
                    self.test_current_mode()
                elif choice == '3':
                    self.run_voice_demo()
                elif choice == '4':
                    self.show_mode_info()
                elif choice == '5':
                    print("👋 再见！")
                    break
                else:
                    print("❌ 无效选择，请重试")
                    
            except KeyboardInterrupt:
                print("\n\n👋 程序被中断，再见！")
                break
            except Exception as e:
                print(f"❌ 操作失败: {e}")
    
    def _handle_mode_switch(self):
        """处理模式切换"""
        print("\n🔄 选择新的音频模式:")
        modes = self.get_available_modes()
        
        # 显示模式选项
        mode_list = list(modes.keys())
        for i, (mode_key, mode_desc) in enumerate(modes.items(), 1):
            available, message = self.check_mode_availability(mode_key)
            status = "✓ 当前" if mode_key == self.current_mode else ("✅" if available else "❌")
            print(f"  {i}. {mode_desc} {status}")
        
        try:
            choice = input(f"\n请选择模式 (1-{len(modes)}): ").strip()
            
            if choice.isdigit():
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(mode_list):
                    new_mode = mode_list[choice_idx]
                    self.switch_mode(new_mode)
                else:
                    print("❌ 选择超出范围")
            else:
                print("❌ 请输入数字")
                
        except ValueError:
            print("❌ 无效输入")


def main():
    """主函数"""
    print("🚀 启动Dragon机器人音频模式切换器")
    
    try:
        switcher = DragonModeSwitcher()
        switcher.interactive_menu()
    except Exception as e:
        print(f"❌ 程序启动失败: {e}")
        print("\n💡 可能的解决方案:")
        print("  1. 确保在正确的目录中运行")
        print("  2. 检查所需的模块是否存在")
        print("  3. 查看错误信息进行调试")


if __name__ == "__main__":
    main()
