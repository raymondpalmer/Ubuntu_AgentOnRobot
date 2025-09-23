#!/usr/bin/env python3
"""
WSL2环境音频接口
支持模拟音频输入/输出，用于在WSL2环境下开发和测试语音控制系统
"""

import os
import sys
import time
import threading
import subprocess
import tempfile
import wave
import asyncio
import base64
from typing import Callable, List, Optional

class WSL2AudioInterface:
    """WSL2环境下的音频接口"""
    
    def __init__(self, mode='mock'):
        """
        初始化音频接口
        
        Args:
            mode: 'mock' - 模拟模式, 'wslg' - WSLg模式, 'virtual' - 虚拟设备模式
        """
        self.mode = mode
        self.recording = False
        self.playing = False
        self.record_thread = None
        self.audio_callback = None
        
        # 模拟语音命令列表
        self.mock_commands = [
            "前进", "后退", "向左", "向右", "停止",
            "抬起左手", "放下左手", "抬起右手", "放下右手",
            "向前走", "向后走", "转身", "蹲下", "站起"
        ]
        self.mock_index = 0
        
        self._initialize_audio()
    
    def _initialize_audio(self):
        """初始化音频系统"""
        if self.mode == 'wslg':
            self._setup_wslg_audio()
        elif self.mode == 'virtual':
            self._setup_virtual_audio()
        elif self.mode == 'mock':
            print("使用模拟音频模式")
        else:
            raise ValueError(f"不支持的音频模式: {self.mode}")
    
    def _setup_wslg_audio(self):
        """设置WSLg音频"""
        try:
            # 检查WSLg PulseAudio服务器
            pulse_server = "/mnt/wslg/PulseServer"
            if not os.path.exists(pulse_server):
                print("WSLg PulseAudio服务器不可用，切换到模拟模式")
                self.mode = 'mock'
                return
            
            # 创建PulseAudio客户端配置
            config_dir = os.path.expanduser("~/.config/pulse")
            os.makedirs(config_dir, exist_ok=True)
            
            config_content = f"default-server = unix:{pulse_server}\n"
            with open(os.path.join(config_dir, "client.conf"), "w") as f:
                f.write(config_content)
            
            print("WSLg音频配置完成")
            
        except Exception as e:
            print(f"WSLg音频设置失败: {e}")
            print("切换到模拟模式")
            self.mode = 'mock'
    
    def _setup_virtual_audio(self):
        """设置虚拟音频设备"""
        try:
            # 启动PulseAudio
            subprocess.run(['pulseaudio', '--start'], 
                         capture_output=True, check=False)
            
            # 创建虚拟音频设备
            commands = [
                ['pactl', 'load-module', 'module-null-sink', 
                 'sink_name=virtual_speaker', 
                 'sink_properties=device.description="Virtual_Speaker"'],
                ['pactl', 'load-module', 'module-virtual-source', 
                 'source_name=virtual_mic', 
                 'master=virtual_speaker.monitor',
                 'source_properties=device.description="Virtual_Microphone"'],
                ['pactl', 'set-default-sink', 'virtual_speaker'],
                ['pactl', 'set-default-source', 'virtual_mic']
            ]
            
            for cmd in commands:
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    print(f"命令执行失败: {' '.join(cmd)}")
                    print(f"错误: {result.stderr}")
            
            print("虚拟音频设备配置完成")
            
        except Exception as e:
            print(f"虚拟音频设置失败: {e}")
            print("切换到模拟模式")
            self.mode = 'mock'
    
    def set_audio_callback(self, callback: Callable[[str], None]):
        """设置音频回调函数"""
        self.audio_callback = callback
    
    def start_recording(self):
        """开始录音"""
        if self.recording:
            return
        
        self.recording = True
        
        if self.mode == 'mock':
            self.record_thread = threading.Thread(target=self._mock_recording)
        else:
            self.record_thread = threading.Thread(target=self._real_recording)
        
        self.record_thread.start()
        print("开始录音...")
    
    def stop_recording(self):
        """停止录音"""
        if not self.recording:
            return
        
        self.recording = False
        if self.record_thread and self.record_thread.is_alive():
            self.record_thread.join()
        
        print("停止录音")
    
    def _mock_recording(self):
        """模拟录音过程"""
        print("按 Enter 键模拟语音输入，输入 'quit' 退出")
        
        while self.recording:
            try:
                # 等待用户输入
                user_input = input("模拟语音命令 (或按Enter使用默认): ").strip()
                
                if not self.recording:
                    break
                
                if user_input.lower() == 'quit':
                    break
                
                # 如果没有输入，使用预设命令
                if not user_input:
                    command = self.mock_commands[self.mock_index % len(self.mock_commands)]
                    self.mock_index += 1
                else:
                    command = user_input
                
                print(f"识别到语音命令: {command}")
                
                # 调用回调函数
                if self.audio_callback:
                    self.audio_callback(command)
                
            except EOFError:
                break
            except KeyboardInterrupt:
                break
    
    def _real_recording(self):
        """真实录音过程（WSLg或虚拟设备）"""
        try:
            import sounddevice as sd
            import numpy as np
            
            # 检查音频设备
            devices = sd.query_devices()
            print(f"🎤 检测到音频设备: {len(devices)} 个")
            
            # 寻找可用的输入设备
            input_device = None
            for i, device in enumerate(devices):
                if device['max_input_channels'] > 0:
                    input_device = i
                    print(f"✅ 使用输入设备: {device['name']}")
                    break
            
            if input_device is None:
                print("❌ 未找到可用的输入设备")
                raise RuntimeError("No input device available")
            
            # 音频参数
            samplerate = 16000
            duration = 3  # 每次录音3秒
            
            while self.recording:
                try:
                    # 录音
                    print(f"🎤 开始录音 {duration} 秒...")
                    audio_data = sd.rec(int(duration * samplerate), 
                                      samplerate=samplerate, 
                                      channels=1, 
                                      dtype=np.int16,
                                      device=input_device)
                    sd.wait()
                    
                    if not self.recording:
                        break
                    
                    print("✅ 录音完成，正在识别...")
                    
                    # 使用真实的语音识别
                    try:
                        # 保存音频为临时文件进行识别
                        import tempfile
                        import wave
                        
                        # 创建临时wav文件
                        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                            temp_path = temp_file.name
                            
                        # 写入wav文件
                        with wave.open(temp_path, 'wb') as wav_file:
                            wav_file.setnchannels(1)
                            wav_file.setsampwidth(2)  # 16-bit
                            wav_file.setframerate(samplerate)
                            wav_file.writeframes(audio_data.tobytes())
                        
                        # 调用语音识别
                        command = self._recognize_speech(audio_data.tobytes())
                        
                        # 清理临时文件
                        import os
                        try:
                            os.unlink(temp_path)
                        except:
                            pass
                            
                    except Exception as e:
                        print(f"❌ 语音识别失败: {e}")
                        print("🔄 回退到键盘输入模式")
                        command = input("请输入语音命令: ").strip()
                        if not command:
                            continue
                    
                    print(f"识别到语音命令: {command}")
                    
                    if self.audio_callback:
                        self.audio_callback(command)
                        
                except sd.PortAudioError as e:
                    print(f"❌ PortAudio错误: {e}")
                    print("🔄 回退到模拟模式")
                    self._mock_recording()
                    break
                except Exception as e:
                    print(f"❌ 录音过程错误: {e}")
                    time.sleep(1)  # 短暂等待后重试
                
        except ImportError:
            print("❌ SoundDevice库未安装，切换到模拟模式")
            self._mock_recording()
        except Exception as e:
            print(f"❌ 音频初始化失败: {e}")
            print("🔄 自动切换到模拟模式")
            self.mode = 'mock'
            self._mock_recording()
    
    def play_audio(self, text: str):
        """播放音频"""
        if self.playing:
            return
        
        self.playing = True
        
        try:
            if self.mode == 'mock':
                print(f"🔊 TTS播放（模拟）: {text}")
                time.sleep(1)  # 模拟播放时间
            else:
                # 尝试使用真实TTS
                self._real_tts_play(text)
        
        except Exception as e:
            print(f"音频播放失败: {e}")
            print(f"🔊 TTS播放（模拟）: {text}")
        
        finally:
            self.playing = False
    
    def _real_tts_play(self, text: str):
        """真实TTS播放"""
        # 这里可以集成真实的TTS服务
        # 暂时使用模拟
        print(f"🔊 TTS播放: {text}")
        time.sleep(len(text) * 0.1)  # 根据文本长度模拟播放时间
    
    def _recognize_speech(self, audio_bytes: bytes) -> str:
        """语音识别方法"""
        try:
            # 首先尝试使用项目中的ASR模块
            from utils.asr import transcribe_once, ASRResult
            
            # 检查是否配置了ASR服务
            asr_url = os.getenv("ASR_WS_URL", "")
            if asr_url:
                print("🌐 使用云端语音识别...")
                result = transcribe_once()
                return result.text
            
        except ImportError:
            pass
        except Exception as e:
            print(f"⚠️ 云端语音识别失败: {e}")
        
        # 尝试使用本地语音识别
        try:
            import speech_recognition as sr
            import io
            import wave
            
            print("🎤 使用本地语音识别...")
            
            # 创建语音识别器
            r = sr.Recognizer()
            
            # 将音频数据转换为AudioFile格式
            # 创建内存中的wav文件
            audio_buffer = io.BytesIO()
            with wave.open(audio_buffer, 'wb') as wav_file:
                wav_file.setnchannels(1)  # 单声道
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(16000)  # 16kHz
                wav_file.writeframes(audio_bytes)
            
            audio_buffer.seek(0)
            
            # 使用speech_recognition识别
            with sr.AudioFile(audio_buffer) as source:
                audio = r.record(source)
                
            # 尝试Google的免费语音识别服务
            try:
                text = r.recognize_google(audio, language='zh-CN')
                print(f"✅ 识别结果: {text}")
                return text
            except sr.UnknownValueError:
                print("⚠️ 无法识别语音内容")
                return self._keyboard_input_fallback()
            except sr.RequestError as e:
                print(f"⚠️ Google语音识别服务错误: {e}")
                return self._keyboard_input_fallback()
                
        except ImportError:
            print("⚠️ SpeechRecognition库不可用，使用键盘输入模式")
            return self._keyboard_input_fallback()
        except Exception as e:
            print(f"⚠️ 本地语音识别失败: {e}")
            return self._keyboard_input_fallback()
    
    def _keyboard_input_fallback(self) -> str:
        """键盘输入回退模式"""
        print("🎤 请说出你的语音命令，然后按Enter...")
        print("💡 支持命令: 前进、后退、向左、向右、转身、抬起左手、放下右手、停止等")
        
        try:
            command = input("语音命令> ").strip()
            if command:
                return command
            else:
                # 如果没有输入，返回一个默认命令
                return "继续"
        except (EOFError, KeyboardInterrupt):
            return "停止"
    
    def is_recording(self) -> bool:
        """检查是否正在录音"""
        return self.recording
    
    def is_playing(self) -> bool:
        """检查是否正在播放"""
        return self.playing
    
    def get_available_modes(self) -> list:
        """获取可用的音频模式"""
        modes = ['mock']
        
        # 检查WSLg支持
        if os.path.exists('/mnt/wslg/PulseServer'):
            modes.append('wslg')
        
        # 检查PulseAudio
        try:
            result = subprocess.run(['which', 'pulseaudio'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                modes.append('virtual')
        except:
            pass
        
        return modes
    
    def test_audio(self):
        """测试音频系统"""
        print(f"🔧 当前音频模式: {self.mode}")
        print("📋 可用模式:", self.get_available_modes())
        
        # 测试播放
        print("🔊 测试音频播放...")
        self.play_audio("音频系统测试")
        
        if self.mode == 'mock':
            print("📝 模拟模式：使用键盘输入测试录音")
            print("测试录音（5秒）...")
            self.start_recording()
            time.sleep(5)
            self.stop_recording()
        else:
            # 测试真实音频设备
            try:
                import sounddevice as sd
                
                print("🎤 检测音频设备...")
                devices = sd.query_devices()
                
                input_devices = []
                output_devices = []
                
                for i, device in enumerate(devices):
                    if device['max_input_channels'] > 0:
                        input_devices.append((i, device))
                    if device['max_output_channels'] > 0:
                        output_devices.append((i, device))
                
                print(f"✅ 找到 {len(input_devices)} 个输入设备")
                print(f"✅ 找到 {len(output_devices)} 个输出设备")
                
                if input_devices:
                    print("🎤 输入设备列表:")
                    for i, (idx, device) in enumerate(input_devices[:3]):  # 只显示前3个
                        print(f"  {i+1}. {device['name']} (通道: {device['max_input_channels']})")
                
                if output_devices:
                    print("🔊 输出设备列表:")
                    for i, (idx, device) in enumerate(output_devices[:3]):  # 只显示前3个
                        print(f"  {i+1}. {device['name']} (通道: {device['max_output_channels']})")
                
                if input_devices and output_devices:
                    print("✅ 音频设备配置正常")
                    choice = input("是否测试录音功能? (y/n): ").strip().lower()
                    if choice == 'y':
                        print("测试录音（5秒）...")
                        self.start_recording()
                        time.sleep(5)
                        self.stop_recording()
                else:
                    print("⚠️  音频设备不完整，建议使用模拟模式")
                    
            except ImportError:
                print("❌ SoundDevice库未安装")
                print("💡 安装建议: pip install sounddevice")
            except Exception as e:
                print(f"❌ 音频设备检测失败: {e}")
                print("🔄 建议切换到模拟模式")


# 示例用法
def audio_command_handler(command: str):
    """处理音频命令的示例函数"""
    print(f"处理语音命令: {command}")
    
    # 这里可以集成到Dragon机器人控制系统
    # from dragon_voice_processor import DragonVoiceProcessor
    # processor = DragonVoiceProcessor()
    # key_action = processor.parse_voice_command(command)
    # print(f"转换为按键动作: {key_action}")


def main():
    """主函数"""
    print("WSL2音频接口测试")
    print("=" * 40)
    
    # 检测最佳音频模式
    interface = WSL2AudioInterface()
    available_modes = interface.get_available_modes()
    
    print(f"检测到可用模式: {available_modes}")
    
    # 如果有多个模式可选，让用户选择
    if len(available_modes) > 1:
        print("请选择音频模式:")
        for i, mode in enumerate(available_modes):
            print(f"  {i+1}. {mode}")
        
        try:
            choice = int(input("输入选择 (1-{}): ".format(len(available_modes))))
            if 1 <= choice <= len(available_modes):
                selected_mode = available_modes[choice-1]
                interface = WSL2AudioInterface(mode=selected_mode)
        except:
            print("使用默认模式")
    
    # 设置命令处理回调
    interface.set_audio_callback(audio_command_handler)
    
    # 测试音频系统
    interface.test_audio()
    
    print("\n音频接口已准备就绪")
    print("可以开始语音控制测试")


if __name__ == "__main__":
    main()
