#!/usr/bin/env python3
"""
测试豆包API支持的音色ID
"""
import asyncio
import websockets
import json
import uuid

async def test_voice_ids():
    """测试不同音色ID"""
    
    # 测试音色列表
    test_voices = [
        "zh_female_qingxin",
        "zh_male_chunhou", 
        "zh_female_qinhe",
        "zh_male_chunzhen",
        "zh_female_tianmei",
        "BV001",
        "BV700",
        "BV705", 
        "BV406",
        "default"
    ]
    
    headers = {
        'X-Api-App-ID': '3618281145',
        'X-Api-Access-Key': 'JLBO_LeiDxgcYsXYKSTrpoqEkNnXpDKF',
        'X-Api-Resource-Id': 'volc.speech.dialog',
        'X-Api-App-Key': 'PlgvMymc7f3tQnJ6',
        'X-Api-Connect-Id': str(uuid.uuid4())
    }
    
    url = "wss://openspeech.bytedance.com/api/v3/realtime/dialogue"
    
    for voice_id in test_voices:
        print(f"\n🎵 测试音色: {voice_id}")
        try:
            async with websockets.connect(url, additional_headers=headers) as websocket:
                # 发送连接请求
                start_connection = {
                    "message_type": "CLIENT_REQUEST",
                    "event": 50,
                    "payload_msg": {}
                }
                await websocket.send(json.dumps(start_connection))
                response = await websocket.recv()
                print(f"连接响应: {response}")
                
                # 发送会话配置
                start_session = {
                    "message_type": "CLIENT_REQUEST", 
                    "event": 1,
                    "payload_msg": {
                        "mode": "dialogue",
                        "vad_config": {
                            "silence_timeout": 1000,
                            "speech_timeout": 10000,
                            "silence_dur_threshold": 800
                        },
                        "asr_config": {
                            "add_punctuation": True,
                            "language": "zh-CN",
                            "max_duration": 60000,
                            "sample_rate": 16000,
                            "vad_enable": True
                        },
                        "tts_config": {
                            "audio_config": {
                                "channel": 1,
                                "format": "pcm",
                                "sample_rate": 24000
                            },
                            "speaker": voice_id,  # 测试这个音色ID
                            "speed_ratio": 1.0,
                            "volume_ratio": 1.0,
                            "pitch_ratio": 1.0
                        },
                        "llm_config": {
                            "model": "ep-20241226194143-n47bs",
                            "system": "你是助手",
                            "stream": True,
                            "temperature": 0.7,
                            "max_tokens": 800
                        }
                    }
                }
                
                await websocket.send(json.dumps(start_session))
                response = await websocket.recv()
                response_data = json.loads(response)
                
                if 'payload_msg' in response_data and 'error' in response_data['payload_msg']:
                    print(f"❌ 错误: {response_data['payload_msg']['error']}")
                else:
                    print(f"✅ 音色 {voice_id} 测试成功!")
                    
        except Exception as e:
            print(f"❌ 测试音色 {voice_id} 失败: {e}")
        
        await asyncio.sleep(1)  # 等待一秒

if __name__ == "__main__":
    asyncio.run(test_voice_ids())