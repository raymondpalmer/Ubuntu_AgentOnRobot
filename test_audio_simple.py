#!/usr/bin/env python3
"""
简单的音频测试脚本，测试Ubuntu环境下的音频功能
"""

import sys
import os

def test_pyaudio():
    """测试PyAudio"""
    try:
        import pyaudio
        print("✓ PyAudio 导入成功")
        
        # 获取音频设备信息
        p = pyaudio.PyAudio()
        print(f"音频设备数量: {p.get_device_count()}")
        
        # 列出音频设备
        for i in range(p.get_device_count()):
            info = p.get_device_info_by_index(i)
            print(f"设备 {i}: {info['name']} - 输入通道: {info['maxInputChannels']}, 输出通道: {info['maxOutputChannels']}")
        
        p.terminate()
        return True
    except Exception as e:
        print(f"✗ PyAudio 测试失败: {e}")
        return False

def test_speech_recognition():
    """测试语音识别"""
    try:
        import speech_recognition as sr
        print("✓ SpeechRecognition 导入成功")
        
        # 测试麦克风
        r = sr.Recognizer()
        mic_list = sr.Microphone.list_microphone_names()
        print(f"可用麦克风数量: {len(mic_list)}")
        for i, name in enumerate(mic_list):
            print(f"麦克风 {i}: {name}")
        
        return True
    except Exception as e:
        print(f"✗ SpeechRecognition 测试失败: {e}")
        return False

def test_pyttsx3():
    """测试文本转语音"""
    try:
        import pyttsx3
        print("✓ pyttsx3 导入成功")
        
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        print(f"可用语音数量: {len(voices) if voices else 0}")
        
        # 测试简单的语音合成
        engine.say("Hello, this is a test")
        engine.runAndWait()
        engine.stop()
        
        return True
    except Exception as e:
        print(f"✗ pyttsx3 测试失败: {e}")
        return False

def test_basic_imports():
    """测试基本模块导入"""
    modules = [
        'requests', 'json', 'asyncio', 'threading',
        'wave', 'io', 'time', 'subprocess'
    ]
    
    success = True
    for module in modules:
        try:
            __import__(module)
            print(f"✓ {module} 导入成功")
        except ImportError as e:
            print(f"✗ {module} 导入失败: {e}")
            success = False
    
    return success

if __name__ == "__main__":
    print("=== Ubuntu 环境音频和基础依赖测试 ===\n")
    
    print("1. 测试基础模块导入...")
    test_basic_imports()
    print()
    
    print("2. 测试PyAudio...")
    test_pyaudio()
    print()
    
    print("3. 测试语音识别...")
    test_speech_recognition()
    print()
    
    print("4. 测试文本转语音...")
    test_pyttsx3()
    print()
    
    print("=== 测试完成 ===")