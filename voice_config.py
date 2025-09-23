#!/usr/bin/env python3
"""
Dragon机器人音色配置系统
支持多种音色选择和个性化设置
"""

class VoiceConfig:
    """音色配置管理类"""
    
    def __init__(self):
        """初始化音色配置"""
        
        # ========== 可用音色列表 ==========
        self.available_voices = {
            # 女声音色
            "BV700_streaming": {
                "name": "温柔自然女声",
                "gender": "female",
                "style": "温柔、自然、适合日常对话",
                "recommended_scenes": ["家庭", "客服", "教育"]
            },
            "BV705_streaming": {
                "name": "甜美清新女声", 
                "gender": "female",
                "style": "甜美、清新、年轻活力",
                "recommended_scenes": ["教育", "娱乐", "儿童"]
            },
            "BV701_streaming": {
                "name": "专业播音女声",
                "gender": "female", 
                "style": "专业、正式、播音腔调",
                "recommended_scenes": ["商务", "新闻", "正式场合"]
            },
            
            # 男声音色
            "BV406_streaming": {
                "name": "沉稳磁性男声",
                "gender": "male",
                "style": "沉稳、磁性、成熟稳重", 
                "recommended_scenes": ["工业", "商务", "技术"]
            },
            "BV407_streaming": {
                "name": "年轻活力男声",
                "gender": "male",
                "style": "年轻、活力、朝气蓬勃",
                "recommended_scenes": ["运动", "娱乐", "青年"]
            },
            
            # 特殊音色
            "BV102_streaming": {
                "name": "童声音色",
                "gender": "child",
                "style": "童真、可爱、天真烂漫",
                "recommended_scenes": ["儿童教育", "童话", "游戏"]
            },
            "BV002_streaming": {
                "name": "老年音色", 
                "gender": "senior",
                "style": "慈祥、温和、长者风范",
                "recommended_scenes": ["老年关怀", "传统文化", "故事讲述"]
            }
        }
        
        # ========== 默认音色配置 ==========
        self.default_voice_config = {
            "speaker": "zh_male_yunzhou_jupiter_bigtts",  # 使用官方示例音色
            "audio_config": {
                "channel": 1,
                "format": "pcm", 
                "sample_rate": 24000
            },
            "voice_params": {
                "speed_ratio": 1.0,    # 语速 (0.5-2.0)
                "volume_ratio": 1.0,   # 音量 (0.5-2.0)
                "pitch_ratio": 1.0     # 音调 (0.5-2.0)
            }
        }
        
        # ========== 场景专用音色配置 ==========
        self.scenario_voices = {
            "default": "BV700_streaming",      # 默认场景
            "industrial": "BV406_streaming",   # 工业场景 - 沉稳男声
            "home": "BV700_streaming",         # 家庭场景 - 温柔女声
            "education": "BV705_streaming",    # 教育场景 - 甜美女声
            "business": "BV701_streaming",     # 商务场景 - 专业女声
            "child": "BV102_streaming",        # 儿童场景 - 童声
            "senior": "BV002_streaming"        # 老年场景 - 老年音色
        }
        
        # ========== 当前激活配置 ==========
        self.current_config = self.default_voice_config.copy()
        
    def get_voice_info(self, voice_id):
        """获取音色详细信息"""
        return self.available_voices.get(voice_id, {})
    
    def get_all_voices(self):
        """获取所有可用音色"""
        return self.available_voices
    
    def get_voices_by_gender(self, gender):
        """根据性别筛选音色"""
        return {k: v for k, v in self.available_voices.items() 
                if v.get("gender") == gender}
    
    def get_recommended_voice(self, scenario):
        """根据场景获取推荐音色"""
        return self.scenario_voices.get(scenario, self.scenario_voices["default"])
    
    def set_voice(self, voice_id, speed=None, volume=None, pitch=None):
        """设置音色和参数"""
        if voice_id not in self.available_voices:
            raise ValueError(f"不支持的音色: {voice_id}")
        
        # 更新音色
        self.current_config["speaker"] = voice_id
        
        # 更新语音参数
        if speed is not None:
            self.current_config["voice_params"]["speed_ratio"] = max(0.5, min(2.0, speed))
        if volume is not None:
            self.current_config["voice_params"]["volume_ratio"] = max(0.5, min(2.0, volume))
        if pitch is not None:
            self.current_config["voice_params"]["pitch_ratio"] = max(0.5, min(2.0, pitch))
        
        return self.current_config
    
    def get_current_config(self):
        """获取当前音色配置"""
        return self.current_config.copy()
    
    def get_config_for_tts(self):
        """获取用于TTS API的配置格式"""
        config = {
            "speaker": self.current_config["speaker"],
            "audio_config": self.current_config["audio_config"].copy()
        }
        
        # 添加语音参数（如果API支持）
        voice_params = self.current_config["voice_params"]
        if any(v != 1.0 for v in voice_params.values()):
            config["voice_params"] = voice_params
            
        return config
    
    def reset_to_default(self):
        """重置为默认配置"""
        self.current_config = self.default_voice_config.copy()
        return self.current_config
    
    def create_scenario_config(self, scenario, custom_params=None):
        """为特定场景创建配置"""
        voice_id = self.get_recommended_voice(scenario)
        config = self.default_voice_config.copy()
        config["speaker"] = voice_id
        
        # 应用自定义参数
        if custom_params:
            if "speed" in custom_params:
                config["voice_params"]["speed_ratio"] = custom_params["speed"]
            if "volume" in custom_params:
                config["voice_params"]["volume_ratio"] = custom_params["volume"] 
            if "pitch" in custom_params:
                config["voice_params"]["pitch_ratio"] = custom_params["pitch"]
        
        return config
    
    def get_voice_preview_text(self, voice_id):
        """获取音色预览文本"""
        voice_info = self.get_voice_info(voice_id)
        if not voice_info:
            return "你好，我是Dragon机器人助手。"
        
        # 根据音色特点生成预览文本
        style = voice_info.get("style", "")
        name = voice_info.get("name", "")
        
        preview_texts = {
            "温柔自然女声": "你好，我是Dragon机器人助手，很高兴为您服务。我的声音温柔自然，希望能带给您舒适的体验。",
            "甜美清新女声": "嗨！我是Dragon机器人助手！我有着甜美清新的声音，让我们一起开始愉快的对话吧！",
            "专业播音女声": "您好，我是Dragon机器人专业助手。我将以专业的服务态度，为您提供准确可靠的帮助。",
            "沉稳磁性男声": "您好，我是Dragon机器人助手。我拥有沉稳的声音，将为您提供可靠的技术支持。",
            "年轻活力男声": "你好！我是Dragon机器人助手！充满活力的声音，准备为您带来精彩的服务体验！",
            "童声音色": "小朋友你好！我是Dragon机器人小助手，我们一起来学习和游戏吧！",
            "老年音色": "您好，孩子。我是Dragon机器人助手，很高兴能够为您服务，请多多指教。"
        }
        
        return preview_texts.get(name, f"你好，我是{name}，很高兴为您服务。")

# ========== 全局实例 ==========
voice_config = VoiceConfig()

# ========== 便捷函数 ==========
def get_current_voice():
    """获取当前音色ID"""
    return voice_config.current_config["speaker"]

def set_voice(voice_id, **params):
    """设置音色"""
    return voice_config.set_voice(voice_id, **params)

def get_tts_config():
    """获取TTS配置"""
    return voice_config.get_config_for_tts()

def list_voices():
    """列出所有音色"""
    return voice_config.get_all_voices()

def get_scenario_voice(scenario):
    """获取场景推荐音色"""
    return voice_config.get_recommended_voice(scenario)

# ========== 使用示例 ==========
if __name__ == "__main__":
    # 创建配置实例
    vc = VoiceConfig()
    
    print("🎵 Dragon机器人音色配置系统")
    print("=" * 50)
    
    # 显示所有可用音色
    print("\n📋 可用音色列表:")
    for voice_id, info in vc.get_all_voices().items():
        print(f"  • {voice_id}: {info['name']} ({info['style']})")
    
    # 测试设置音色
    print(f"\n🎯 当前音色: {vc.get_current_config()['speaker']}")
    
    # 切换到男声
    vc.set_voice("BV406_streaming", speed=1.2)
    print(f"🔄 切换后音色: {vc.get_current_config()['speaker']}")
    
    # 获取TTS配置
    tts_config = vc.get_config_for_tts()
    print(f"🎙️ TTS配置: {tts_config}")
    
    # 场景推荐
    print(f"\n🎬 工业场景推荐音色: {vc.get_recommended_voice('industrial')}")
    print(f"🏠 家庭场景推荐音色: {vc.get_recommended_voice('home')}")