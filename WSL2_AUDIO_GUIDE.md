# WSL2环境下的音频配置指南

## 当前环境分析
你正在WSL2（Windows Subsystem for Linux 2）环境中运行，这解释了为什么没有检测到音频硬件设备。

## WSL2音频解决方案

### 方案一：WSLg音频支持（推荐）

WSL2的新版本通过WSLg支持音频。需要确保：

1. **更新WSL和Windows**
```powershell
# 在Windows PowerShell中运行
wsl --update
wsl --shutdown
```

2. **启用WSLg音频**
在WSL2中创建PulseAudio配置：
```bash
# 创建PulseAudio配置目录
mkdir -p ~/.config/pulse

# 创建配置文件
cat > ~/.config/pulse/client.conf << 'EOF'
# Connect to the WSLg PulseAudio server
default-server = unix:/mnt/wslg/PulseServer
EOF
```

3. **安装音频工具**
```bash
# 由于网络问题，我们使用离线安装或者配置代理
# 如果有代理，可以配置：
# export http_proxy=http://your-proxy:port
# export https_proxy=http://your-proxy:port

# 安装基础音频包
sudo apt install -y alsa-utils pulseaudio-utils

# 安装Python音频库
pip install sounddevice pyaudio speech_recognition
```

### 方案二：虚拟音频设备（用于开发测试）

如果WSLg音频不可用，可以创建虚拟音频设备用于开发测试：

```bash
# 安装PulseAudio
sudo apt install -y pulseaudio

# 启动PulseAudio
pulseaudio --start --verbose

# 创建虚拟音频设备
pactl load-module module-null-sink sink_name=virtual_speaker sink_properties=device.description="Virtual_Speaker"
pactl load-module module-virtual-source source_name=virtual_mic master=virtual_speaker.monitor source_properties=device.description="Virtual_Microphone"

# 设置为默认设备
pactl set-default-sink virtual_speaker
pactl set-default-source virtual_mic
```

### 方案三：使用模拟音频进行开发

创建一个模拟音频接口，用于开发和测试：

```python
# 模拟音频类，用于开发测试
class MockAudioInterface:
    def __init__(self):
        self.recording = False
        self.playing = False
    
    def start_recording(self):
        print("开始录音（模拟）")
        self.recording = True
        # 返回模拟的音频数据或从文件读取
        return "模拟语音输入：前进"
    
    def stop_recording(self):
        print("停止录音（模拟）")
        self.recording = False
    
    def play_audio(self, text):
        print(f"播放音频（模拟）：{text}")
        self.playing = True
    
    def is_recording(self):
        return self.recording
    
    def is_playing(self):
        return self.playing
```

## 推荐的开发流程

### 1. 立即可用的解决方案

让我们修改现有的语音控制系统，使其在WSL2环境下也能工作：
