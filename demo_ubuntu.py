#!/usr/bin/env python3
"""
AgentOnRobot 简单演示 - Ubuntu 22.04
"""

import os
import sys

# 添加项目路径
project_root = "/home/raymond/AgentOnRobot-main"
sys.path.insert(0, project_root)
os.chdir(project_root)

from utils.agent import call_agent
from utils.tts import speak
import json

def demo_conversation():
    """演示对话功能"""
    print("=== AgentOnRobot 功能演示 ===")
    print("这是一个智能机器人助手，支持自然语言对话和机器人控制")
    print("\n演示内容:")
    print("1. 普通对话")
    print("2. 机器人控制指令")
    print("3. 语音合成")
    print("-" * 50)
    
    # 演示对话
    test_inputs = [
        "你好",
        "你能做什么",
        "抬起左手",
        "放下右手",
        "说话"
    ]
    
    for i, user_input in enumerate(test_inputs, 1):
        print(f"\n[演示 {i}] 用户: {user_input}")
        
        # 调用AI代理
        reply = call_agent(user_input)
        print(f"[机器人] {reply.text}")
        
        # 显示命令（如果有）
        if reply.commands:
            print(f"[执行命令] {json.dumps(reply.commands, ensure_ascii=False, indent=2)}")
        
        # 语音合成
        try:
            speak(reply.text)
        except:
            pass  # 如果TTS失败就跳过
        
        # 短暂暂停
        import time
        time.sleep(1)
    
    print("\n" + "=" * 50)
    print("演示完成！")
    print("\n项目功能概览:")
    print("✓ 自然语言理解和对话")
    print("✓ 机器人控制指令解析")
    print("✓ 语音合成输出")
    print("✓ 本地降级模式（无需云端API）")
    print("✓ Ubuntu 22.04 完全兼容")
    
    print("\n要使用完整功能，请:")
    print("1. 配置豆包(Doubao) API密钥在.env文件中")
    print("2. 运行 python3 main_voice_agent.py 进行交互")
    print("3. 连接ROS2机器人系统进行实际控制")

if __name__ == "__main__":
    demo_conversation()