#!/usr/bin/env python3
"""
Dragon机器人音色管理工具
用于管理和切换不同的音色配置
"""

import sys
import argparse
from voice_config import VoiceConfig

def show_current_config(voice_config):
    """显示当前音色配置"""
    current = voice_config.get_current_config()
    voice_id = current["speaker"]
    voice_info = voice_config.get_voice_info(voice_id)
    params = current["voice_params"]
    
    print("🎵 当前音色配置")
    print("=" * 50)
    print(f"🎭 音色ID: {voice_id}")
    print(f"📝 音色名称: {voice_info.get('name', '未知')}")
    print(f"👤 性别: {voice_info.get('gender', '未知')}")
    print(f"🎨 风格: {voice_info.get('style', '未知')}")
    print(f"🎬 推荐场景: {', '.join(voice_info.get('recommended_scenes', []))}")
    print(f"\n⚙️ 语音参数:")
    print(f"  • 语速: {params['speed_ratio']}")
    print(f"  • 音量: {params['volume_ratio']}")
    print(f"  • 音调: {params['pitch_ratio']}")

def list_all_voices(voice_config):
    """列出所有可用音色"""
    voices = voice_config.get_all_voices()
    
    print("🎵 所有可用音色")
    print("=" * 60)
    
    # 按性别分组显示
    genders = {"female": "👩 女声", "male": "👨 男声", "child": "👶 童声", "senior": "👴 老年"}
    
    for gender, title in genders.items():
        gender_voices = voice_config.get_voices_by_gender(gender)
        if gender_voices:
            print(f"\n{title}:")
            for voice_id, info in gender_voices.items():
                print(f"  🎭 {voice_id}")
                print(f"     名称: {info['name']}")
                print(f"     风格: {info['style']}")
                print(f"     场景: {', '.join(info['recommended_scenes'])}")
                print()

def set_voice_config(voice_config, voice_id, speed=None, volume=None, pitch=None):
    """设置音色配置"""
    try:
        # 验证音色是否存在
        if voice_id not in voice_config.get_all_voices():
            print(f"❌ 错误: 不支持的音色 '{voice_id}'")
            print("💡 使用 'list' 命令查看所有可用音色")
            return False
        
        # 设置音色
        voice_config.set_voice(voice_id, speed=speed, volume=volume, pitch=pitch)
        
        # 显示设置结果
        voice_info = voice_config.get_voice_info(voice_id)
        print(f"✅ 音色已切换到: {voice_info['name']} ({voice_id})")
        
        if speed is not None:
            print(f"🏃 语速设置为: {speed}")
        if volume is not None:
            print(f"🔊 音量设置为: {volume}")
        if pitch is not None:
            print(f"🎵 音调设置为: {pitch}")
        
        return True
        
    except Exception as e:
        print(f"❌ 设置失败: {e}")
        return False

def show_scenario_recommendations(voice_config):
    """显示场景推荐音色"""
    scenarios = voice_config.scenario_voices
    
    print("🎬 场景音色推荐")
    print("=" * 50)
    
    for scenario, voice_id in scenarios.items():
        voice_info = voice_config.get_voice_info(voice_id)
        scenario_names = {
            "default": "🏠 默认场景",
            "industrial": "🏭 工业场景", 
            "home": "🏠 家庭场景",
            "education": "🎓 教育场景",
            "business": "🏢 商务场景",
            "child": "👶 儿童场景",
            "senior": "👴 老年场景"
        }
        
        scenario_name = scenario_names.get(scenario, f"📍 {scenario}")
        print(f"{scenario_name}: {voice_info.get('name', voice_id)} ({voice_id})")

def test_voice_preview(voice_config, voice_id):
    """测试音色预览"""
    if voice_id not in voice_config.get_all_voices():
        print(f"❌ 错误: 不支持的音色 '{voice_id}'")
        return
    
    voice_info = voice_config.get_voice_info(voice_id)
    preview_text = voice_config.get_voice_preview_text(voice_id)
    
    print(f"🎭 音色预览: {voice_info['name']}")
    print("=" * 50)
    print(f"📝 预览文本:")
    print(f"   {preview_text}")
    print(f"\n💡 提示: 在实际系统中，这段文字会用 {voice_info['name']} 播放")

def backup_config(voice_config):
    """备份当前配置"""
    import json
    from datetime import datetime
    
    config = voice_config.get_current_config()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"voice_config_backup_{timestamp}.json"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        print(f"✅ 配置已备份到: {filename}")
    except Exception as e:
        print(f"❌ 备份失败: {e}")

def restore_config(voice_config, filename):
    """恢复配置"""
    import json
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 验证配置格式
        required_keys = ["speaker", "audio_config", "voice_params"]
        if not all(key in config for key in required_keys):
            print(f"❌ 配置文件格式错误")
            return
        
        # 应用配置
        voice_config.current_config = config
        voice_info = voice_config.get_voice_info(config["speaker"])
        print(f"✅ 配置已恢复: {voice_info.get('name', config['speaker'])}")
        
    except FileNotFoundError:
        print(f"❌ 文件不存在: {filename}")
    except Exception as e:
        print(f"❌ 恢复失败: {e}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Dragon机器人音色管理工具")
    parser.add_argument("action", choices=[
        "show", "list", "set", "scenarios", "test", "backup", "restore"
    ], help="操作类型")
    
    parser.add_argument("voice_id", nargs="?", help="音色ID")
    parser.add_argument("--speed", type=float, help="语速 (0.5-2.0)")
    parser.add_argument("--volume", type=float, help="音量 (0.5-2.0)")
    parser.add_argument("--pitch", type=float, help="音调 (0.5-2.0)")
    parser.add_argument("--file", help="备份/恢复文件名")
    
    # 如果没有参数，显示帮助
    if len(sys.argv) == 1:
        parser.print_help()
        return
    
    args = parser.parse_args()
    voice_config = VoiceConfig()
    
    try:
        if args.action == "show":
            show_current_config(voice_config)
            
        elif args.action == "list":
            list_all_voices(voice_config)
            
        elif args.action == "set":
            if not args.voice_id:
                print("❌ 错误: 请指定音色ID")
                print("💡 使用 'list' 命令查看所有可用音色")
                return
            set_voice_config(voice_config, args.voice_id, 
                           args.speed, args.volume, args.pitch)
            
        elif args.action == "scenarios":
            show_scenario_recommendations(voice_config)
            
        elif args.action == "test":
            if not args.voice_id:
                print("❌ 错误: 请指定要测试的音色ID")
                return
            test_voice_preview(voice_config, args.voice_id)
            
        elif args.action == "backup":
            backup_config(voice_config)
            
        elif args.action == "restore":
            if not args.file:
                print("❌ 错误: 请指定要恢复的配置文件")
                return
            restore_config(voice_config, args.file)
            
    except KeyboardInterrupt:
        print("\n👋 操作已取消")
    except Exception as e:
        print(f"❌ 操作失败: {e}")

if __name__ == "__main__":
    main()