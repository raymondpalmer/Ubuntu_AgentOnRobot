#!/usr/bin/env python3
"""
音频优化工具 - 解决WSL2环境下的音频断续问题
"""

import subprocess
import time

def optimize_wsl_audio():
    """优化WSL2音频设置"""
    commands = [
        # 设置音频缓冲区大小
        "export PULSE_BUFFER_SIZE=32768",
        # 设置音频延迟
        "export PULSE_LATENCY_MSEC=30",
        # 禁用音频节能模式
        "export PULSE_MODULE_DISABLE=module-suspend-on-idle",
    ]
    
    for cmd in commands:
        try:
            subprocess.run(cmd, shell=True, check=False)
            print(f"✅ 执行: {cmd}")
        except Exception as e:
            print(f"⚠️ 执行失败: {cmd} - {e}")

def check_audio_devices():
    """检查音频设备状态"""
    try:
        # 检查ALSA设备
        result = subprocess.run("aplay -l", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("🔊 ALSA音频设备:")
            print(result.stdout)
        else:
            print("⚠️ ALSA设备检测失败")
            
        # 检查PulseAudio设备
        result = subprocess.run("pactl list short sinks", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("🎵 PulseAudio设备:")
            print(result.stdout)
        else:
            print("⚠️ PulseAudio设备检测失败")
            
    except Exception as e:
        print(f"❌ 音频设备检测错误: {e}")

def restart_audio_services():
    """重启音频服务"""
    try:
        # 重启PulseAudio
        subprocess.run("pulseaudio --kill", shell=True, check=False)
        time.sleep(2)
        subprocess.run("pulseaudio --start", shell=True, check=False)
        print("🔄 PulseAudio已重启")
        
    except Exception as e:
        print(f"⚠️ 音频服务重启失败: {e}")

if __name__ == "__main__":
    print("🎵 音频系统优化工具")
    print("=" * 40)
    
    print("\n1. 检查音频设备...")
    check_audio_devices()
    
    print("\n2. 优化WSL2音频设置...")
    optimize_wsl_audio()
    
    print("\n3. 重启音频服务...")
    restart_audio_services()
    
    print("\n✅ 音频优化完成！")