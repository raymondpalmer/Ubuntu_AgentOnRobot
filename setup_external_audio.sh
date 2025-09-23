#!/bin/bash
# 外接音频设备配置脚本

echo "🎧 配置外接音频设备支持"
echo "=========================="

# 检查Windows音频设备状态
echo "🔍 检查Windows音频设备..."

# 创建高级音频配置
cat > ~/.pulse/daemon.conf << 'EOF'
# PulseAudio Daemon Configuration - 外接设备优化

# 增加缓冲区大小以支持外接设备
default-sample-format = s16le
default-sample-rate = 44100
default-sample-channels = 2

# 降低延迟
default-fragments = 4
default-fragment-size-msec = 25

# 启用自动设备检测
load-module-on-demand = yes

# 外接设备支持
flat-volumes = no
EOF

# 重启PulseAudio以应用配置
echo "🔄 重启PulseAudio服务..."
pulseaudio --kill 2>/dev/null || true
sleep 2

# 重新连接到WSL音频
export PULSE_SERVER="unix:/mnt/wslg/PulseServer"
export PULSE_RUNTIME_PATH="$XDG_RUNTIME_DIR/pulse"

# 检查连接状态
if pactl info > /dev/null 2>&1; then
    echo "✅ PulseAudio重新连接成功"
    
    # 列出所有设备
    echo ""
    echo "🔊 可用输出设备:"
    pactl list sinks short
    
    echo ""
    echo "🎤 可用输入设备:"
    pactl list sources short
    
    # 检查设备状态
    echo ""
    echo "📊 设备状态:"
    echo "默认输出: $(pactl get-default-sink)"
    echo "默认输入: $(pactl get-default-source)"
    
else
    echo "❌ PulseAudio连接失败"
fi

echo ""
echo "💡 外接设备使用提示:"
echo "1. 确保Windows中外接设备被设为默认设备"
echo "2. 检查Windows音量控制面板中的设备状态"
echo "3. 可能需要在Windows设置中允许独占模式"