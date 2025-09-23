#!/usr/bin/env python3
"""
外接音频设备专用配置覆盖
为Dragon机器人系统优化外接设备支持
"""

import sys
import os

# 添加官方示例路径
official_example_path = '/home/ray/agent/official_example'
if official_example_path not in sys.path:
    sys.path.insert(0, official_example_path)

import config
import pyaudio

def override_audio_config():
    """覆盖音频配置以适配外接设备"""
    print("🔧 应用外接设备音频配置...")
    
    # 优化输入配置（麦克风）
    config.input_audio_config = {
        "chunk": 1024,  # 减小chunk size以降低延迟
        "format": "pcm",
        "channels": 1,
        "sample_rate": 44100,  # 使用标准采样率
        "bit_size": pyaudio.paInt16
    }
    
    # 优化输出配置（扬声器）
    config.output_audio_config = {
        "chunk": 1024,
        "format": "pcm", 
        "channels": 2,  # 立体声输出
        "sample_rate": 44100,  # 匹配输入采样率
        "bit_size": pyaudio.paInt16  # 使用整数格式
    }
    
    # 更新TTS配置
    config.start_session_req["tts"]["audio_config"] = {
        "channel": 2,
        "format": "pcm",
        "sample_rate": 44100
    }
    
    print("✅ 外接设备音频配置已应用")
    print(f"🎤 输入: {config.input_audio_config['sample_rate']}Hz, {config.input_audio_config['channels']}ch")
    print(f"🔊 输出: {config.output_audio_config['sample_rate']}Hz, {config.output_audio_config['channels']}ch")

if __name__ == "__main__":
    override_audio_config()