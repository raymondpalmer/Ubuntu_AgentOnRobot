#!/usr/bin/env python3
"""
Dragon机器人音色配置演示脚本
展示如何使用和测试不同的音色配置
"""

import sys
import asyncio
from voice_config import VoiceConfig

def demo_basic_voice_config():
    """演示基本音色配置功能"""
    print("🎵 Dragon机器人音色配置演示")
    print("=" * 60)
    
    # 创建音色配置实例
    voice_config = VoiceConfig()
    
    # 1. 显示所有可用音色
    print("\n📋 所有可用音色:")
    voices = voice_config.get_all_voices()
    for voice_id, info in voices.items():
        print(f"  🎭 {voice_id}: {info['name']}")
        print(f"     风格: {info['style']}")
        print(f"     场景: {', '.join(info['recommended_scenes'])}")
        print()
    
    # 2. 显示当前配置
    current = voice_config.get_current_config()
    print(f"🎯 当前音色: {current['speaker']}")
    
    # 3. 测试不同音色切换
    print("\n🔄 音色切换演示:")
    test_voices = ["BV700_streaming", "BV406_streaming", "BV705_streaming"]
    
    for voice_id in test_voices:
        voice_config.set_voice(voice_id)
        voice_info = voice_config.get_voice_info(voice_id)
        preview_text = voice_config.get_voice_preview_text(voice_id)
        
        print(f"\n  🎭 {voice_info['name']} ({voice_id}):")
        print(f"     预览: {preview_text}")

def demo_scenario_voices():
    """演示场景专用音色"""
    print("\n\n🎬 场景音色演示")
    print("=" * 60)
    
    voice_config = VoiceConfig()
    scenarios = {
        "industrial": "🏭 工业场景",
        "home": "🏠 家庭场景", 
        "education": "🎓 教育场景",
        "business": "🏢 商务场景"
    }
    
    for scenario, name in scenarios.items():
        recommended_voice = voice_config.get_recommended_voice(scenario)
        voice_info = voice_config.get_voice_info(recommended_voice)
        
        print(f"\n{name}:")
        print(f"  推荐音色: {voice_info['name']} ({recommended_voice})")
        print(f"  风格特点: {voice_info['style']}")
        
        # 创建场景配置
        scenario_config = voice_config.create_scenario_config(scenario)
        print(f"  TTS配置: {scenario_config['speaker']}")

def demo_voice_parameters():
    """演示音色参数调节"""
    print("\n\n⚙️ 音色参数调节演示")
    print("=" * 60)
    
    voice_config = VoiceConfig()
    
    # 测试不同参数组合
    test_configs = [
        {"voice": "BV700_streaming", "speed": 1.0, "volume": 1.0, "pitch": 1.0, "desc": "标准配置"},
        {"voice": "BV700_streaming", "speed": 1.5, "volume": 1.2, "pitch": 1.1, "desc": "快速活泼"},
        {"voice": "BV406_streaming", "speed": 0.8, "volume": 1.0, "pitch": 0.9, "desc": "沉稳缓慢"},
        {"voice": "BV705_streaming", "speed": 1.2, "volume": 1.1, "pitch": 1.2, "desc": "甜美欢快"}
    ]
    
    for config in test_configs:
        voice_config.set_voice(
            config["voice"], 
            speed=config["speed"], 
            volume=config["volume"], 
            pitch=config["pitch"]
        )
        
        voice_info = voice_config.get_voice_info(config["voice"])
        current_config = voice_config.get_current_config()
        params = current_config["voice_params"]
        
        print(f"\n  🎛️ {config['desc']}:")
        print(f"     音色: {voice_info['name']}")
        print(f"     语速: {params['speed_ratio']}")
        print(f"     音量: {params['volume_ratio']}")
        print(f"     音调: {params['pitch_ratio']}")

def demo_voice_integration():
    """演示与主系统的集成"""
    print("\n\n🔗 主系统集成演示")
    print("=" * 60)
    
    try:
        # 模拟主系统集成
        print("📡 模拟主系统音色配置...")
        
        voice_config = VoiceConfig()
        
        # 测试配置应用
        tts_config = voice_config.get_config_for_tts()
        print(f"✅ TTS配置生成成功:")
        print(f"   音色: {tts_config['speaker']}")
        if 'voice_params' in tts_config:
            print(f"   参数: {tts_config['voice_params']}")
        
        # 测试场景切换
        print(f"\n🎬 场景切换测试:")
        scenarios = ["industrial", "home", "education"]
        
        for scenario in scenarios:
            recommended = voice_config.get_recommended_voice(scenario)
            voice_info = voice_config.get_voice_info(recommended)
            print(f"   {scenario}: {voice_info['name']} ({recommended})")
        
        print("✅ 集成演示完成")
        
    except Exception as e:
        print(f"❌ 集成演示失败: {e}")

def interactive_voice_demo():
    """交互式音色演示"""
    print("\n\n🎮 交互式音色演示")
    print("=" * 60)
    
    voice_config = VoiceConfig()
    
    while True:
        print("\n请选择操作:")
        print("1. 查看所有音色")
        print("2. 切换音色")
        print("3. 调整参数")
        print("4. 场景推荐")
        print("5. 预览音色")
        print("0. 退出")
        
        try:
            choice = input("\n输入选择 (0-5): ").strip()
            
            if choice == "0":
                print("👋 演示结束")
                break
                
            elif choice == "1":
                voices = voice_config.get_all_voices()
                print("\n🎭 所有可用音色:")
                for voice_id, info in voices.items():
                    current_mark = " ← 当前" if voice_id == voice_config.get_current_config()["speaker"] else ""
                    print(f"   {voice_id}: {info['name']}{current_mark}")
                    
            elif choice == "2":
                voice_id = input("输入音色ID: ").strip()
                if voice_id in voice_config.get_all_voices():
                    voice_config.set_voice(voice_id)
                    voice_info = voice_config.get_voice_info(voice_id)
                    print(f"✅ 已切换到: {voice_info['name']}")
                else:
                    print("❌ 无效的音色ID")
                    
            elif choice == "3":
                try:
                    speed = float(input("输入语速 (0.5-2.0, 当前不变请按回车): ") or voice_config.get_current_config()["voice_params"]["speed_ratio"])
                    volume = float(input("输入音量 (0.5-2.0, 当前不变请按回车): ") or voice_config.get_current_config()["voice_params"]["volume_ratio"])
                    pitch = float(input("输入音调 (0.5-2.0, 当前不变请按回车): ") or voice_config.get_current_config()["voice_params"]["pitch_ratio"])
                    
                    current_voice = voice_config.get_current_config()["speaker"]
                    voice_config.set_voice(current_voice, speed=speed, volume=volume, pitch=pitch)
                    print("✅ 参数已更新")
                    
                except ValueError:
                    print("❌ 参数格式错误")
                    
            elif choice == "4":
                scenario = input("输入场景 (industrial/home/education/business): ").strip()
                if scenario in voice_config.scenario_voices:
                    recommended = voice_config.get_recommended_voice(scenario)
                    voice_info = voice_config.get_voice_info(recommended)
                    print(f"🎬 {scenario}场景推荐: {voice_info['name']} ({recommended})")
                    
                    if input("是否切换到这个音色? (y/n): ").strip().lower() == 'y':
                        voice_config.set_voice(recommended)
                        print("✅ 已切换")
                else:
                    print("❌ 无效的场景")
                    
            elif choice == "5":
                voice_id = input("输入要预览的音色ID: ").strip()
                if voice_id in voice_config.get_all_voices():
                    preview_text = voice_config.get_voice_preview_text(voice_id)
                    voice_info = voice_config.get_voice_info(voice_id)
                    print(f"\n🎭 {voice_info['name']} 预览:")
                    print(f"   {preview_text}")
                else:
                    print("❌ 无效的音色ID")
                    
            else:
                print("❌ 无效选择")
                
        except KeyboardInterrupt:
            print("\n👋 演示结束")
            break
        except Exception as e:
            print(f"❌ 操作失败: {e}")

def main():
    """主函数"""
    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        interactive_voice_demo()
    else:
        # 运行所有演示
        demo_basic_voice_config()
        demo_scenario_voices()
        demo_voice_parameters()
        demo_voice_integration()
        
        print("\n" + "=" * 60)
        print("🎵 音色配置演示完成！")
        print("\n💡 提示:")
        print("   - 运行 'python3 voice_demo.py interactive' 进入交互模式")
        print("   - 使用 'python3 voice_manager.py' 管理音色配置")
        print("   - 在dragon_robot_session.py中调用 update_voice_config() 切换音色")

if __name__ == "__main__":
    main()