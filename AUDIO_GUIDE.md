# 🎵 Dragon机器人音频配置完成指南

## ✅ 配置状态

您的Dragon机器人语音控制系统现在已经配置好音频支持！

### 🔧 已完成的配置

1. **PulseAudio音频服务** ✅
   - 连接到Windows音频系统
   - 默认扬声器: RDPSink
   - 默认麦克风: RDPSource

2. **音频环境变量** ✅
   - PULSE_SERVER 已设置
   - 音频设备已激活

3. **Dragon机器人系统** ✅
   - 音频环境自动初始化
   - 音色配置: zh_female_xueling
   - 知识库已加载 (78文档)

## 🚀 启动系统

### 方法1: 使用启动脚本（推荐）
```bash
/home/ray/agent/start_dragon_robot.sh
```

### 方法2: 手动启动
```bash
cd /home/ray/agent
export PULSE_SERVER="unix:/mnt/wslg/PulseServer"
python3 dragon_robot_session.py
```

## 🎯 音频功能测试

### 检查音频设备
```bash
# 测试音频设备状态
python3 /home/ray/agent/test_audio.py

# 查看音频设备信息
pactl list sinks short    # 扬声器
pactl list sources short  # 麦克风
```

### 当前状态
- 🔊 **扬声器**: ✅ 正常工作
- 🎤 **麦克风**: ⚠️ 可能需要Windows权限

## 🔊 声音问题排查

### 如果听不到声音：

1. **检查Windows音量**
   - 确保Windows系统音量没有静音
   - 检查默认播放设备设置

2. **检查WSL音频连接**
   ```bash
   pactl info  # 查看连接状态
   pactl list sinks  # 查看扬声器设备
   ```

3. **重新激活音频设备**
   ```bash
   pactl set-sink-mute RDPSink false
   pactl set-sink-volume RDPSink 80%
   ```

### 如果麦克风无法录音：

1. **检查Windows麦克风权限**
   - Windows设置 → 隐私 → 麦克风
   - 允许应用访问麦克风
   - 检查麦克风默认设备

2. **在WSL中测试麦克风**
   ```bash
   # 录制测试（说话3秒）
   parecord --format=s16le --rate=16000 --channels=1 test.wav
   
   # 播放测试
   paplay test.wav
   ```

3. **检查麦克风设备**
   ```bash
   pactl set-source-mute RDPSource false
   pactl set-source-volume RDPSource 80%
   ```

## 🤖 使用Dragon机器人系统

### 启动后的功能：

1. **语音对话** 🎙️
   - 系统会自动监听您的语音
   - 可以进行自然对话
   - 基于知识库回答问题

2. **机器人控制** 🤖
   - "机器人前进" → 前进动作
   - "机器人左转" → 左转动作
   - "机器人停止" → 停止动作

3. **知识库查询** 📚
   - "机器人怎么操作？"
   - "语音识别问题怎么解决？"
   - 任何关于文档内容的问题

### 系统提示信息：
- ✅ 音频环境初始化成功 = 音频配置正常
- 🎵 音色已应用 = 语音合成准备就绪
- 🧠 知识库已加载 = 智能问答功能可用
- 🔗 连接豆包语音服务 = 在线语音功能启用

## 🛠️ 高级配置

### 调整音频质量
编辑 `/home/ray/.pulse/client.conf`:
```
# 启用高质量音频
enable-shm = true
default-sample-format = s24le
default-sample-rate = 48000
```

### 音色切换
编辑 `/home/ray/agent/voice_config.py`:
```python
# 更改默认音色
"speaker": "zh_female_xueling"  # 当前
"speaker": "zh_male_yunfeng"    # 男声
```

## 📞 技术支持

### 常见ALSA警告
看到这些警告是正常的，不影响功能：
```
ALSA lib confmisc.c:855:(parse_card) cannot find card '0'
ALSA lib pcm.c:2664:(snd_pcm_open_noupdate) Unknown PCM sysdefault
```
这是WSL环境下的正常现象。

### 日志查看
```bash
# 查看音频日志
journalctl --user -u pulseaudio

# 查看系统音频状态
systemctl --user status pulseaudio
```

## 🎉 开始使用！

现在您可以：

1. **启动系统**:
   ```bash
   /home/ray/agent/start_dragon_robot.sh
   ```

2. **测试对话**: 等待系统完全启动后，尝试说话

3. **控制机器人**: 说出"机器人前进"等指令

4. **智能问答**: 询问关于文档的任何问题

5. **安全退出**: 使用 `Ctrl+C`

---

**🎵 音频配置完成！您的Dragon机器人现在可以听到和说话了！** 🤖✨