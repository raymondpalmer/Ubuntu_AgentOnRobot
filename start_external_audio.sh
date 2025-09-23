#!/bin/bash
# Dragon机器人 - 外接音频设备专用启动脚本

echo "🎧 Dragon机器人外接音频设备版本"
echo "====================================="

# 切换到正确目录
cd /home/ray/agent

# 设置外接设备音频环境
echo "🔧 配置外接音频设备..."
export PULSE_SERVER="unix:/mnt/wslg/PulseServer"
export PULSE_RUNTIME_PATH="$XDG_RUNTIME_DIR/pulse"

# 强制激活和优化外接设备
echo "⚡ 激活外接音频设备..."
pactl set-sink-mute RDPSink false 2>/dev/null || true
pactl set-sink-volume RDPSink 100% 2>/dev/null || true
pactl set-source-mute RDPSource false 2>/dev/null || true  
pactl set-source-volume RDPSource 100% 2>/dev/null || true
pactl set-default-sink RDPSink 2>/dev/null || true
pactl set-default-source RDPSource 2>/dev/null || true

# 检查音频设备状态
if pactl info > /dev/null 2>&1; then
    echo "✅ 外接音频设备配置完成"
    echo "🔊 默认输出: $(pactl get-default-sink)"
    echo "🎤 默认输入: $(pactl get-default-source)"
else
    echo "⚠️ 音频设备配置异常，但系统仍可尝试运行"
fi

echo ""
echo "🚀 启动Dragon机器人系统（外接设备优化版）..."
echo ""
echo "💡 外接设备使用提示:"
echo "   ✓ 系统已针对外接声卡和麦克风进行优化"
echo "   ✓ 使用直接音频播放方式，兼容性更好"
echo "   ✓ 如果仍无声音，请检查Windows默认设备设置"
echo "   ✓ 建议将外接设备设为Windows默认播放/录制设备"
echo ""
echo "🎯 测试步骤:"
echo "   1. 等待系统显示'已打开麦克风'提示"
echo "   2. 对着外接麦克风说: '你好机器人'"
echo "   3. 听外接扬声器是否有回应"
echo "   4. 如有问题请先运行: python3 audio_diagnosis.py"
echo ""

# 启动系统
python3 dragon_robot_session.py