# 音频设备配置指南

## 系统要求检查

### 1. 硬件检查
```bash
# 检查USB音频设备
lsusb | grep -i audio

# 检查PCI音频设备
lspci | grep -i audio

# 查看音频设备
cat /proc/asound/cards
```

### 2. 驱动检查
```bash
# 查看音频相关模块
lsmod | grep snd

# 手动加载音频模块（如果需要）
sudo modprobe snd-hda-intel
sudo modprobe snd-usb-audio
```

## 软件安装

### 1. 安装基本音频包
```bash
# 更新包列表
sudo apt update

# 安装ALSA工具
sudo apt install -y alsa-utils

# 安装PulseAudio
sudo apt install -y pulseaudio pulseaudio-utils

# 安装音频控制工具
sudo apt install -y pavucontrol
```

### 2. 安装Python音频库
```bash
# 安装PyAudio依赖
sudo apt install -y portaudio19-dev

# 安装Python音频库
pip install pyaudio sounddevice
```

## 音频配置

### 1. ALSA配置
```bash
# 测试音频播放
speaker-test -t wav -c 2

# 查看可用音频设备
aplay -l
arecord -l

# 设置默认音频设备
alsamixer
```

### 2. PulseAudio配置
```bash
# 启动PulseAudio
pulseaudio --start

# 查看PulseAudio状态
pulseaudio --check

# 列出音频设备
pactl list short sources  # 麦克风
pactl list short sinks    # 扬声器

# 图形化音量控制
pavucontrol
```

### 3. 测试音频
```bash
# 录音测试
arecord -d 5 test.wav

# 播放测试
aplay test.wav

# 使用PulseAudio测试
parecord -d 5 test_pulse.wav
paplay test_pulse.wav
```

## Python代码中的音频配置

### 1. 检测音频设备
```python
import sounddevice as sd
import pyaudio

def list_audio_devices():
    """列出所有音频设备"""
    print("=== SoundDevice 设备列表 ===")
    print(sd.query_devices())
    
    print("\n=== PyAudio 设备列表 ===")
    p = pyaudio.PyAudio()
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        print(f"设备 {i}: {info['name']}")
        print(f"  输入通道: {info['maxInputChannels']}")
        print(f"  输出通道: {info['maxOutputChannels']}")
        print(f"  采样率: {info['defaultSampleRate']}")
    p.terminate()

if __name__ == "__main__":
    list_audio_devices()
```

### 2. 配置默认音频设备
```python
import sounddevice as sd

# 设置默认设备
sd.default.device = 'default'  # 或具体设备ID
sd.default.samplerate = 16000
sd.default.channels = 1

# 获取默认设备信息
print("默认输入设备:", sd.default.device[0])
print("默认输出设备:", sd.default.device[1])
```

## 虚拟环境解决方案

### 1. Docker容器音频支持
```bash
# 运行容器时映射音频设备
docker run -it \
  --device=/dev/snd \
  -e PULSE_RUNTIME_PATH=/var/run/pulse \
  -v /var/run/pulse:/var/run/pulse \
  your_image
```

### 2. 虚拟音频设备
```bash
# 安装虚拟音频设备
sudo apt install -y pulseaudio-module-virtual-surround-sink

# 创建虚拟音频设备
pactl load-module module-null-sink sink_name=virtual_speaker
pactl load-module module-virtual-source source_name=virtual_mic
```

## 常见问题解决

### 1. 权限问题
```bash
# 将用户添加到audio组
sudo usermod -a -G audio $USER

# 重新登录或使用
newgrp audio
```

### 2. 设备被占用
```bash
# 查看占用音频设备的进程
sudo fuser -v /dev/snd/*

# 重启音频服务
sudo systemctl restart alsa-state
pulseaudio -k && pulseaudio --start
```

### 3. 驱动问题
```bash
# 重新加载音频驱动
sudo rmmod snd_hda_intel
sudo modprobe snd_hda_intel

# 检查内核日志
dmesg | grep -i audio
```

## 测试脚本

### audio_test.py
```python
#!/usr/bin/env python3
import sounddevice as sd
import numpy as np
import time

def test_audio_system():
    """测试音频系统"""
    try:
        print("=== 音频设备检测 ===")
        devices = sd.query_devices()
        print(devices)
        
        print("\n=== 录音测试 ===")
        duration = 3  # 秒
        samplerate = 16000
        
        print(f"开始录音 {duration} 秒...")
        recording = sd.rec(int(duration * samplerate), 
                          samplerate=samplerate, 
                          channels=1, 
                          dtype=np.int16)
        sd.wait()
        print("录音完成")
        
        print("\n=== 播放测试 ===")
        print("播放录音...")
        sd.play(recording, samplerate=samplerate)
        sd.wait()
        print("播放完成")
        
        return True
        
    except Exception as e:
        print(f"音频测试失败: {e}")
        return False

if __name__ == "__main__":
    test_audio_system()
```

## 项目中的使用

在你的语音控制项目中，建议：

1. **开始时检测音频设备**：在启动语音控制前先检测可用的音频设备
2. **提供设备选择**：允许用户选择特定的麦克风和扬声器
3. **处理音频错误**：优雅地处理音频设备不可用的情况
4. **音频质量配置**：根据需要调整采样率、通道数等参数

### 在main_voice_agent.py中集成
```python
def initialize_audio():
    """初始化音频系统"""
    try:
        # 检测音频设备
        devices = sd.query_devices()
        
        # 选择合适的设备
        input_device = None
        output_device = None
        
        for i, device in enumerate(devices):
            if device['max_input_channels'] > 0:
                input_device = i
                break
                
        for i, device in enumerate(devices):
            if device['max_output_channels'] > 0:
                output_device = i
                break
        
        if input_device is None:
            raise RuntimeError("未找到可用的麦克风设备")
        if output_device is None:
            raise RuntimeError("未找到可用的扬声器设备")
            
        # 设置默认设备
        sd.default.device = (input_device, output_device)
        sd.default.samplerate = 16000
        sd.default.channels = 1
        
        print(f"音频初始化成功:")
        print(f"  输入设备: {devices[input_device]['name']}")
        print(f"  输出设备: {devices[output_device]['name']}")
        
        return True
        
    except Exception as e:
        print(f"音频初始化失败: {e}")
        return False
```
