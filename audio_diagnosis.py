#!/usr/bin/env python3
"""
外接音频设备诊断和修复工具
专门处理WSL环境下的外接声卡和麦克风问题
"""

import subprocess
import sys
import time
import os

def run_command(cmd, description=""):
    """安全执行命令"""
    try:
        if description:
            print(f"🔧 {description}")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def force_activate_audio_devices():
    """强制激活音频设备"""
    print("⚡ 强制激活音频设备...")
    
    # 激活输出设备
    commands = [
        "pactl set-sink-mute RDPSink false",
        "pactl set-sink-volume RDPSink 100%",
        "pactl set-default-sink RDPSink",
        
        # 激活输入设备
        "pactl set-source-mute RDPSource false", 
        "pactl set-source-volume RDPSource 100%",
        "pactl set-default-source RDPSource"
    ]
    
    for cmd in commands:
        success, stdout, stderr = run_command(cmd)
        if not success:
            print(f"⚠️ 命令失败: {cmd}")
        else:
            print(f"✅ {cmd}")

def test_audio_playback():
    """测试音频播放"""
    print("\n🔊 测试音频播放...")
    
    # 生成测试音频 (440Hz正弦波，2秒)
    test_audio_cmd = """
python3 -c "
import math
import wave
import struct

# 生成440Hz正弦波
sample_rate = 44100
duration = 2
frequency = 440

frames = []
for i in range(int(sample_rate * duration)):
    value = int(32767 * math.sin(2 * math.pi * frequency * i / sample_rate))
    frames.append(struct.pack('<h', value))

# 写入WAV文件
with wave.open('/tmp/test_tone.wav', 'wb') as wf:
    wf.setnchannels(1)
    wf.setsampwidth(2) 
    wf.setframerate(sample_rate)
    wf.writeframes(b''.join(frames))
    
print('测试音频文件已生成')
"
"""
    
    success, stdout, stderr = run_command(test_audio_cmd, "生成测试音频")
    if not success:
        print(f"❌ 测试音频生成失败: {stderr}")
        return False
    
    # 播放测试音频
    print("🎵 播放测试音频（2秒440Hz音调）...")
    success, stdout, stderr = run_command("paplay /tmp/test_tone.wav", "播放测试音频")
    
    if success:
        print("✅ 音频播放测试完成")
        # 询问用户是否听到声音
        print("\n❓ 您听到测试音调了吗？")
        print("   如果听到了，说明扬声器工作正常")
        print("   如果没听到，可能需要检查Windows音频设置")
        return True
    else:
        print(f"❌ 音频播放失败: {stderr}")
        return False

def test_microphone():
    """测试麦克风录音"""
    print("\n🎤 测试麦克风录音...")
    
    print("📢 请在听到提示后说话（录音3秒）...")
    time.sleep(1)
    print("🔴 开始录音...")
    
    # 录音3秒
    record_cmd = "parecord --format=s16le --rate=44100 --channels=1 /tmp/test_recording.wav"
    
    try:
        process = subprocess.Popen(record_cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(3)  # 录音3秒
        process.terminate()
        process.wait()
        
        print("🔵 录音结束")
        
        # 检查录音文件
        if os.path.exists('/tmp/test_recording.wav'):
            size = os.path.getsize('/tmp/test_recording.wav')
            print(f"📁 录音文件大小: {size} 字节")
            
            if size > 1000:  # 大于1KB说明录到了内容
                print("✅ 麦克风录音成功")
                
                # 播放录音
                print("🔄 播放刚才的录音...")
                success, stdout, stderr = run_command("paplay /tmp/test_recording.wav")
                if success:
                    print("✅ 录音播放完成")
                    print("❓ 您听到自己的声音了吗？")
                    return True
                else:
                    print(f"⚠️ 录音播放失败: {stderr}")
            else:
                print("⚠️ 录音文件太小，可能没有录到声音")
                
        else:
            print("❌ 录音文件不存在")
            
    except Exception as e:
        print(f"❌ 录音测试失败: {e}")
    
    return False

def check_windows_audio_settings():
    """检查Windows音频设置建议"""
    print("\n🪟 Windows音频设置检查建议:")
    print("=" * 50)
    print("1. 📱 右键点击Windows任务栏的音量图标")
    print("2. 🔧 选择'声音设置'或'打开音量混合器'")
    print("3. 🎧 确保您的外接扬声器被设为'默认设备'")
    print("4. 🎤 确保您的外接麦克风被设为'默认设备'")
    print("5. 🔊 测试播放和录制功能是否正常")
    print("6. ⚙️ 在设备属性中启用'允许应用程序独占控制此设备'")
    print("7. 🔄 重启WSL: wsl --shutdown (在Windows CMD中执行)")

def main():
    """主函数"""
    print("🎧 外接音频设备诊断工具")
    print("=" * 50)
    
    # 设置环境变量
    os.environ['PULSE_SERVER'] = 'unix:/mnt/wslg/PulseServer'
    
    # 1. 强制激活设备
    force_activate_audio_devices()
    
    # 2. 测试扬声器
    speaker_ok = test_audio_playback()
    
    # 3. 测试麦克风
    mic_ok = test_microphone()
    
    # 4. 显示结果
    print("\n" + "=" * 50)
    print("📊 诊断结果:")
    print(f"🔊 扬声器: {'✅ 工作正常' if speaker_ok else '❌ 需要检查'}")
    print(f"🎤 麦克风: {'✅ 工作正常' if mic_ok else '❌ 需要检查'}")
    
    if not speaker_ok or not mic_ok:
        check_windows_audio_settings()
        
        print("\n💡 故障排除步骤:")
        print("1. 按照上述Windows设置进行配置")
        print("2. 重启WSL: wsl --shutdown")
        print("3. 重新运行此诊断工具")
        print("4. 如仍有问题，可能需要使用虚拟音频驱动")
    else:
        print("\n🎉 音频设备工作正常，可以使用Dragon机器人系统！")

if __name__ == "__main__":
    main()