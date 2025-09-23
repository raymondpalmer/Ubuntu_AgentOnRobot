#!/usr/bin/env python3
"""
WSL2环境音频兼容性测试和修复工具
"""
import subprocess
import tempfile
import wave
import struct
import math
import os

def test_wsl_audio_environment():
    """测试WSL2音频环境"""
    print("🔧 WSL2音频环境诊断...")
    
    # 检查WSL版本
    try:
        result = subprocess.run(['wsl.exe', '--version'], capture_output=True, text=True)
        if 'WSL' in result.stdout:
            print("✅ 检测到WSL2环境")
    except:
        print("⚠️ 无法确定WSL版本")
    
    # 检查音频子系统
    try:
        result = subprocess.run(['pulseaudio', '--version'], capture_output=True, text=True)
        print(f"🎵 PulseAudio版本: {result.stdout.strip()}")
    except:
        print("❌ PulseAudio未安装")
    
    # 检查WSLG音频
    wslg_pulse = os.environ.get('PULSE_RUNTIME_PATH')
    if wslg_pulse:
        print(f"🔗 WSLG音频路径: {wslg_pulse}")
    else:
        print("⚠️ 未检测到WSLG音频配置")

def create_wsl_compatible_audio(audio_data, output_file):
    """创建WSL2兼容的音频文件"""
    print(f"🔧 创建WSL2兼容音频文件...")
    
    try:
        # 方法1: 标准WAV格式
        with wave.open(output_file, 'wb') as wav_file:
            wav_file.setnchannels(1)      # 单声道
            wav_file.setsampwidth(2)      # 16-bit
            wav_file.setframerate(24000)  # 24kHz
            wav_file.writeframes(audio_data)
        
        print(f"✅ WAV文件创建成功: {output_file}")
        return True
        
    except Exception as e:
        print(f"❌ WAV创建失败: {e}")
        return False

def test_wsl_audio_formats():
    """测试WSL2音频格式兼容性"""
    print("🎵 测试WSL2音频格式兼容性...")
    
    # 生成测试音频数据
    sample_rate = 24000
    duration = 1  # 1秒
    frequency = 440  # A4音调
    
    # 生成16-bit PCM数据（豆包格式）
    frames = []
    for i in range(sample_rate * duration):
        value = int(16384 * math.sin(2 * math.pi * frequency * i / sample_rate))
        frames.append(struct.pack('<h', value))  # little-endian 16-bit
    
    audio_data = b''.join(frames)
    print(f"📊 生成测试音频: {len(audio_data)} 字节")
    
    # 测试不同的播放方式
    test_methods = [
        ("直接paplay播放", lambda f: ['paplay', f]),
        ("指定RDPSink设备", lambda f: ['paplay', '--device=RDPSink', f]),
        ("强制16位格式", lambda f: ['paplay', '--format=s16le', '--rate=24000', '--channels=1', f]),
        ("使用aplay播放", lambda f: ['aplay', '-D', 'default', f]),
    ]
    
    for method_name, cmd_func in test_methods:
        print(f"\n🔄 测试: {method_name}")
        
        # 创建临时WAV文件
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
            tmp_filename = tmp_file.name
        
        if create_wsl_compatible_audio(audio_data, tmp_filename):
            try:
                cmd = cmd_func(tmp_filename)
                print(f"   命令: {' '.join(cmd)}")
                
                result = subprocess.run(cmd, capture_output=True, timeout=3)
                
                if result.returncode == 0:
                    print(f"   ✅ {method_name} 执行成功")
                else:
                    print(f"   ❌ {method_name} 失败: {result.stderr.decode()}")
                    
            except subprocess.TimeoutExpired:
                print(f"   ⏱️ {method_name} 超时")
            except Exception as e:
                print(f"   ❌ {method_name} 异常: {e}")
        
        # 清理
        try:
            os.unlink(tmp_filename)
        except:
            pass

def fix_wsl_audio_config():
    """修复WSL2音频配置"""
    print("🔧 修复WSL2音频配置...")
    
    try:
        # 重启PulseAudio
        subprocess.run(['pulseaudio', '--kill'], capture_output=True)
        subprocess.run(['pulseaudio', '--start'], capture_output=True)
        print("✅ PulseAudio服务重启")
        
        # 设置默认设备
        subprocess.run(['pactl', 'set-default-sink', 'RDPSink'], capture_output=True)
        subprocess.run(['pactl', 'set-default-source', 'RDPSource'], capture_output=True)
        print("✅ 默认音频设备设置")
        
        # 设置音量
        subprocess.run(['pactl', 'set-sink-volume', 'RDPSink', '100%'], capture_output=True)
        subprocess.run(['pactl', 'set-sink-mute', 'RDPSink', 'false'], capture_output=True)
        print("✅ 音频音量配置")
        
    except Exception as e:
        print(f"⚠️ 配置修复部分失败: {e}")

def main():
    """主函数"""
    print("🎧 WSL2音频兼容性测试工具")
    print("=" * 50)
    
    test_wsl_audio_environment()
    print()
    
    fix_wsl_audio_config()
    print()
    
    test_wsl_audio_formats()
    print()
    
    print("📋 WSL2音频建议:")
    print("1. 确保Windows音频服务正常运行")
    print("2. 在Windows声音设置中设置正确的默认播放设备")
    print("3. 检查外接音频设备是否被Windows正确识别")
    print("4. 尝试在Windows中播放音频确认设备工作")
    print("5. 考虑使用Windows端的音频播放器作为替代方案")

if __name__ == "__main__":
    main()