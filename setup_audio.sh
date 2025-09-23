#!/bin/bash
# WSL音频环境配置脚本

echo "🔧 配置WSL音频环境..."

# 设置环境变量
export PULSE_SERVER="unix:/mnt/wslg/PulseServer"
export PULSE_RUNTIME_PATH="$XDG_RUNTIME_DIR/pulse"

# 确保PulseAudio目录存在
mkdir -p ~/.pulse
mkdir -p "$PULSE_RUNTIME_PATH"

# 验证音频连接
echo "📡 检查PulseAudio连接..."
if pactl info > /dev/null 2>&1; then
    echo "✅ PulseAudio连接成功"
    
    echo "🔊 可用输出设备:"
    pactl list sinks short
    
    echo "🎤 可用输入设备:"
    pactl list sources short
    
    # 激活音频设备
    echo "⚡ 激活音频设备..."
    pactl set-sink-mute RDPSink false 2>/dev/null || true
    pactl set-source-mute RDPSource false 2>/dev/null || true
    
    echo "✅ 音频环境配置完成"
else
    echo "❌ PulseAudio连接失败"
    echo "请确保:"
    echo "1. WSL2已启用"
    echo "2. Windows音频服务正常运行" 
    echo "3. WSLg已安装和配置"
fi