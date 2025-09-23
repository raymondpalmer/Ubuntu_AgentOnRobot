#!/bin/bash
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
