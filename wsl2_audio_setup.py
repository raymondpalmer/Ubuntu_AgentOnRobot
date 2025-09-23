#!/usr/bin/env python3
"""
WSL2专用音频设置工具
"""

import os
import subprocess

def setup_wsl2_audio_environment():
    """设置WSL2音频环境变量"""
    env_vars = {
        'PULSE_AUDIO_SYSTEM_WIDE': '1',
        'PULSE_BUFFER_SIZE': '65536',  # 更大的缓冲区
        'PULSE_LATENCY_MSEC': '50',    # 增加延迟容忍度
        'XDG_RUNTIME_DIR': '/run/user/1000',
        'PULSE_RUNTIME_PATH': '/run/user/1000/pulse'
    }
    
    for key, value in env_vars.items():
        os.environ[key] = value
        print(f"✅ 设置环境变量: {key}={value}")

def create_pulseaudio_config():
    """创建PulseAudio配置文件"""
    config_dir = os.path.expanduser("~/.config/pulse")
    os.makedirs(config_dir, exist_ok=True)
    
    # 客户端配置
    client_conf = """
# WSL2 PulseAudio客户端配置
default-server = unix:/mnt/wslg/PulseServer
# enable-memfd = yes
autospawn = no
daemon-binary = /bin/true
enable-shm = false
"""
    
    with open(f"{config_dir}/client.conf", "w") as f:
        f.write(client_conf)
    print(f"✅ 创建客户端配置: {config_dir}/client.conf")

def test_audio_configuration():
    """测试音频配置"""
    try:
        # 测试音频设备
        result = subprocess.run("pactl info", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("🎵 PulseAudio信息:")
            print(result.stdout[:500])  # 前500字符
        else:
            print(f"⚠️ PulseAudio测试失败: {result.stderr}")
            
    except Exception as e:
        print(f"❌ 音频测试错误: {e}")

if __name__ == "__main__":
    print("🎵 WSL2音频环境设置")
    print("=" * 40)
    
    print("\n1. 设置环境变量...")
    setup_wsl2_audio_environment()
    
    print("\n2. 创建PulseAudio配置...")
    create_pulseaudio_config()
    
    print("\n3. 测试音频配置...")
    test_audio_configuration()
    
    print("\n✅ WSL2音频环境设置完成！")
    print("💡 建议重启终端或使用 'source ~/.bashrc' 使环境变量生效")