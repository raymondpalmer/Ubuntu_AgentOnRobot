#!/bin/bash
# Dragon机器人语音控制系统启动脚本
# 自动配置音频环境并启动系统

echo "🤖 Dragon机器人语音控制系统"
echo "================================"

# 设置音频环境
echo "🔧 配置音频环境..."
export PULSE_SERVER="unix:/mnt/wslg/PulseServer"
export PULSE_RUNTIME_PATH="$XDG_RUNTIME_DIR/pulse"

# 检查音频连接
if pactl info > /dev/null 2>&1; then
    echo "✅ 音频环境就绪"
    
    # 激活音频设备
    pactl set-sink-mute RDPSink false 2>/dev/null || true
    pactl set-source-mute RDPSource false 2>/dev/null || true
    
    echo "🔊 扬声器: RDPSink (已激活)"
    echo "🎤 麦克风: RDPSource (已激活)"
else
    echo "⚠️ 音频环境未就绪，但系统仍可运行"
fi

echo ""
echo "🚀 启动Dragon机器人对话系统..."
echo "💡 提示:"
echo "   - 如果听不到声音，请检查Windows音量设置"
echo "   - 麦克风可能需要在Windows中授权WSL访问"
echo "   - 使用 Ctrl+C 可以安全退出系统"
echo ""

# 切换到正确目录并启动系统
cd /home/ray/agent
python3 dragon_robot_session.py