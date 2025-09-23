#!/bin/bash
# Dragon机器人快速启动脚本 - 修复版

echo "🤖 Dragon机器人语音控制系统 v2.0"
echo "🔧 修复版 - 解决音频和启动问题"
echo "=================================="

# 确保在正确目录
cd /home/ray/agent

# 设置音频环境
export PULSE_SERVER="unix:/mnt/wslg/PulseServer"
export PULSE_RUNTIME_PATH="$XDG_RUNTIME_DIR/pulse"

# 激活音频设备
echo "🔊 激活音频设备..."
pactl set-sink-mute RDPSink false 2>/dev/null || true
pactl set-source-mute RDPSource false 2>/dev/null || true

echo ""
echo "✅ 系统修复完成，现在启动Dragon机器人..."
echo "💡 新功能:"
echo "   - 解决了'发送初始问候'卡死问题"
echo "   - 增强了音频播放支持（包含备用播放方式）"
echo "   - 改进了错误处理和调试信息"
echo ""
echo "🎯 使用方法:"
echo "   - 等待系统显示'已打开麦克风'后开始说话"
echo "   - 控制机器人: '机器人前进'、'机器人停止'等"
echo "   - 智能问答: 询问关于文档的任何问题"
echo "   - 退出: 按 Ctrl+C"
echo ""

# 启动系统
python3 dragon_robot_session.py