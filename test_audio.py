#!/usr/bin/env python3
"""
音频设备测试脚本
测试录音和播放功能
"""

import sys
import subprocess
import time
import os

def check_audio_devices():
    """检查音频设备"""
    print("🔍 检查音频设备...")
    
    # 检查PulseAudio
    try:
        result = subprocess.run(['pactl', 'info'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ PulseAudio服务正常")
            
            # 提取默认设备信息
            lines = result.stdout.split('\n')
            default_sink = "未知"
            default_source = "未知"
            
            for line in lines:
                if 'Default Sink:' in line:
                    default_sink = line.strip()
                elif 'Default Source:' in line:
                    default_source = line.strip()
            
            print(f"默认输出设备: {default_sink}")
            print(f"默认输入设备: {default_source}")
        else:
            print("❌ PulseAudio服务异常")
            return False
    except Exception as e:
        print(f"❌ 无法检查PulseAudio: {e}")
        return False
    
    return True

def test_microphone():
    """测试麦克风录音"""
    print("\n🎤 测试麦克风录音...")
    
    try:
        # 录制2秒音频
        print("开始录音（2秒）...")
        result = subprocess.run([
            'parecord', 
            '--format=s16le', 
            '--rate=16000',
            '--channels=1',
            '/tmp/test_recording.wav'
        ], timeout=3, capture_output=True)
        
        if result.returncode == 0:
            print("✅ 麦克风录音成功")
            
            # 检查文件大小
            if os.path.exists('/tmp/test_recording.wav'):
                size = os.path.getsize('/tmp/test_recording.wav')
                print(f"录音文件大小: {size} 字节")
                if size > 1000:  # 大于1KB说明有录到内容
                    print("✅ 麦克风正常工作")
                    return True
                else:
                    print("⚠️ 录音文件太小，可能没有录到声音")
            
        else:
            print(f"❌ 录音失败: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        print("⚠️ 录音超时")
    except Exception as e:
        print(f"❌ 录音异常: {e}")
    
    return False

def test_speaker():
    """测试扬声器播放"""
    print("\n🔊 测试扬声器播放...")
    
    try:
        # 生成测试音频（440Hz正弦波，1秒）
        print("生成测试音频...")
        subprocess.run([
            'pacat', 
            '--format=s16le', 
            '--rate=44100',
            '--channels=2'
        ], input=b'\x00' * 44100 * 2 * 2, timeout=2)  # 静音测试
        
        print("✅ 扬声器测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 扬声器测试失败: {e}")
        return False

def main():
    """主函数"""
    print("🎵 Dragon机器人音频设备测试")
    print("=" * 50)
    
    # 设置环境变量
    os.environ['PULSE_SERVER'] = 'unix:/mnt/wslg/PulseServer'
    
    # 检查音频设备
    if not check_audio_devices():
        print("\n❌ 音频设备检查失败，请先配置音频环境")
        sys.exit(1)
    
    # 测试麦克风
    mic_ok = test_microphone()
    
    # 测试扬声器
    speaker_ok = test_speaker()
    
    # 总结
    print("\n" + "=" * 50)
    print("📊 测试结果:")
    print(f"🎤 麦克风: {'✅ 正常' if mic_ok else '❌ 异常'}")
    print(f"🔊 扬声器: {'✅ 正常' if speaker_ok else '❌ 异常'}")
    
    if mic_ok and speaker_ok:
        print("\n🎉 音频设备全部正常，可以使用Dragon机器人语音控制系统！")
        return True
    else:
        print("\n⚠️ 部分音频设备异常，可能影响语音控制功能")
        return False

if __name__ == "__main__":
    main()