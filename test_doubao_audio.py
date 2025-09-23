#!/usr/bin/env python3
"""
豆包API音频格式验证工具
测试16kHz输入和24kHz输出是否正常工作
"""

import subprocess
import sys
import time
import os
import wave
import struct
import math

def test_doubao_input_format():
    """测试豆包输入格式 (16kHz单声道)"""
    print("🎤 测试豆包输入格式 (16kHz单声道)...")
    
    try:
        # 录制16kHz单声道音频（豆包标准）
        print("📢 请说话（录音3秒，16kHz格式）...")
        
        process = subprocess.Popen([
            'parecord', 
            '--device=RDPSource',
            '--format=s16le', 
            '--rate=16000',      # 豆包要求16kHz
            '--channels=1',      # 豆包要求单声道
            '/tmp/doubao_input_test.wav'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        time.sleep(3)
        process.terminate()
        process.wait()
        
        if os.path.exists('/tmp/doubao_input_test.wav'):
            size = os.path.getsize('/tmp/doubao_input_test.wav')
            print(f"✅ 16kHz输入录制成功: {size} 字节")
            
            # 播放录制的音频
            print("🔄 播放16kHz录音...")
            subprocess.run(['paplay', '/tmp/doubao_input_test.wav'], 
                         capture_output=True, timeout=5)
            return True
        else:
            print("❌ 16kHz录音失败")
            return False
            
    except Exception as e:
        print(f"❌ 16kHz录音测试失败: {e}")
        return False

def generate_doubao_output_test():
    """生成豆包输出格式测试音频 (24kHz单声道)"""
    print("🔊 生成豆包输出格式测试音频 (24kHz单声道)...")
    
    try:
        # 生成24kHz单声道测试音频
        sample_rate = 24000  # 豆包TTS输出标准
        duration = 2
        frequency = 880  # A5音调
        
        frames = []
        for i in range(int(sample_rate * duration)):
            value = int(16384 * math.sin(2 * math.pi * frequency * i / sample_rate))
            frames.append(struct.pack('<h', value))
        
        # 写入24kHz WAV文件
        with wave.open('/tmp/doubao_output_test.wav', 'wb') as wf:
            wf.setnchannels(1)      # 豆包TTS单声道
            wf.setsampwidth(2)      # 16-bit
            wf.setframerate(24000)  # 豆包TTS 24kHz
            wf.writeframes(b''.join(frames))
        
        print("✅ 24kHz测试音频生成成功")
        return True
        
    except Exception as e:
        print(f"❌ 24kHz测试音频生成失败: {e}")
        return False

def test_doubao_output_format():
    """测试豆包输出格式播放 (24kHz单声道)"""
    print("🎵 测试豆包输出格式播放 (24kHz单声道)...")
    
    try:
        # 播放24kHz单声道音频（模拟豆包TTS）
        result = subprocess.run([
            'paplay', 
            '--device=RDPSink',
            '--rate=24000',      # 豆包TTS输出标准
            '--channels=1',      # 豆包TTS单声道
            '/tmp/doubao_output_test.wav'
        ], capture_output=True, timeout=5)
        
        if result.returncode == 0:
            print("✅ 24kHz输出播放成功")
            print("❓ 您听到880Hz音调了吗？(豆包TTS格式测试)")
            return True
        else:
            print(f"❌ 24kHz播放失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 24kHz播放测试失败: {e}")
        return False

def check_audio_format_compatibility():
    """检查音频格式兼容性"""
    print("\n🔍 豆包API音频格式要求:")
    print("=" * 50)
    print("📥 输入 (ASR): 16kHz, 单声道, PCM")
    print("📤 输出 (TTS): 24kHz, 单声道, PCM") 
    print("🎯 这是豆包API的严格要求，不能更改")
    print("")
    
    # 检查当前设备支持
    print("🔧 检查当前设备支持...")
    
    # 检查输入设备
    result = subprocess.run(['pactl', 'list', 'sources', 'short'], 
                          capture_output=True, text=True)
    if 'RDPSource' in result.stdout:
        print("✅ 输入设备 RDPSource 可用")
    else:
        print("❌ 输入设备 RDPSource 不可用")
    
    # 检查输出设备  
    result = subprocess.run(['pactl', 'list', 'sinks', 'short'], 
                          capture_output=True, text=True)
    if 'RDPSink' in result.stdout:
        print("✅ 输出设备 RDPSink 可用")
    else:
        print("❌ 输出设备 RDPSink 不可用")

def main():
    """主函数"""
    print("🔊 豆包API音频格式验证工具")
    print("=" * 50)
    
    # 设置环境
    os.environ['PULSE_SERVER'] = 'unix:/mnt/wslg/PulseServer'
    
    # 激活设备
    subprocess.run(['pactl', 'set-sink-mute', 'RDPSink', 'false'], 
                  capture_output=True)
    subprocess.run(['pactl', 'set-source-mute', 'RDPSource', 'false'], 
                  capture_output=True)
    
    # 检查格式兼容性
    check_audio_format_compatibility()
    
    # 测试输入格式 (16kHz)
    input_ok = test_doubao_input_format()
    
    # 生成和测试输出格式 (24kHz)
    if generate_doubao_output_test():
        output_ok = test_doubao_output_format()
    else:
        output_ok = False
    
    # 结果
    print("\n" + "=" * 50)
    print("📊 豆包API格式测试结果:")
    print(f"🎤 16kHz输入: {'✅ 正常' if input_ok else '❌ 异常'}")
    print(f"🔊 24kHz输出: {'✅ 正常' if output_ok else '❌ 异常'}")
    
    if input_ok and output_ok:
        print("\n🎉 豆包API音频格式完全兼容！")
        print("💡 可以正常使用Dragon机器人语音功能")
    else:
        print("\n⚠️ 音频格式存在问题")
        print("💡 建议检查:")
        print("   - Windows默认设备设置")
        print("   - WSL音频驱动")
        print("   - PulseAudio配置")

if __name__ == "__main__":
    main()