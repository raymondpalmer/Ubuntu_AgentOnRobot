#!/usr/bin/env python3
"""
WSL2音频诊断和修复工具
帮助诊断和解决WSL2环境下的音频问题
"""

import os
import sys
import subprocess
import platform
from typing import Dict, List, Tuple

def check_wsl_environment() -> Dict[str, any]:
    """检查WSL环境"""
    info = {
        'is_wsl': False,
        'wsl_version': None,
        'kernel_version': None,
        'windows_version': None
    }
    
    try:
        # 检查是否在WSL中
        with open('/proc/version', 'r') as f:
            version_info = f.read().lower()
            if 'microsoft' in version_info:
                info['is_wsl'] = True
                if 'wsl2' in version_info:
                    info['wsl_version'] = '2'
                else:
                    info['wsl_version'] = '1'
                info['kernel_version'] = version_info.strip()
    except:
        pass
    
    return info

def check_wslg_support() -> Dict[str, any]:
    """检查WSLg支持"""
    info = {
        'wslg_available': False,
        'display_env': None,
        'wayland_env': None,
        'pulse_server': None,
        'wslg_mount': False
    }
    
    # 检查环境变量
    info['display_env'] = os.getenv('DISPLAY')
    info['wayland_env'] = os.getenv('WAYLAND_DISPLAY')
    info['pulse_server'] = os.getenv('PULSE_SERVER')
    
    # 检查WSLg挂载点
    if os.path.exists('/mnt/wslg'):
        info['wslg_mount'] = True
        
    # 判断WSLg是否可用
    if any([info['display_env'], info['wayland_env'], info['pulse_server'], info['wslg_mount']]):
        info['wslg_available'] = True
    
    return info

def check_audio_packages() -> Dict[str, bool]:
    """检查音频相关包"""
    packages = {
        'alsa-utils': False,
        'pulseaudio': False,
        'pulseaudio-utils': False,
        'portaudio19-dev': False
    }
    
    for package in packages.keys():
        try:
            result = subprocess.run(['dpkg', '-l', package], 
                                  capture_output=True, text=True)
            if result.returncode == 0 and 'ii' in result.stdout:
                packages[package] = True
        except:
            pass
    
    return packages

def check_python_audio_libs() -> Dict[str, bool]:
    """检查Python音频库"""
    libs = {
        'sounddevice': False,
        'pyaudio': False,
        'pydub': False,
        'speech_recognition': False
    }
    
    for lib in libs.keys():
        try:
            __import__(lib)
            libs[lib] = True
        except ImportError:
            pass
    
    return libs

def test_audio_devices() -> Dict[str, any]:
    """测试音频设备"""
    info = {
        'sounddevice_available': False,
        'input_devices': [],
        'output_devices': [],
        'default_input': None,
        'default_output': None,
        'error': None
    }
    
    try:
        import sounddevice as sd
        info['sounddevice_available'] = True
        
        # 获取设备列表
        devices = sd.query_devices()
        
        for i, device in enumerate(devices):
            device_info = {
                'id': i,
                'name': device['name'],
                'channels': device['max_input_channels'] if device['max_input_channels'] > 0 else device['max_output_channels'],
                'sample_rate': device['default_samplerate']
            }
            
            if device['max_input_channels'] > 0:
                info['input_devices'].append(device_info)
            if device['max_output_channels'] > 0:
                info['output_devices'].append(device_info)
        
        # 获取默认设备
        try:
            info['default_input'] = sd.default.device[0]
            info['default_output'] = sd.default.device[1]
        except:
            pass
            
    except ImportError as e:
        info['error'] = f"SoundDevice未安装: {e}"
    except Exception as e:
        info['error'] = f"音频设备检测失败: {e}"
    
    return info

def generate_audio_fix_script() -> str:
    """生成音频修复脚本"""
    script = """#!/bin/bash
# WSL2音频修复脚本

echo "🔧 WSL2音频环境修复工具"
echo "================================"

# 更新包列表
echo "📦 更新包列表..."
sudo apt update

# 安装基础音频包
echo "🎵 安装音频包..."
sudo apt install -y alsa-utils pulseaudio pulseaudio-utils portaudio19-dev

# 安装Python音频库
echo "🐍 安装Python音频库..."
pip install sounddevice pyaudio pydub speech_recognition

# 配置WSLg音频
echo "🎤 配置WSLg音频..."
mkdir -p ~/.config/pulse

# 创建PulseAudio客户端配置
cat > ~/.config/pulse/client.conf << 'EOF'
# WSLg PulseAudio配置
default-server = unix:/mnt/wslg/PulseServer
EOF

# 设置音频权限
echo "🔐 设置音频权限..."
sudo usermod -a -G audio $USER

echo "✅ 音频环境修复完成"
echo "💡 请重启WSL或重新登录以应用权限更改"
echo "   命令: wsl --shutdown 然后重新启动WSL"
"""
    return script

def diagnose_audio_environment():
    """完整的音频环境诊断"""
    print("🔍 WSL2音频环境诊断工具")
    print("=" * 60)
    
    # 1. 检查WSL环境
    print("\n1️⃣ WSL环境检查")
    wsl_info = check_wsl_environment()
    
    if wsl_info['is_wsl']:
        print(f"✅ WSL环境: WSL{wsl_info['wsl_version']}")
        print(f"   内核版本: {wsl_info['kernel_version']}")
    else:
        print("❌ 不是WSL环境")
        return
    
    # 2. 检查WSLg支持
    print("\n2️⃣ WSLg支持检查")
    wslg_info = check_wslg_support()
    
    if wslg_info['wslg_available']:
        print("✅ WSLg环境可用")
        if wslg_info['display_env']:
            print(f"   DISPLAY: {wslg_info['display_env']}")
        if wslg_info['wayland_env']:
            print(f"   WAYLAND_DISPLAY: {wslg_info['wayland_env']}")
        if wslg_info['pulse_server']:
            print(f"   PULSE_SERVER: {wslg_info['pulse_server']}")
        if wslg_info['wslg_mount']:
            print("   WSLg挂载点: /mnt/wslg ✅")
    else:
        print("❌ WSLg环境不可用")
        print("💡 建议: 确保Windows 11并启用WSLg功能")
    
    # 3. 检查系统音频包
    print("\n3️⃣ 系统音频包检查")
    packages = check_audio_packages()
    
    for package, installed in packages.items():
        status = "✅" if installed else "❌"
        print(f"   {package}: {status}")
    
    # 4. 检查Python音频库
    print("\n4️⃣ Python音频库检查")
    libs = check_python_audio_libs()
    
    for lib, available in libs.items():
        status = "✅" if available else "❌"
        print(f"   {lib}: {status}")
    
    # 5. 测试音频设备
    print("\n5️⃣ 音频设备测试")
    audio_info = test_audio_devices()
    
    if audio_info['sounddevice_available']:
        print("✅ SoundDevice库可用")
        print(f"   输入设备数量: {len(audio_info['input_devices'])}")
        print(f"   输出设备数量: {len(audio_info['output_devices'])}")
        
        if audio_info['input_devices']:
            print("🎤 输入设备:")
            for device in audio_info['input_devices'][:3]:  # 只显示前3个
                print(f"     - {device['name']} (ID: {device['id']})")
        
        if audio_info['output_devices']:
            print("🔊 输出设备:")
            for device in audio_info['output_devices'][:3]:  # 只显示前3个
                print(f"     - {device['name']} (ID: {device['id']})")
        
        if audio_info['default_input'] is not None:
            print(f"   默认输入设备: {audio_info['default_input']}")
        if audio_info['default_output'] is not None:
            print(f"   默认输出设备: {audio_info['default_output']}")
            
    else:
        print("❌ SoundDevice库不可用")
        if audio_info['error']:
            print(f"   错误: {audio_info['error']}")
    
    # 6. 生成建议
    print("\n6️⃣ 诊断结果和建议")
    
    issues = []
    fixes = []
    
    # 检查问题
    if not wslg_info['wslg_available']:
        issues.append("WSLg环境不可用")
        fixes.append("升级到Windows 11并启用WSLg")
    
    if not any(packages.values()):
        issues.append("缺少系统音频包")
        fixes.append("安装音频系统包: sudo apt install alsa-utils pulseaudio")
    
    if not libs['sounddevice']:
        issues.append("SoundDevice库未安装")
        fixes.append("安装Python音频库: pip install sounddevice")
    
    if not audio_info['input_devices'] and audio_info['sounddevice_available']:
        issues.append("未检测到音频输入设备")
        fixes.append("检查Windows音频设备或使用模拟模式")
    
    if issues:
        print("❌ 发现问题:")
        for issue in issues:
            print(f"   - {issue}")
        
        print("\n💡 建议修复:")
        for fix in fixes:
            print(f"   - {fix}")
        
        # 询问是否生成修复脚本
        choice = input("\n是否生成自动修复脚本? (y/n): ").strip().lower()
        if choice == 'y':
            script_content = generate_audio_fix_script()
            with open('fix_audio.sh', 'w') as f:
                f.write(script_content)
            os.chmod('fix_audio.sh', 0o755)
            print("✅ 修复脚本已生成: fix_audio.sh")
            print("   运行: ./fix_audio.sh")
    else:
        print("✅ 音频环境配置良好")
    
    # 7. 推荐模式
    print("\n7️⃣ 推荐音频模式")
    
    if (wslg_info['wslg_available'] and 
        libs['sounddevice'] and 
        audio_info['input_devices'] and 
        audio_info['output_devices']):
        print("🎤 推荐: WSLg模式 (真实语音控制)")
    elif libs['sounddevice']:
        print("🔧 推荐: 虚拟音频模式 (开发测试)")
    else:
        print("📝 推荐: 模拟模式 (键盘输入)")
    
    print("\n" + "=" * 60)
    print("诊断完成！")

def main():
    """主函数"""
    try:
        diagnose_audio_environment()
    except KeyboardInterrupt:
        print("\n\n诊断被中断")
    except Exception as e:
        print(f"\n诊断过程出错: {e}")

if __name__ == "__main__":
    main()
