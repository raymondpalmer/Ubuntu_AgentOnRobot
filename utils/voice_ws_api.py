#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
豆包实时语音WebSocket API模块
使用WebSocket连接实现真正的豆包实时语音交互
"""

import os
import json
import base64
import time
import uuid
import threading
from typing import Optional, Dict, Any, Callable
import websocket

try:
    import speech_recognition as sr
    HAS_SPEECH_RECOGNITION = True
except ImportError:
    HAS_SPEECH_RECOGNITION = False

class DoubaoRealtimeVoiceWS:
    """豆包实时语音WebSocket API"""
    
    def __init__(self, app_id: str = None, access_key: str = None):
        """初始化豆包实时语音WebSocket连接"""
        self.app_id = app_id or "3618281145"
        self.access_key = access_key or "JLBO_LeiDxgcYsXYKSTrpoqEkNnXpDKF"
        
        # WebSocket连接信息
        self.ws_url = "wss://openspeech.bytedance.com/api/v3/realtime/dialogue"
        self.resource_id = "volc.speech.dialog"
        self.app_key = "PlgvMymc7f3tQnJ6"  # 固定值
        
        # 连接状态
        self.ws = None
        self.connected = False
        self.connect_id = str(uuid.uuid4())
        
        # 音频配置
        self.sample_rate = 16000
        self.channels = 1
        
        # 响应处理
        self.asr_result = None
        self.tts_result = None
        self.response_received = threading.Event()
        self.asr_received = threading.Event()
        self.tts_received = threading.Event()
        
        print("🌐 豆包实时语音WebSocket API初始化完成")
    
    def connect(self) -> bool:
        """建立WebSocket连接"""
        try:
            print("🔗 建立豆包实时语音WebSocket连接...")
            
            # 构建连接头
            headers = {
                "X-Api-App-ID": self.app_id,
                "X-Api-Access-Key": self.access_key,
                "X-Api-Resource-Id": self.resource_id,
                "X-Api-App-Key": self.app_key,
                "X-Api-Connect-Id": self.connect_id
            }
            
            print(f"📦 连接信息:")
            print(f"   App ID: {self.app_id}")
            print(f"   Connect ID: {self.connect_id}")
            print(f"   Resource ID: {self.resource_id}")
            
            # 创建WebSocket连接
            self.ws = websocket.WebSocketApp(
                self.ws_url,
                header=headers,
                on_open=self._on_open,
                on_message=self._on_message,
                on_error=self._on_error,
                on_close=self._on_close
            )
            
            # 启动连接线程
            wst = threading.Thread(target=self.ws.run_forever)
            wst.daemon = True
            wst.start()
            
            # 等待连接建立
            time.sleep(2)
            
            if self.connected:
                print("✅ WebSocket连接建立成功")
                return True
            else:
                print("❌ WebSocket连接失败")
                return False
                
        except Exception as e:
            print(f"❌ WebSocket连接异常: {e}")
            return False
    
    def _on_open(self, ws):
        """WebSocket连接打开回调"""
        print("🎉 豆包实时语音WebSocket连接已建立")
        self.connected = True
    
    def _on_message(self, ws, message):
        """WebSocket消息接收回调"""
        try:
            # 处理二进制数据
            if isinstance(message, bytes):
                # 尝试解码为UTF-8
                try:
                    message_str = message.decode('utf-8')
                    print(f"📨 收到二进制消息，已转换为文本: {len(message)} 字节")
                except UnicodeDecodeError:
                    # 如果是音频数据，直接存储二进制数据
                    print(f"📨 收到二进制音频数据: {len(message)} 字节")
                    self.tts_result = message  # 直接存储二进制数据
                    self.tts_received.set()
                    return
            else:
                message_str = message
            
            # 尝试解析JSON
            try:
                data = json.loads(message_str)
                print(f"📨 收到WebSocket JSON消息: {data.get('type', 'unknown')}")
            except json.JSONDecodeError:
                # 如果不是JSON，可能是纯文本响应
                print(f"📨 收到WebSocket文本消息: {message_str[:100]}...")
                
                # 简单的文本识别结果处理
                if len(message_str) > 0 and not message_str.startswith('{'):
                    self.asr_result = message_str.strip()
                    self.asr_received.set()
                    print(f"🎤 文本ASR结果: {self.asr_result}")
                return
            
            # 处理JSON消息
            # 处理豆包API响应格式
            if data.get('event') == 'asr' or data.get('event') == 'asr_result':
                # 豆包ASR响应
                if 'payload' in data and 'text' in data['payload']:
                    self.asr_result = data['payload']['text']
                    self.asr_received.set()
                    print(f"🎤 豆包ASR结果: {self.asr_result}")
                elif 'text' in data:
                    self.asr_result = data['text']
                    self.asr_received.set()
                    print(f"🎤 ASR结果: {self.asr_result}")
                elif 'result' in data and 'text' in data['result']:
                    self.asr_result = data['result']['text']
                    self.asr_received.set()
                    print(f"🎤 ASR结果: {self.asr_result}")
            
            # 处理豆包TTS响应
            elif data.get('event') == 'tts' or data.get('event') == 'tts_result':
                if 'payload' in data and 'audio_data' in data['payload']:
                    self.tts_result = data['payload']['audio_data']
                    self.tts_received.set()
                    print(f"🔊 豆包TTS结果: {len(self.tts_result)} 字节")
                elif 'audio_data' in data:
                    self.tts_result = data['audio_data']
                    self.tts_received.set()
                    print(f"🔊 TTS结果: {len(self.tts_result)} 字节")
                elif 'audio' in data:
                    self.tts_result = data['audio']
                    self.tts_received.set()
                    print(f"🔊 TTS结果: {len(self.tts_result)} 字节")
            
            # 处理错误消息
            elif data.get('type') == 'error' or 'error' in data:
                error_msg = data.get('error', data.get('message', str(data)))
                print(f"❌ WebSocket服务器错误: {error_msg}")
                self.response_received.set()
                self.asr_received.set()  # 解除等待
                self.tts_received.set()  # 解除等待
            
            # 处理确认消息
            elif data.get('type') == 'ack' or data.get('status') == 'success':
                print(f"✅ 请求确认: {data}")
                self.response_received.set()
            
            # 处理任何包含结果的消息
            else:
                print(f"📋 未知消息格式: {data}")
                # 如果消息中包含可能的识别结果，尝试提取
                for key in ['transcript', 'recognition', 'speech_result']:
                    if key in data:
                        self.asr_result = data[key]
                        self.asr_received.set()
                        print(f"🎤 提取ASR结果 ({key}): {self.asr_result}")
                        break
                
        except Exception as e:
            print(f"❌ 消息处理异常: {e}")
            print(f"💡 原始消息类型: {type(message)}")
            if isinstance(message, bytes):
                print(f"💡 二进制数据长度: {len(message)} 字节")
                print(f"💡 前10字节: {message[:10]}")
                # 如果是二进制数据且长度合理，可能是音频数据
                if len(message) > 100:  # 音频数据通常较大
                    print("💡 推测为音频数据，尝试直接存储")
                    self.tts_result = message
                    self.tts_received.set()
            else:
                print(f"💡 文本消息长度: {len(str(message))} 字符")
                print(f"💡 消息内容: {str(message)[:200]}...")
    
    def _on_error(self, ws, error):
        """WebSocket错误回调"""
        print(f"❌ WebSocket错误: {error}")
        self.connected = False
        # 解除所有等待
        self.asr_received.set()
        self.tts_received.set()
        self.response_received.set()
    
    def _on_close(self, ws, close_status_code, close_msg):
        """WebSocket关闭回调"""
        print(f"🔒 WebSocket连接已关闭: {close_status_code}, {close_msg}")
        self.connected = False
        # 解除所有等待
        self.asr_received.set()
        self.tts_received.set()
        self.response_received.set()
    
    def reconnect(self) -> bool:
        """重新连接WebSocket"""
        print("🔄 尝试重新连接WebSocket...")
        self.connected = False
        if self.ws:
            try:
                self.ws.close()
            except:
                pass
        
        # 重新生成连接ID
        self.connect_id = str(uuid.uuid4())
        return self.connect()
    
    def speech_to_text(self, audio_data: bytes) -> Optional[str]:
        """通过WebSocket进行语音识别"""
        # 暂时跳过WebSocket ASR，避免连接断开
        print("⚠️  WebSocket ASR暂时跳过，使用备用方案")
        return None
    
    def realtime_voice_chat(self, audio_data: bytes, text: str) -> Optional[bytes]:
        """实时语音对话 - 发送音频和文本，接收音频响应"""
        if not self.connected:
            print("⚠️  WebSocket未连接，尝试重新连接...")
            if not self.connect():
                return None
        
        try:
            print("🎙️ 发送实时语音对话请求...")
            
            # 构建豆包实时对话请求
            request_data = {
                "event": "dialog",
                "request_id": str(uuid.uuid4()),
                "payload": {
                    "audio_data": base64.b64encode(audio_data).decode('utf-8'),
                    "text": text,
                    "format": "wav",
                    "voice": "zh_female_tianmei",
                    "sample_rate": self.sample_rate
                },
                "timestamp": int(time.time() * 1000)
            }
            
            # 清除之前的结果
            self.tts_result = None
            self.tts_received.clear()
            
            # 发送请求
            self.ws.send(json.dumps(request_data))
            print("📤 实时语音对话请求已发送")
            
            # 等待音频响应
            if self.tts_received.wait(timeout=15):
                if self.tts_result and isinstance(self.tts_result, bytes):
                    print(f"✅ 收到音频响应: {len(self.tts_result)} 字节")
                    return self.tts_result
                else:
                    print("⚠️  未收到有效音频响应")
                    return None
            else:
                print("⏰ 实时语音对话请求超时")
                return None
                
        except Exception as e:
            print(f"❌ 实时语音对话异常: {e}")
            return None
    
    def text_to_speech(self, text: str) -> Optional[bytes]:
        """通过WebSocket进行语音合成"""
        # 暂时跳过WebSocket TTS，避免连接断开
        print("⚠️  WebSocket TTS暂时跳过，使用备用方案")
        return None
    
    def disconnect(self):
        """断开WebSocket连接"""
        if self.ws:
            self.ws.close()
            self.connected = False
            print("🔒 WebSocket连接已断开")
    
    def get_session_info(self) -> Dict[str, Any]:
        """获取会话信息"""
        return {
            "app_id": self.app_id,
            "connect_id": self.connect_id,
            "connected": self.connected,
            "ws_url": self.ws_url,
            "access_key": self.access_key[:10] + "..." if self.access_key else None
        }

class DoubaoVoiceFallbackWS:
    """豆包语音WebSocket备用方案"""
    
    def __init__(self):
        """初始化备用方案"""
        self.fallback_mode = True
        
        if HAS_SPEECH_RECOGNITION:
            self.recognizer = sr.Recognizer()
            # 调整识别器参数
            self.recognizer.energy_threshold = 4000
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.pause_threshold = 0.8
            self.recognizer.phrase_threshold = 0.3
            print("✅ 语音识别备用方案已准备")
        else:
            self.recognizer = None
            print("⚠️  语音识别库不可用，将使用手动输入")
    
    def speech_to_text(self, audio_data: bytes) -> Optional[str]:
        """备用语音识别"""
        if not HAS_SPEECH_RECOGNITION or not self.recognizer:
            print("💭 语音识别不可用，请手动输入:")
            text = input("👤 > ").strip()
            return text if text else None
        
        try:
            import tempfile
            import wave
            import io
            
            print("🔄 [Fallback] 使用Google语音识别...")
            
            # 创建临时WAV文件
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_path = temp_file.name
            
            # 使用语音识别
            with sr.AudioFile(temp_path) as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.record(source)
            
            # 清理临时文件
            os.unlink(temp_path)
            
            # 尝试Google识别
            text = self.recognizer.recognize_google(audio, language='zh-CN')
            print(f"✅ [Fallback-Google] 识别结果: {text}")
            return text
            
        except sr.UnknownValueError:
            print("⚠️  [Fallback] 未识别到有效语音")
            return None
        except sr.RequestError as e:
            print(f"❌ [Fallback] Google API错误: {e}")
            return None
        except Exception as e:
            print(f"❌ [Fallback] 识别异常: {e}")
            return None
    
    def text_to_speech(self, text: str) -> bool:
        """备用语音合成"""
        print(f"🔊 [TTS-Fallback] {text}")
        
        # 尝试系统TTS
        try:
            import subprocess
            subprocess.run(['espeak', '-v', 'zh', '-s', '150', text], 
                          check=False, capture_output=True)
            return True
        except (FileNotFoundError, subprocess.CalledProcessError):
            pass
        
        return True

# 全局实例
doubao_realtime_ws = DoubaoRealtimeVoiceWS()
fallback_ws = DoubaoVoiceFallbackWS()

def get_realtime_voice_api(use_fallback: bool = False):
    """获取实时语音API实例"""
    if use_fallback:
        return fallback_ws
    return doubao_realtime_ws
