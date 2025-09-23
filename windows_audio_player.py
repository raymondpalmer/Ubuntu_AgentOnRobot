#!/usr/bin/env python3
"""
WSL2环境专用音频播放解决方案
通过Windows PowerShell调用Windows音频API
"""
import subprocess
import tempfile
import wave
import os

def play_audio_via_windows(audio_data):
    """通过Windows PowerShell播放音频"""
    try:
        # 创建临时WAV文件
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
            tmp_filename = tmp_file.name
        
        # 写入WAV格式
        with wave.open(tmp_filename, 'wb') as wav_file:
            wav_file.setnchannels(1)        # 单声道
            wav_file.setsampwidth(2)        # 16-bit
            wav_file.setframerate(24000)    # 24kHz
            wav_file.writeframes(audio_data)
        
        # 转换为Windows路径
        windows_path = subprocess.check_output([
            'wslpath', '-w', tmp_filename
        ]).decode().strip()
        
        print(f"🎵 通过Windows播放: {windows_path}")
        
        # 使用PowerShell播放音频
        powershell_script = f'''
Add-Type -AssemblyName presentationCore
$mediaPlayer = New-Object system.windows.media.mediaplayer
$mediaPlayer.open([uri]"{windows_path}")
$mediaPlayer.Play()
Start-Sleep -Seconds 3
$mediaPlayer.Stop()
$mediaPlayer.Close()
'''
        
        result = subprocess.run([
            'powershell.exe', '-Command', powershell_script
        ], capture_output=True, text=True, timeout=10)
        
        # 清理临时文件
        try:
            os.unlink(tmp_filename)
        except:
            pass
        
        if result.returncode == 0:
            print("✅ Windows音频播放成功")
            return True
        else:
            print(f"❌ Windows播放失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Windows音频播放异常: {e}")
        return False

def play_audio_via_windows_simple(audio_data):
    """简化的Windows播放方案"""
    try:
        # 在Windows临时目录创建文件
        temp_dir = '/mnt/c/Windows/Temp'
        if not os.path.exists(temp_dir):
            temp_dir = '/tmp'
        
        wav_file = os.path.join(temp_dir, 'wsl_audio.wav')
        
        # 写入WAV格式
        with wave.open(wav_file, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(24000)
            wf.writeframes(audio_data)
        
        print(f"🎵 播放文件: {wav_file}")
        
        # 使用Windows的start命令播放
        if wav_file.startswith('/mnt/c/'):
            windows_path = wav_file.replace('/mnt/c/', 'C:\\').replace('/', '\\')
            result = subprocess.run([
                'cmd.exe', '/c', 'start', '/min', windows_path
            ], capture_output=True, timeout=5)
        else:
            # 如果不在Windows分区，使用aplay
            result = subprocess.run([
                'aplay', wav_file
            ], capture_output=True, timeout=5)
        
        if result.returncode == 0:
            print("✅ 音频播放启动成功")
            return True
        else:
            print(f"⚠️ 播放启动: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 简化播放失败: {e}")
        return False

def test_audio_methods():
    """测试不同的音频播放方法"""
    import struct
    import math
    
    # 生成测试音频
    sample_rate = 24000
    duration = 2
    frequency = 440
    
    frames = []
    for i in range(sample_rate * duration):
        value = int(16384 * math.sin(2 * math.pi * frequency * i / sample_rate))
        frames.append(struct.pack('<h', value))
    
    audio_data = b''.join(frames)
    print(f"📊 生成测试音频: {len(audio_data)} 字节")
    
    print("\n🔄 测试Windows PowerShell播放...")
    play_audio_via_windows(audio_data)
    
    print("\n🔄 测试简化Windows播放...")
    play_audio_via_windows_simple(audio_data)

if __name__ == "__main__":
    print("🎧 WSL2 Windows音频播放测试")
    print("=" * 40)
    test_audio_methods()