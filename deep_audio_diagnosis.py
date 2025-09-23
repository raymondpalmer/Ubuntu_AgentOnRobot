#!/usr/bin/env python3
"""
深度音频诊断工具
专门解决WSL音频噪音问题
"""
import subprocess
import time
import wave
import tempfile
import os

def test_audio_formats():
    """测试不同的音频格式"""
    print("🔧 测试不同音频格式...")
    
    # 生成测试音频数据 (1秒440Hz正弦波)
    import math
    sample_rates = [16000, 22050, 44100, 48000]
    
    for sample_rate in sample_rates:
        print(f"\n🎵 测试 {sample_rate}Hz...")
        
        # 生成正弦波
        duration = 1
        frames = []
        for i in range(sample_rate * duration):
            value = int(16384 * math.sin(2 * math.pi * 440 * i / sample_rate))
            frames.append(value.to_bytes(2, byteorder='little', signed=True))
        
        audio_data = b''.join(frames)
        
        # 创建WAV文件
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
            tmp_filename = tmp_file.name
        
        try:
            with wave.open(tmp_filename, 'wb') as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(audio_data)
            
            print(f"  🔊 播放 {sample_rate}Hz WAV文件...")
            result = subprocess.run([
                'paplay', '--device=RDPSink', tmp_filename
            ], capture_output=True, timeout=3)
            
            if result.returncode == 0:
                print(f"  ✅ {sample_rate}Hz 播放成功")
            else:
                print(f"  ❌ {sample_rate}Hz 播放失败: {result.stderr.decode()}")
                
            # 测试原始PCM播放
            print(f"  🔊 播放 {sample_rate}Hz 原始PCM...")
            result = subprocess.run([
                'paplay', 
                '--device=RDPSink',
                '--format=s16le',
                '--rate={}'.format(sample_rate),
                '--channels=1',
                '--raw'
            ], input=audio_data, capture_output=True, timeout=3)
            
            if result.returncode == 0:
                print(f"  ✅ {sample_rate}Hz PCM播放成功")
            else:
                print(f"  ❌ {sample_rate}Hz PCM播放失败: {result.stderr.decode()}")
            
            os.unlink(tmp_filename)
            
        except Exception as e:
            print(f"  ❌ {sample_rate}Hz 测试失败: {e}")

def check_windows_audio():
    """检查Windows音频设置"""
    print("\n🖥️ Windows音频诊断建议:")
    print("1. 检查Windows声音设置中的默认播放设备")
    print("2. 确保外接音频设备在Windows中被识别")
    print("3. 尝试在Windows中播放音频确认设备工作")
    print("4. 检查外接设备的驱动程序是否正常")
    print("5. 尝试重新插拔外接音频设备")

def test_pulseaudio_config():
    """测试PulseAudio配置"""
    print("\n🔧 PulseAudio配置诊断...")
    
    try:
        # 检查PulseAudio服务器信息
        result = subprocess.run(['pactl', 'info'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ PulseAudio服务正常")
            for line in result.stdout.split('\n'):
                if 'Server String' in line or 'Default Sink' in line or 'Default Source' in line:
                    print(f"  {line}")
        else:
            print("❌ PulseAudio服务异常")
            
        # 检查音频设备状态
        result = subprocess.run(['pactl', 'list', 'sinks', 'short'], capture_output=True, text=True)
        if result.returncode == 0:
            print("\n🔊 音频输出设备:")
            for line in result.stdout.strip().split('\n'):
                if line:
                    print(f"  {line}")
                    if 'SUSPENDED' in line:
                        print("  ⚠️ 设备处于挂起状态")
        
    except Exception as e:
        print(f"❌ PulseAudio诊断失败: {e}")

if __name__ == "__main__":
    print("🔍 深度音频诊断开始...")
    test_pulseaudio_config()
    test_audio_formats()
    check_windows_audio()
    print("\n🔍 诊断完成")