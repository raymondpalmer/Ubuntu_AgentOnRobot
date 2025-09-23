#!/bin/bash
echo "🔧 WSL2音频环境修复脚本"
echo "================================"

# 检查PulseAudio
echo "1. 检查PulseAudio状态..."
if ! command -v pulseaudio &> /dev/null; then
    echo "⚠️ PulseAudio未安装，正在安装..."
    sudo apt update
    sudo apt install -y pulseaudio pulseaudio-utils
fi

# 创建ALSA配置
echo "2. 配置ALSA..."
cat > ~/.asoundrc << EOF
pcm.!default pulse
ctl.!default pulse
pcm.pulse {
    type pulse
}
ctl.pulse {
    type pulse
}
EOF

# 设置环境变量
echo "3. 设置音频环境变量..."
cat >> ~/.bashrc << 'EOF'
# WSL2音频优化
export PULSE_RUNTIME_PATH=/tmp/pulse-$(id -u)
export ALSA_BACKEND=pulse
export PULSE_LATENCY_MSEC=60
EOF

# 立即应用环境变量
export PULSE_RUNTIME_PATH=/tmp/pulse-$(id -u)
export ALSA_BACKEND=pulse
export PULSE_LATENCY_MSEC=60

# 重启PulseAudio
echo "4. 重启PulseAudio..."
pulseaudio --kill 2>/dev/null || true
sleep 1
pulseaudio --start --verbose &

echo "✅ WSL2音频环境修复完成！"
echo "💡 请重新启动终端或运行 'source ~/.bashrc'"
echo "🎵 然后重新运行Dragon机器人系统"