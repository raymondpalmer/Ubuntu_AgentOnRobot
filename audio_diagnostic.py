#!/usr/bin/env python3
"""
音频设备检测和配置工具
用于Dragon机器人语音控制系统的音频设备配置
"""

import sys
import subprocess
import platform
import os

def check_system_info():
    """检查系统信息"""
    print("=== 系统信息 ===")
    print(f"操作系统: {platform.system()} {platform.release()}")
    print(f"架构: {platform.machine()}")
    print(f"Python版本: {sys.version}")
    print()

def check_audio_hardware():
    """检查音频硬件"""
    print("=== 硬件检测 ===")
    
    # 检查USB音频设备
    try:
        result = subprocess.run(['lsusb'], capture_output=True, text=True)
        usb_audio = [line for line in result.stdout.split('\n') if 'audio' in line.lower()]
        if usb_audio:
            print("USB音频设备:")
            for device in usb_audio:
                print(f"  {device}")
        else:
            print("未发现USB音频设备")
    except:
        print("无法检查USB设备")
    
    # 检查PCI音频设备
    try:
        result = subprocess.run(['lspci'], capture_output=True, text=True)
        pci_audio = [line for line in result.stdout.split('\n') if 'audio' in line.lower()]
        if pci_audio:
            print("PCI音频设备:")
            for device in pci_audio:
                print(f"  {device}")
        else:
            print("未发现PCI音频设备")
    except:
        print("无法检查PCI设备")
    
    # 检查音频设备文件
    print("\n音频设备文件:")
    if os.path.exists('/dev/snd'):
        devices = os.listdir('/dev/snd')
        if devices:
            print(f"  发现设备: {devices}")
        else:
            print("  /dev/snd 目录为空")
    else:
        print("  /dev/snd 目录不存在")
    
    # 检查ALSA音频卡
    if os.path.exists('/proc/asound/cards'):
        try:
            with open('/proc/asound/cards', 'r') as f:
                cards = f.read().strip()
                if cards:
                    print(f"\nALSA音频卡:\n{cards}")
                else:
                    print("\n未发现ALSA音频卡")
        except:
            print("\n无法读取ALSA音频卡信息")
    else:
        print("\n/proc/asound/cards 不存在")
    
    print()

def check_audio_software():
    """检查音频软件"""
    print("=== 软件检测 ===")
    
    # 检查ALSA工具
    tools = ['aplay', 'arecord', 'alsamixer', 'amixer']
    for tool in tools:
        try:
            result = subprocess.run(['which', tool], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✓ {tool}: {result.stdout.strip()}")
            else:
                print(f"✗ {tool}: 未安装")
        except:
            print(f"✗ {tool}: 检查失败")
    
    # 检查PulseAudio
    try:
        result = subprocess.run(['which', 'pulseaudio'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ pulseaudio: {result.stdout.strip()}")
            
            # 检查PulseAudio状态
            try:
                result = subprocess.run(['pulseaudio', '--check'], capture_output=True, text=True)
                if result.returncode == 0:
                    print("  状态: 运行中")
                else:
                    print("  状态: 未运行")
            except:
                print("  状态: 检查失败")
        else:
            print("✗ pulseaudio: 未安装")
    except:
        print("✗ pulseaudio: 检查失败")
    
    print()

def check_python_audio():
    """检查Python音频库"""
    print("=== Python音频库检测 ===")
    
    libraries = [
        ('pyaudio', 'PyAudio'),
        ('sounddevice', 'SoundDevice'),
        ('wave', 'Wave'),
        ('audioop', 'AudioOp'),
        ('speech_recognition', 'SpeechRecognition'),
        ('pydub', 'PyDub')
    ]
    
    for module_name, display_name in libraries:
        try:
            __import__(module_name)
            print(f"✓ {display_name}: 已安装")
        except ImportError:
            print(f"✗ {display_name}: 未安装")
    
    print()

def test_audio_devices():
    """测试音频设备"""
    print("=== 音频设备测试 ===")
    
    try:
        import sounddevice as sd
        
        # 列出所有设备
        devices = sd.query_devices()
        print("可用音频设备:")
        
        input_devices = []
        output_devices = []
        
        for i, device in enumerate(devices):
            device_type = []
            if device['max_input_channels'] > 0:
                device_type.append('输入')
                input_devices.append(i)
            if device['max_output_channels'] > 0:
                device_type.append('输出')
                output_devices.append(i)
            
            if device_type:
                print(f"  设备 {i}: {device['name']}")
                print(f"    类型: {'/'.join(device_type)}")
                print(f"    输入通道: {device['max_input_channels']}")
                print(f"    输出通道: {device['max_output_channels']}")
                print(f"    默认采样率: {device['default_samplerate']:.0f} Hz")
        
        # 检查默认设备
        try:
            default_input = sd.default.device[0]
            default_output = sd.default.device[1] 
            print(f"\n默认输入设备: {default_input}")
            print(f"默认输出设备: {default_output}")
        except:
            print("\n无法获取默认设备")
        
        return len(input_devices) > 0 and len(output_devices) > 0
        
    except ImportError:
        print("SoundDevice库未安装，无法测试设备")
        return False
    except Exception as e:
        print(f"设备测试失败: {e}")
        return False

def suggest_installation():
    """建议安装步骤"""
    print("=== 安装建议 ===")
    
    print("1. 安装系统音频包:")
    print("   sudo apt update")
    print("   sudo apt install -y alsa-utils pulseaudio pulseaudio-utils")
    print("   sudo apt install -y portaudio19-dev")
    print()
    
    print("2. 安装Python音频库:")
    print("   pip install pyaudio sounddevice speech_recognition pydub")
    print()
    
    print("3. 配置音频权限:")
    print("   sudo usermod -a -G audio $USER")
    print("   # 重新登录或运行: newgrp audio")
    print()
    
    print("4. 启动PulseAudio:")
    print("   pulseaudio --start")
    print()
    
    print("5. 测试音频:")
    print("   aplay /usr/share/sounds/alsa/Front_Left.wav")
    print("   arecord -d 3 test.wav && aplay test.wav")
    print()

def check_virtual_environment():
    """检查虚拟环境"""
    print("=== 虚拟环境检测 ===")
    
    # 检查是否在Docker中
    if os.path.exists('/.dockerenv'):
        print("检测到Docker容器环境")
        print("建议:")
        print("  1. 在启动容器时添加音频设备映射:")
        print("     docker run --device=/dev/snd ...")
        print("  2. 或使用虚拟音频设备进行测试")
        return True
    
    # 检查是否在虚拟机中
    try:
        result = subprocess.run(['dmidecode', '-s', 'system-product-name'], 
                              capture_output=True, text=True)
        product_name = result.stdout.strip().lower()
        if any(vm in product_name for vm in ['virtualbox', 'vmware', 'kvm', 'qemu']):
            print(f"检测到虚拟机环境: {product_name}")
            print("建议在虚拟机设置中启用音频设备")
            return True
    except:
        pass
    
    print("运行在物理机环境")
    return False

def main():
    """主函数"""
    print("Dragon机器人语音控制系统 - 音频设备诊断工具")
    print("=" * 60)
    
    check_system_info()
    is_virtual = check_virtual_environment()
    check_audio_hardware()
    check_audio_software()
    check_python_audio()
    
    # 测试音频设备
    audio_working = test_audio_devices()
    
    print("=== 诊断结果 ===")
    if audio_working:
        print("✓ 音频系统配置正常，可以使用语音控制功能")
    else:
        print("✗ 音频系统配置不完整")
        if is_virtual:
            print("  原因: 虚拟环境中音频设备受限")
            print("  解决方案: 配置虚拟环境音频设备或使用虚拟音频设备")
        else:
            print("  原因: 缺少音频硬件或软件包")
            suggest_installation()
    
    print("\n详细的配置指南请参考: AUDIO_SETUP_GUIDE.md")

if __name__ == "__main__":
    main()
