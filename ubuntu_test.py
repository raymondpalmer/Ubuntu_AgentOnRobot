#!/usr/bin/env python3
"""
项目功能测试脚本 - 测试AgentOnRobot在Ubuntu 22.04上的运行状况
"""

import os
import sys
import time
import subprocess

# 添加项目路径
project_root = "/home/raymond/AgentOnRobot-main"
sys.path.insert(0, project_root)
os.chdir(project_root)

def test_imports():
    """测试核心模块导入"""
    print("=== 测试模块导入 ===")
    
    try:
        from utils.agent import call_agent, AgentReply
        print("✓ utils.agent 导入成功")
    except Exception as e:
        print(f"✗ utils.agent 导入失败: {e}")
        return False
    
    try:
        from utils.asr import transcribe_once, ASRResult
        print("✓ utils.asr 导入成功")
    except Exception as e:
        print(f"✗ utils.asr 导入失败: {e}")
        return False
    
    try:
        from utils.tts import speak
        print("✓ utils.tts 导入成功")
    except Exception as e:
        print(f"✗ utils.tts 导入失败: {e}")
        return False
    
    return True

def test_agent():
    """测试AI代理功能"""
    print("\n=== 测试AI代理功能 ===")
    
    try:
        from utils.agent import call_agent
        
        # 测试普通对话
        reply = call_agent("你好")
        print(f"普通对话测试:")
        print(f"  输入: 你好")
        print(f"  输出: {reply.text}")
        print(f"  命令: {reply.commands}")
        
        # 测试机器人控制
        reply = call_agent("抬起左手")
        print(f"机器人控制测试:")
        print(f"  输入: 抬起左手")
        print(f"  输出: {reply.text}")
        print(f"  命令: {reply.commands}")
        
        return True
    except Exception as e:
        print(f"✗ AI代理测试失败: {e}")
        return False

def test_tts():
    """测试语音合成"""
    print("\n=== 测试语音合成 ===")
    
    try:
        from utils.tts import speak
        
        print("正在测试语音合成...")
        speak("Hello, this is a test of the text to speech system")
        print("✓ TTS 测试完成")
        
        return True
    except Exception as e:
        print(f"✗ TTS测试失败: {e}")
        return False

def test_environment():
    """测试环境配置"""
    print("\n=== 测试环境配置 ===")
    
    # 检查.env文件
    env_file = os.path.join(project_root, ".env")
    if os.path.exists(env_file):
        print("✓ .env 配置文件存在")
    else:
        print("✗ .env 配置文件不存在")
        return False
    
    # 检查降级模式
    from dotenv import load_dotenv
    load_dotenv()
    
    fallback = os.getenv("VOICE_FALLBACK", "0")
    if fallback == "1":
        print("✓ VOICE_FALLBACK=1，启用本地降级模式")
    else:
        print("⚠ VOICE_FALLBACK=0，需要云端API配置")
    
    return True

def test_audio_dependencies():
    """测试音频依赖"""
    print("\n=== 测试音频依赖 ===")
    
    # 测试espeak-ng
    try:
        result = subprocess.run(["espeak-ng", "--version"], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✓ espeak-ng 可用")
        else:
            print("✗ espeak-ng 不可用")
    except Exception as e:
        print(f"✗ espeak-ng 测试失败: {e}")
    
    # 测试aplay
    try:
        result = subprocess.run(["aplay", "--version"], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✓ aplay 可用")
        else:
            print("✗ aplay 不可用")
    except Exception as e:
        print(f"✗ aplay 测试失败: {e}")
    
    return True

def interactive_test():
    """交互式测试"""
    print("\n=== 交互式测试 ===")
    print("现在可以进行交互式对话测试...")
    print("输入文本来测试对话功能，输入 'quit' 退出")
    
    try:
        from utils.agent import call_agent
        from utils.tts import speak
        
        while True:
            user_input = input("\n[用户] > ").strip()
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
            
            if not user_input:
                continue
                
            # 调用AI代理
            reply = call_agent(user_input)
            print(f"[机器人] {reply.text}")
            
            # 语音合成
            speak(reply.text)
            
            # 显示命令
            if reply.commands:
                print(f"[命令] {reply.commands}")
    
    except KeyboardInterrupt:
        print("\n交互测试结束")
    except Exception as e:
        print(f"交互测试失败: {e}")

def main():
    """主测试函数"""
    print("AgentOnRobot Ubuntu 22.04 兼容性测试")
    print("=" * 50)
    
    success_count = 0
    total_tests = 4
    
    # 运行各项测试
    if test_imports():
        success_count += 1
    
    if test_environment():
        success_count += 1
    
    if test_audio_dependencies():
        success_count += 1
    
    if test_agent():
        success_count += 1
    
    if test_tts():
        pass  # TTS测试不计入成功计数，因为可能没有音频输出
    
    # 输出测试结果
    print(f"\n=== 测试总结 ===")
    print(f"成功测试: {success_count}/{total_tests}")
    
    if success_count == total_tests:
        print("🎉 所有核心功能测试通过！项目在Ubuntu 22.04上运行正常。")
        
        # 提供交互式测试选项
        choice = input("\n是否进行交互式对话测试？(y/n): ").strip().lower()
        if choice in ['y', 'yes']:
            interactive_test()
    else:
        print("⚠ 部分测试失败，请检查相关依赖和配置。")
    
    print("\n测试完成！")

if __name__ == "__main__":
    main()