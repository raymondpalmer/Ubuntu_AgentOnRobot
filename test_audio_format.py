#!/usr/bin/env python3
"""
测试豆包音频数据格式
"""
import wave
import tempfile
import subprocess
import os

def test_wav_creation():
    """测试WAV文件创建"""
    print("🔧 测试WAV文件创建...")
    
    # 创建一个简单的音频数据（1秒静音）
    sample_rate = 24000
    duration = 1
    silence_data = b'\x00\x00' * (sample_rate * duration)  # 16-bit静音
    
    # 创建WAV文件
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
        tmp_filename = tmp_file.name
    
    try:
        with wave.open(tmp_filename, 'wb') as wav_file:
            wav_file.setnchannels(1)        # 单声道
            wav_file.setsampwidth(2)        # 16-bit = 2字节
            wav_file.setframerate(24000)    # 24kHz
            wav_file.writeframes(silence_data)
        
        print(f"✅ WAV文件创建成功: {tmp_filename}")
        
        # 获取文件信息
        file_size = os.path.getsize(tmp_filename)
        print(f"📁 文件大小: {file_size} 字节")
        
        # 尝试播放
        print("🎵 测试播放WAV文件...")
        result = subprocess.run([
            'paplay', 
            '--device=RDPSink',
            tmp_filename
        ], capture_output=True, timeout=3)
        
        if result.returncode == 0:
            print("✅ WAV播放成功")
        else:
            print(f"❌ WAV播放失败: {result.stderr}")
            
        # 清理
        os.unlink(tmp_filename)
        
    except Exception as e:
        print(f"❌ WAV测试失败: {e}")

if __name__ == "__main__":
    test_wav_creation()