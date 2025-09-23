#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
豆包语音API配置模块
用于端到端语音模型的API封装
"""

import os
import json
import base64
import requests
import time
from typing import Optional, Dict, Any

class DoubaoVoiceAPI:
    """豆包语音API封装类 - 豆包实时语音模型"""
    
    def __init__(self, app_id: str = None, access_token: str = None, secret_key: str = None):
        """初始化豆包实时语音API"""
        # 豆包实时语音模型凭证
        self.app_id = app_id or "3618281145"
        self.access_token = access_token or "JLBO_LeiDxgcYsXYKSTrpoqEkNnXpDKF"
        self.secret_key = secret_key or "-d9bcajcaXRZg4810VoDzw8mQ_WMPOTQ"
        self.instance_id = "Doubao_scene_SLM_Doubao_realtime_voice_model2000000362790199362"
        
        # 豆包实时语音API端点
        self.base_url = "https://openspeech.bytedance.com/api/v1"
        self.realtime_asr_endpoint = f"{self.base_url}/asr/submit"  # 实时语音识别
        self.realtime_tts_endpoint = f"{self.base_url}/tts/submit"  # 实时语音合成
        
        # 备用端点
        self.fallback_asr_endpoint = "https://speech.volcengineapi.com/asr/v1/submit"
        self.fallback_tts_endpoint = "https://speech.volcengineapi.com/tts/v1/submit"
        
        # 默认配置
        self.default_asr_config = {
            "format": "wav",
            "sample_rate": 16000,
            "language": "zh-CN",
            "model": "general",
            "use_itn": True,  # 逆文本标准化
            "use_punc": True,  # 标点符号
            "max_silence": 800,  # 最大静音时长
            "nbest": 1
        }
        
        self.default_tts_config = {
            "voice": "zh_female_tianmei",  # 天美女声
            "format": "wav",
            "sample_rate": 16000,
            "speed": 1.0,
            "volume": 1.0,
            "pitch": 1.0,
            "emotion": "neutral"
        }
        
        # 会话状态
        self.session_id = None
        self.request_count = 0
        
    def _make_request(self, endpoint: str, payload: Dict[Any, Any], timeout: int = 30) -> Optional[Dict[Any, Any]]:
        """发送API请求 - 使用豆包实时语音模型认证"""
        # 豆包实时语音API认证方式
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'DragonEndToEndVoice/1.0',
            'Authorization': f'Bearer {self.access_token}',  # 使用Access Token
            'X-App-Id': self.app_id,                         # APP ID
            'X-Secret-Key': self.secret_key,                 # Secret Key
            'X-Instance-Id': self.instance_id                # 实例ID
        }
        
        # 在payload中添加实例信息
        payload.update({
            'app_id': self.app_id,
            'instance_id': self.instance_id,
            'timestamp': int(time.time() * 1000)
        })
        
        if self.session_id:
            headers['Session-ID'] = self.session_id
            payload['session_id'] = self.session_id
            
        self.request_count += 1
        
        try:
            print(f"🔗 调用豆包实时语音API: {endpoint}")
            print(f"📦 请求头: App-Id={self.app_id}, Instance={self.instance_id[:20]}...")
            
            response = requests.post(
                endpoint, 
                headers=headers, 
                json=payload, 
                timeout=timeout
            )
            
            print(f"📊 响应状态: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                
                # 更新会话ID
                if 'session_id' in result:
                    self.session_id = result['session_id']
                
                # 检查响应格式
                if 'code' in result and result['code'] == 0:
                    print("✅ 豆包实时语音API调用成功")
                    return result
                else:
                    print(f"⚠️  API返回错误: {result}")
                    return None
                    
            elif response.status_code == 401:
                print(f"❌ 认证失败 - 检查Access Token和凭证")
                print(f"错误详情: {response.text}")
                return None
            else:
                print(f"❌ API请求失败: {response.status_code}")
                print(f"错误详情: {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            print("❌ API请求超时")
            return None
        except requests.exceptions.RequestException as e:
            print(f"❌ API请求异常: {e}")
            return None
    
    def speech_to_text(self, audio_data: bytes, config: Dict[Any, Any] = None) -> Optional[str]:
        """语音转文字 - 豆包实时语音识别"""
        print("🔄 调用豆包实时语音识别API...")
        
        # 合并配置
        asr_config = {**self.default_asr_config}
        if config:
            asr_config.update(config)
        
        # 编码音频数据
        try:
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        except Exception as e:
            print(f"❌ 音频编码失败: {e}")
            return None
        
        # 构建请求负载 - 豆包实时语音识别格式
        payload = {
            "audio_data": audio_base64,
            "audio_format": asr_config.get("format", "wav"),
            "sample_rate": asr_config.get("sample_rate", 16000),
            "language": asr_config.get("language", "zh-CN"),
            "model": "realtime_asr",  # 实时语音识别模型
            "enable_punctuation": asr_config.get("use_punc", True),
            "enable_itn": asr_config.get("use_itn", True),
            "max_silence_ms": asr_config.get("max_silence", 800)
        }
        
        # 发送请求
        result = self._make_request(self.realtime_asr_endpoint, payload)
        
        if result and result.get('code') == 0:
            if 'data' in result and 'text' in result['data']:
                text = result['data']['text'].strip()
                confidence = result['data'].get('confidence', 0.0)
                
                print(f"✅ 识别结果: {text}")
                print(f"📊 置信度: {confidence:.2f}")
                
                return text if text else None
            else:
                print("⚠️  识别结果为空")
                return None
        else:
            print("❌ 豆包实时语音识别失败")
            return None
    
    def text_to_speech(self, text: str, config: Dict[Any, Any] = None) -> Optional[bytes]:
        """文字转语音 - 豆包实时语音合成"""
        print("🔊 调用豆包实时语音合成API...")
        
        if not text or not text.strip():
            print("⚠️  输入文本为空")
            return None
        
        # 合并配置
        tts_config = {**self.default_tts_config}
        if config:
            tts_config.update(config)
        
        # 构建请求负载 - 豆包实时语音合成格式
        payload = {
            "text": text.strip(),
            "voice_type": tts_config.get("voice", "zh_female_tianmei"),
            "audio_format": tts_config.get("format", "wav"),
            "sample_rate": tts_config.get("sample_rate", 16000),
            "speed": tts_config.get("speed", 1.0),
            "volume": tts_config.get("volume", 1.0),
            "pitch": tts_config.get("pitch", 1.0),
            "emotion": tts_config.get("emotion", "neutral"),
            "model": "realtime_tts"  # 实时语音合成模型
        }
        
        # 发送请求
        result = self._make_request(self.realtime_tts_endpoint, payload)
        
        if result and result.get('code') == 0:
            if 'data' in result and 'audio_data' in result['data']:
                audio_base64 = result['data']['audio_data']
                try:
                    audio_bytes = base64.b64decode(audio_base64)
                    print(f"✅ 语音合成成功: {len(audio_bytes)} 字节")
                    return audio_bytes
                except Exception as e:
                    print(f"❌ 音频解码失败: {e}")
                    return None
            else:
                print("⚠️  合成结果为空")
                return None
        else:
            print("❌ 豆包实时语音合成失败")
            return None
    
    def get_voice_list(self) -> Optional[list]:
        """获取可用语音列表"""
        endpoint = f"{self.base_url}/voices"
        result = self._make_request(endpoint, {})
        
        if result and 'data' in result:
            return result['data']
        return None
    
    def get_session_info(self) -> Dict[str, Any]:
        """获取会话信息"""
        return {
            "session_id": self.session_id,
            "request_count": self.request_count,
            "app_id": self.app_id,
            "instance_id": self.instance_id[:20] + "..." if self.instance_id else None,
            "access_token": self.access_token[:10] + "..." if self.access_token else None
        }

# 全局API实例 - 使用新的豆包实时语音凭证
doubao_voice_api = DoubaoVoiceAPI()

class DoubaoVoiceFallback:
    """豆包语音API降级方案"""
    
    def __init__(self):
        """初始化降级方案"""
        self.fallback_mode = True
        
    def speech_to_text(self, audio_data: bytes) -> Optional[str]:
        """降级：使用Google语音识别"""
        try:
            import speech_recognition as sr
            import io
            import wave
            
            # 将字节流转换为可识别格式
            audio_file = io.BytesIO(audio_data)
            
            recognizer = sr.Recognizer()
            with sr.AudioFile(audio_file) as source:
                audio = recognizer.record(source)
            
            # 尝试Google识别
            try:
                text = recognizer.recognize_google(audio, language='zh-CN')
                print(f"✅ [Fallback-Google] 识别结果: {text}")
                return text
            except sr.UnknownValueError:
                print("⚠️  [Fallback] 未识别到语音")
                return None
            except sr.RequestError as e:
                print(f"❌ [Fallback] Google API错误: {e}")
                return None
                
        except ImportError:
            print("❌ [Fallback] 缺少speech_recognition库")
            return None
        except Exception as e:
            print(f"❌ [Fallback] 降级识别失败: {e}")
            return None
    
    def text_to_speech(self, text: str) -> bool:
        """降级：文字输出"""
        print(f"🔊 [TTS-Fallback] {text}")
        return True

# 全局API实例
doubao_voice_api = DoubaoVoiceAPI()
fallback_api = DoubaoVoiceFallback()

def get_voice_api(use_fallback: bool = False):
    """获取语音API实例"""
    if use_fallback:
        return fallback_api
    return doubao_voice_api
