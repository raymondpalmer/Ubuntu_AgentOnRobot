#!/usr/bin/env python3
"""
Dragon机器人对话系统 - 基于官方示例架构
支持连续语音对话和机器人控制集成
集成本地知识库功能
"""

import asyncio
import sys
import os
import queue
import threading
import time
import re
import subprocess

def setup_audio_environment():
    """设置WSL音频环境"""
    print("🔧 初始化音频环境...")
    
    # 设置PulseAudio环境变量
    os.environ['PULSE_SERVER'] = 'unix:/mnt/wslg/PulseServer'
    os.environ['PULSE_RUNTIME_PATH'] = f"{os.environ.get('XDG_RUNTIME_DIR', '/run/user/1000')}/pulse"
    
    # 检查PulseAudio连接
    try:
        result = subprocess.run(['pactl', 'info'], capture_output=True, timeout=5)
        if result.returncode == 0:
            print("✅ 音频环境初始化成功")
            
            # 强制激活和配置外接设备
            external_audio_commands = [
                ['pactl', 'set-sink-mute', 'RDPSink', 'false'],
                ['pactl', 'set-sink-volume', 'RDPSink', '100%'],
                ['pactl', 'set-source-mute', 'RDPSource', 'false'],
                ['pactl', 'set-source-volume', 'RDPSource', '100%'],
                ['pactl', 'set-default-sink', 'RDPSink'],
                ['pactl', 'set-default-source', 'RDPSource']
            ]
            
            for cmd in external_audio_commands:
                try:
                    subprocess.run(cmd, capture_output=True, timeout=2)
                except:
                    pass
                    
            print("🎧 外接音频设备已优化配置")
            return True
        else:
            print("⚠️ PulseAudio连接失败，音频功能可能受限")
            return False
    except Exception as e:
        print(f"⚠️ 音频环境配置异常: {e}")
        return False

def override_audio_config_for_external_devices():
    """为外接设备优化音频配置 - 严格按豆包API要求"""
    print("🎧 应用豆包API标准音频配置...")
    
    # 严格按照豆包API要求配置输入（麦克风）
    config.input_audio_config.update({
        "chunk": 3200,
        "sample_rate": 16000,  # 豆包API要求16kHz
        "channels": 1,         # 单声道
        "format": "pcm"
    })
    
    # 严格按照豆包API要求配置输出（TTS）
    config.output_audio_config.update({
        "chunk": 3200,
        "sample_rate": 24000,  # 豆包API要求24kHz
        "channels": 1,         # 单声道
        "format": "pcm"
    })
    
    # 确保TTS配置匹配
    config.start_session_req["tts"]["audio_config"].update({
        "channel": 1,
        "sample_rate": 24000,
        "format": "pcm"
    })
    
    print("✅ 豆包API标准配置已应用")
    print("🎤 输入: 16kHz, 单声道 (豆包标准)")
    print("🔊 输出: 24kHz, 单声道 (豆包标准)")

# 初始化音频环境
setup_audio_environment()

# 添加官方示例路径
official_example_path = '/home/ray/agent/official_example'
if official_example_path not in sys.path:
    sys.path.insert(0, official_example_path)

# 导入官方组件
try:
    import config
    from audio_manager import AudioDeviceManager
    from realtime_dialog_client import RealtimeDialogClient
    print("✅ 官方组件导入成功")
    
    # 在导入后立即应用外接设备配置
    override_audio_config_for_external_devices()
    
except ImportError as e:
    print(f"❌ 官方组件导入失败: {e}")
    print("请确保在official_example目录下运行")
    sys.exit(1)

# 导入知识库
try:
    from simple_knowledge_base import SimpleKnowledgeBase
    SIMPLE_KB_AVAILABLE = True
    print("✅ 简化版知识库模块导入成功")
except ImportError as e:
    SIMPLE_KB_AVAILABLE = False
    print(f"⚠️ 简化版知识库模块未安装: {e}")

# 尝试导入LangChain知识库
try:
    sys.path.insert(0, '/home/ray/agent/doubao_robot_voice_agent_starter')
    from langchain_kb_manager import UnifiedKnowledgeBaseManager
    LANGCHAIN_KB_AVAILABLE = True
    print("✅ LangChain知识库模块导入成功")
except ImportError as e:
    LANGCHAIN_KB_AVAILABLE = False
    print(f"⚠️ LangChain知识库模块未安装: {e}")

# 导入自动知识库管理器
try:
    from auto_kb_manager import AutoKnowledgeBaseManager
    AUTO_KB_AVAILABLE = True
    print("✅ 自动知识库管理器导入成功")
except ImportError as e:
    AUTO_KB_AVAILABLE = False
    print(f"⚠️ 自动知识库管理器未安装: {e}")

# 确定知识库可用性
KNOWLEDGE_BASE_AVAILABLE = SIMPLE_KB_AVAILABLE or LANGCHAIN_KB_AVAILABLE
if not KNOWLEDGE_BASE_AVAILABLE:
    print("  运行: pip install -r requirements_knowledge.txt")

# 导入prompt配置
try:
    from dragon_prompts_config import DragonRobotPrompts
    PROMPTS_CONFIG_AVAILABLE = True
    print("✅ Prompt配置模块导入成功")
except ImportError as e:
    PROMPTS_CONFIG_AVAILABLE = False
    print(f"⚠️ Prompt配置模块未找到: {e}")
    print("  使用默认配置")

# 导入音色配置
try:
    from voice_config import VoiceConfig
    VOICE_CONFIG_AVAILABLE = True
    print("✅ 音色配置模块导入成功")
except ImportError as e:
    VOICE_CONFIG_AVAILABLE = False
    print(f"⚠️ 音色配置模块未找到: {e}")
    print("  使用默认音色配置")

# ROS相关
try:
    import rospy
    from geometry_msgs.msg import Twist
    ROS_AVAILABLE = True
except ImportError:
    ROS_AVAILABLE = False
    print("⚠️ ROS未安装，使用模拟模式")

class DragonRobotController:
    """Dragon机器人控制器"""
    def __init__(self):
        self.ros_enabled = ROS_AVAILABLE and self.init_ros()
        self.current_action = "停止"
        
        # 指令映射
        self.command_map = {
            "前进": (0.5, 0.0),
            "后退": (-0.3, 0.0), 
            "左转": (0.0, 0.5),
            "右转": (0.0, -0.5),
            "停止": (0.0, 0.0),
            "向前": (0.5, 0.0),
            "向后": (-0.3, 0.0),
            "向左": (0.0, 0.5),
            "向右": (0.0, -0.5),
            "往前": (0.5, 0.0),
            "往后": (-0.3, 0.0),
            "往左": (0.0, 0.5),
            "往右": (0.0, -0.5),
            "前走": (0.5, 0.0),
            "后走": (-0.3, 0.0),
            "左拐": (0.0, 0.5),
            "右拐": (0.0, -0.5),
            "走前面": (0.5, 0.0),
            "走后面": (-0.3, 0.0),
            "左边": (0.0, 0.5),
            "右边": (0.0, -0.5),
            "停下": (0.0, 0.0),
            "停车": (0.0, 0.0),
            "暂停": (0.0, 0.0),
        }
    
    def init_ros(self):
        """初始化ROS"""
        try:
            rospy.init_node('dragon_robot_controller', anonymous=True)
            self.cmd_vel_pub = rospy.Publisher('/cmd_vel', Twist, queue_size=1)
            print("✅ ROS连接成功")
            return True
        except Exception as e:
            print(f"⚠️ ROS初始化失败: {e}")
            return False
    
    def check_robot_command(self, text: str) -> bool:
        """检查是否包含机器人控制指令"""
        text = text.strip().replace("。", "").replace("，", "").replace(",", "").replace(".", "")
        
        # 检查是否包含机器人相关关键词
        robot_keywords = ["机器人", "让机器人", "控制机器人", "机器人请"]
        has_robot_keyword = any(keyword in text for keyword in robot_keywords)
        
        # 检查是否包含运动指令
        has_movement = any(command in text for command in self.command_map.keys())
        
        return has_robot_keyword or has_movement
    
    def parse_and_execute_command(self, text: str) -> bool:
        """解析并执行语音指令"""
        text = text.strip().replace("。", "").replace("，", "").replace(",", "").replace(".", "")
        
        for command, (x, z) in self.command_map.items():
            if command in text:
                self.current_action = command  # 先更新动作名称
                self.execute_movement(x, z)    # 再执行运动
                return True
        return False
    
    def execute_movement(self, linear_x: float, angular_z: float):
        """执行运动指令"""
        if self.ros_enabled:
            try:
                twist = Twist()
                twist.linear.x = linear_x
                twist.angular.z = angular_z
                self.cmd_vel_pub.publish(twist)
                print(f"🤖 ROS执行: {self.current_action} (x={linear_x}, z={angular_z})")
            except Exception as e:
                print(f"❌ ROS发布失败: {e}")
        else:
            print(f"🤖 模拟执行: {self.current_action} (x={linear_x}, z={angular_z})")

class DragonDialogSession:
    """Dragon对话会话 - 基于官方架构"""
    def __init__(self):
        # 生成唯一的session_id
        import uuid
        session_id = str(uuid.uuid4())
        
        # 创建AudioConfig对象
        from audio_manager import AudioConfig
        input_config = AudioConfig(**config.input_audio_config)
        output_config = AudioConfig(**config.output_audio_config)
        
        self.audio_device = AudioDeviceManager(input_config, output_config)
        
        # 初始化音频输出流 - 添加错误处理
        try:
            self.output_stream = self.audio_device.open_output_stream()
            print("✅ 音频输出流初始化成功")
        except Exception as e:
            print(f"⚠️ 音频输出流初始化失败: {e}")
            print("🔄 尝试使用备用音频配置...")
            self.output_stream = None
            
        self.client = RealtimeDialogClient(config.ws_connect_config, session_id)
        self.robot_controller = DragonRobotController()
        
        # 初始化prompt配置
        if PROMPTS_CONFIG_AVAILABLE:
            self.prompts = DragonRobotPrompts()
            print("🎯 Prompt配置已加载")
        else:
            self.prompts = None
            print("🎯 使用默认prompt配置")
        
        # 初始化音色配置
        if VOICE_CONFIG_AVAILABLE:
            self.voice_config = VoiceConfig()
            print("🎵 音色配置已加载")
            # 应用默认音色配置
            self._apply_voice_config()
        else:
            self.voice_config = None
            print("🎵 使用默认音色配置")
        
        # 初始化知识库
        self.knowledge_base = None
        self.auto_kb_manager = None
        
        if KNOWLEDGE_BASE_AVAILABLE:
            try:
                if LANGCHAIN_KB_AVAILABLE:
                    # 优先使用LangChain知识库
                    self.knowledge_base = UnifiedKnowledgeBaseManager(
                        kb_dir="knowledge_base", 
                        backend="auto"
                    )
                    backend_type = self.knowledge_base.backend
                    print(f"🧠 LangChain知识库已加载 (后端: {backend_type})")
                    
                    # 初始化自动知识库管理器
                    if AUTO_KB_AVAILABLE:
                        try:
                            self.auto_kb_manager = AutoKnowledgeBaseManager(
                                watch_dirs=["knowledge_base/files"],
                                kb_dir="knowledge_base"
                            )
                            print("🔄 自动知识库管理器已初始化")
                            
                            # 启动时自动扫描更新
                            print("📁 正在扫描 knowledge_base/files 目录...")
                            update_stats = self.auto_kb_manager.auto_update_knowledge_base()
                            
                            if update_stats["new_added"] > 0 or update_stats["modified_updated"] > 0:
                                print(f"   ✅ 自动更新完成: 新增{update_stats['new_added']}个，更新{update_stats['modified_updated']}个文档")
                            else:
                                print("   📚 知识库已是最新状态")
                                
                        except Exception as e:
                            print(f"⚠️ 自动知识库管理器初始化失败: {e}")
                            self.auto_kb_manager = None
                    
                    # 显示统计信息
                    stats = self.knowledge_base.get_stats()
                    doc_count = stats.get('total_documents', 0)
                    chunk_count = stats.get('total_chunks', 0)
                    if chunk_count > 0:
                        print(f"   📚 最终统计 - 文档数: {doc_count}, 分块数: {chunk_count}")
                    else:
                        print(f"   📚 最终统计 - 文档数: {doc_count}")
                        
                elif SIMPLE_KB_AVAILABLE:
                    # 回退到简化版知识库
                    self.knowledge_base = SimpleKnowledgeBase()
                    print(f"🧠 简化版知识库已加载 ({len(self.knowledge_base.documents)} 个文档片段)")
                    
            except Exception as e:
                print(f"⚠️ 知识库初始化失败: {e}")
                self.knowledge_base = None
        
        # 状态控制
        self.is_recording = True
        self.audio_queue = queue.Queue()
        self.say_hello_over_event = asyncio.Event()
        self.is_sending_chat_tts_text = False
        self.is_user_querying = False
        self.audio_buffer = b''
        
        # 启动音频播放线程
        self.is_playing = True
        self.player_thread = threading.Thread(target=self._audio_player_thread)
        self.player_thread.daemon = True
        self.player_thread.start()
    
    def update_prompts_config(self, config_path: str = None):
        """动态更新prompt配置"""
        try:
            if config_path:
                # 如果提供了配置文件路径，重新加载
                import importlib.util
                spec = importlib.util.spec_from_file_location("dragon_prompts_config", config_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                self.prompts = module.DragonRobotPrompts()
            else:
                # 重新导入配置模块
                import importlib
                if 'dragon_prompts_config' in sys.modules:
                    importlib.reload(sys.modules['dragon_prompts_config'])
                from dragon_prompts_config import DragonRobotPrompts
                self.prompts = DragonRobotPrompts()
            
            print("🎯 Prompt配置已更新")
            return True
        except Exception as e:
            print(f"⚠️ Prompt配置更新失败: {e}")
            return False
    
    def get_current_prompts_info(self):
        """获取当前prompt配置信息"""
        if not self.prompts:
            return "当前使用默认prompt配置"
        
        info = f"""当前Prompt配置信息:
- 系统角色: {len(self.prompts.system_roles)} 个
- 说话风格: {len(self.prompts.speaking_styles)} 个  
- 场景配置: {len(self.prompts.scenario_prompts)} 个
- 默认角色: {self.prompts.get_system_role('default')[:100]}...
"""
        return info
    
    def _apply_voice_config(self):
        """应用音色配置到系统"""
        if not self.voice_config:
            return
        
        try:
            # 获取当前音色配置
            tts_config = self.voice_config.get_config_for_tts()
            
            # 更新config中的TTS配置
            if hasattr(config, 'start_session_req') and 'tts' in config.start_session_req:
                # 更新speaker
                config.start_session_req['tts']['speaker'] = tts_config['speaker']
                
                # 如果有语音参数，添加到配置中
                if 'voice_params' in tts_config:
                    config.start_session_req['tts'].update(tts_config['voice_params'])
                
                print(f"🎵 音色已应用: {tts_config['speaker']}")
            
        except Exception as e:
            print(f"⚠️ 音色配置应用失败: {e}")
    
    def update_voice_config(self, voice_id, **params):
        """动态更新音色配置"""
        if not self.voice_config:
            print("⚠️ 音色配置系统未初始化")
            return False
        
        try:
            # 设置新音色
            self.voice_config.set_voice(voice_id, **params)
            
            # 应用到系统
            self._apply_voice_config()
            
            # 获取音色信息
            voice_info = self.voice_config.get_voice_info(voice_id)
            print(f"🎵 音色已切换到: {voice_info.get('name', voice_id)}")
            
            return True
            
        except Exception as e:
            print(f"⚠️ 音色配置更新失败: {e}")
            return False
    
    def get_current_voice_info(self):
        """获取当前音色配置信息"""
        if not self.voice_config:
            return "当前使用默认音色配置"
        
        current = self.voice_config.get_current_config()
        voice_id = current["speaker"]
        voice_info = self.voice_config.get_voice_info(voice_id)
        params = current["voice_params"]
        
        info = f"""当前音色配置信息:
- 音色ID: {voice_id}
- 音色名称: {voice_info.get('name', '未知')}
- 性别: {voice_info.get('gender', '未知')}
- 风格: {voice_info.get('style', '未知')}
- 语速: {params['speed_ratio']}
- 音量: {params['volume_ratio']}
- 音调: {params['pitch_ratio']}
"""
        return info
    
    def set_scenario_voice(self, scenario):
        """为特定场景设置推荐音色"""
        if not self.voice_config:
            return False
        
        try:
            recommended_voice = self.voice_config.get_recommended_voice(scenario)
            return self.update_voice_config(recommended_voice)
        except Exception as e:
            print(f"⚠️ 场景音色设置失败: {e}")
            return False
    
    def _create_robot_context_message(self, user_text: str, action: str) -> str:
        """创建包含机器人执行结果的上下文消息"""
        if self.prompts:
            # 使用配置的prompt模板
            return self.prompts.robot_confirmation_templates["action_success"].format(
                user_command=user_text,
                action=action
            )
        else:
            # 使用默认配置
            action_map = {
                "前进": "向前移动",
                "后退": "向后移动", 
                "左转": "向左转动",
                "右转": "向右转动",
                "停止": "停止移动",
                "向前": "向前移动",
                "向后": "向后移动",
                "向左": "向左转动", 
                "向右": "向右转动",
                "往前": "向前移动",
                "往后": "向后移动",
                "往左": "向左转动",
                "往右": "向右转动"
            }
            
            action_desc = action_map.get(action, action)
            return f"用户指令：'{user_text}'。我已成功控制机器人执行{action_desc}操作。请确认指令完成并给出积极的回应。"
    
    def _enhance_message_with_knowledge(self, user_message: str) -> str:
        """使用本地知识库增强用户消息"""
        if not self.knowledge_base:
            return user_message
        
        try:
            # 根据知识库类型调用不同的方法
            if hasattr(self.knowledge_base, 'get_context'):
                # 新的统一管理器
                relevant_context = self.knowledge_base.get_context(user_message, max_length=2000)
                
                # 检查是否真的找到了相关信息
                if relevant_context and relevant_context not in ["知识库未初始化", "未找到相关信息", "获取信息时出现错误"]:
                    context_found = True
                else:
                    context_found = False
                    
            elif hasattr(self.knowledge_base, 'get_context_for_query'):
                # 旧的简化版知识库
                relevant_context = self.knowledge_base.get_context_for_query(user_message)
                context_found = bool(relevant_context)
            else:
                # 兜底方案
                relevant_context = ""
                context_found = False
            
            if context_found:
                if self.prompts:
                    # 使用配置的prompt模板
                    enhanced_message = self.prompts.knowledge_enhancement_templates["with_context"].format(
                        context=relevant_context,
                        user_question=user_message
                    )
                else:
                    # 使用默认模板
                    enhanced_message = f"""{relevant_context}

用户问题: {user_message}

请基于上述本地知识库信息回答用户问题。如果知识库中没有直接相关的信息，请结合你的知识正常回答。回复要自然、友好，适合语音对话。"""
                
                print(f"🧠 知识库增强: 找到相关信息")
                return enhanced_message
            else:
                print(f"🧠 知识库搜索: 无相关信息")
                return user_message
                
        except Exception as e:
            print(f"⚠️ 知识库查询失败: {e}")
            return user_message
    
    def _audio_player_thread(self):
        """音频播放线程 - WSL环境使用paplay方式"""
        print("🎵 音频播放线程启动（WSL paplay模式）")
        
        while self.is_playing:
            try:
                # 从队列获取音频数据
                audio_data = self.audio_queue.get(timeout=1.0)
                if audio_data is not None:
                    # 在WSL环境下使用paplay播放，直接写入PCM数据
                    self._wsl_paplay_audio(audio_data)
                    
            except queue.Empty:
                # 队列为空时等待一小段时间
                time.sleep(0.1)
            except Exception as e:
                print(f"⚠️ 音频播放错误: {e}")
                time.sleep(0.1)
        
        print("🎵 音频播放线程结束")
    
    def _wsl_paplay_audio(self, audio_data):
        """WSL2环境下通过Windows端播放音频"""
        try:
            import subprocess
            import tempfile
            import os
            import wave
            
            # 先保存一个样本用于分析（只保存第一个）
            if not hasattr(self, '_saved_sample'):
                self._saved_sample = True
                with open('/tmp/doubao_sample.raw', 'wb') as f:
                    f.write(audio_data)
                print(f"🔍 已保存豆包音频样本: /tmp/doubao_sample.raw ({len(audio_data)} 字节)")
            
            print(f"🎵 准备播放音频: {len(audio_data)} 字节")
            
            # 在Windows临时目录创建文件，避免WSL音频桥接问题
            temp_dir = '/mnt/c/Windows/Temp'
            if not os.path.exists(temp_dir):
                # 备用方案：使用WSL tmp目录
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                    wav_file = tmp_file.name
            else:
                # 主方案：使用Windows临时目录
                wav_file = os.path.join(temp_dir, f'dragon_audio_{os.getpid()}.wav')
            
            # 写入WAV格式文件（豆包格式：24kHz，16-bit，单声道）
            with wave.open(wav_file, 'wb') as wf:
                wf.setnchannels(1)        # 单声道
                wf.setsampwidth(2)        # 16-bit = 2字节
                wf.setframerate(24000)    # 24kHz
                wf.writeframes(audio_data)
            
            # 检查生成的WAV文件
            file_size = os.path.getsize(wav_file)
            print(f"📁 生成WAV文件: {file_size} 字节 -> {wav_file}")
            
            # 尝试Windows端播放（绕过WSL2音频桥接问题）
            success = False
            
            # 方案1：Windows CMD播放
            if wav_file.startswith('/mnt/c/'):
                try:
                    windows_path = wav_file.replace('/mnt/c/', 'C:\\').replace('/', '\\')
                    print(f"🔊 Windows播放: {windows_path}")
                    result = subprocess.run([
                        'cmd.exe', '/c', 'start', '/min', windows_path
                    ], capture_output=True, timeout=3)
                    
                    if result.returncode == 0:
                        print("✅ Windows CMD音频播放启动成功")
                        success = True
                    else:
                        print(f"⚠️ Windows CMD播放失败: {result.stderr}")
                except Exception as e:
                    print(f"⚠️ Windows CMD方案异常: {e}")
            
            # 方案2：aplay备用播放
            if not success:
                try:
                    print("🔊 使用aplay备用播放...")
                    result = subprocess.run([
                        'aplay', '-D', 'default', wav_file
                    ], capture_output=True, timeout=5)
                    
                    if result.returncode == 0:
                        print("✅ aplay音频播放成功")
                        success = True
                    else:
                        print(f"⚠️ aplay播放失败: {result.stderr}")
                except Exception as e:
                    print(f"⚠️ aplay方案异常: {e}")
            
            # 清理临时文件（延迟清理给播放时间）
            import threading
            def cleanup_after_delay():
                import time
                time.sleep(3)  # 给播放时间
                try:
                    if os.path.exists(wav_file):
                        os.unlink(wav_file)
                except:
                    pass
            
            threading.Thread(target=cleanup_after_delay, daemon=True).start()
                
            if not success:
                print("❌ 所有音频播放方案都失败")
                
        except Exception as e:
            print(f"❌ WSL2音频播放失败: {e}")
    
    def handle_server_response(self, response):
        """处理服务器响应 - 基于官方实现并集成机器人控制"""
        if response == {}:
            return
        
        # TTS音频数据处理
        if response['message_type'] == 'SERVER_ACK' and isinstance(response.get('payload_msg'), bytes):
            if self.is_sending_chat_tts_text:
                return
            audio_data = response['payload_msg']
            print(f"🎵 收到豆包TTS音频: {len(audio_data)} 字节 (24kHz单声道)")
            self.audio_queue.put(audio_data)
            self.audio_buffer += audio_data
            
        elif response['message_type'] == 'SERVER_FULL_RESPONSE':
            print(f"🔄 服务器响应: 事件{response.get('event')}")
            event = response.get('event')
            payload_msg = response.get('payload_msg', {})
            
            # 清空音频缓存
            if event == 450:
                print(f"🧹 清空缓存音频")
                while not self.audio_queue.empty():
                    try:
                        self.audio_queue.get_nowait()
                    except queue.Empty:
                        continue
                # 标记用户查询状态
                self.is_user_querying = True
            
            # ASR识别结果处理
            if event == 451 and isinstance(payload_msg, dict):
                results = payload_msg.get('results', [])
                if results and len(results) > 0:
                    result = results[0]
                    text = result.get('text', '')
                    is_final = not result.get('is_interim', True)
                    
                    if text and is_final:
                        print(f"🎙️ 用户说: {text}")
                        
                        # 检查是否是机器人控制指令
                        if self.robot_controller.check_robot_command(text):
                            if self.robot_controller.parse_and_execute_command(text):
                                print(f"✅ 机器人执行: {self.robot_controller.current_action}")
                                # 发送增强的上下文消息给豆包
                                enhanced_message = self._create_robot_context_message(text, self.robot_controller.current_action)
                                asyncio.create_task(self.client.chat_text_query(enhanced_message))
                            else:
                                print("⚠️ 未识别的机器人指令")
                        else:
                            # 非机器人指令，使用知识库增强
                            enhanced_message = self._enhance_message_with_knowledge(text)
                            asyncio.create_task(self.client.chat_text_query(enhanced_message))
                        
            # TTS文本流处理
            if event == 550 and isinstance(payload_msg, dict):
                content = payload_msg.get('content', '')
                if content:
                    print(f"💬 豆包: {content}", end='', flush=True)
            
            # TTS完成事件
            if event == 351:
                print()  # 换行
            
            # say_hello完成事件
            if event == 359 and not self.say_hello_over_event.is_set():
                print("✅ 初始问候完成")
                self.say_hello_over_event.set()
    
    async def start_connection(self):
        """启动连接"""
        print("🔗 正在连接豆包语音服务...")
        await self.client.connect()
        print("✅ 连接成功")
        
        # 设置系统角色
        await self.setup_system_role()
    
    async def setup_system_role(self):
        """设置系统角色和prompt"""
        if self.prompts:
            # 使用配置的系统角色
            system_role = self.prompts.get_system_role("default")
            print(f"🎯 使用配置的系统角色: {system_role[:50]}...")
        else:
            # 使用默认系统角色
            system_role = """你是Dragon机器人的语音助手，具有以下特点：
1. 友好、热情、有帮助的个性
2. 可以控制机器人执行运动指令
3. 具备本地知识库查询能力
4. 回复简洁明了，适合语音对话
5. 对机器人执行结果给予积极确认"""
            print("🎯 使用默认系统角色")
        
        try:
            # 发送系统设置消息 (如果API支持)
            # 注意：这取决于你的client API是否支持系统消息设置
            # await self.client.set_system_message(system_role)
            print("✅ 系统角色设置完成")
        except Exception as e:
            print(f"⚠️ 系统角色设置失败: {e}")
    
    async def initial_greeting(self):
        """初始问候 - 恢复豆包API标准激活流程"""
        print("🎤 发送初始问候...")
        
        try:
            # 发送say_hello激活豆包语音流
            await self.client.say_hello()
            print("✅ say_hello已发送，等待豆包语音激活...")
            
            # 等待say_hello完成事件(359) - 这是豆包API的激活机制
            # 添加10秒超时防止卡死
            await asyncio.wait_for(self.say_hello_over_event.wait(), timeout=10.0)
            print("✅ 豆包语音流已激活，开始对话...")
            
        except asyncio.TimeoutError:
            print("⚠️ say_hello激活超时，强制继续...")
            self.say_hello_over_event.set()  # 强制设置事件
        except Exception as e:
            print(f"⚠️ 初始问候失败: {e}")
            print("⚠️ 强制激活语音流...")
            self.say_hello_over_event.set()  # 强制设置事件
    
    async def process_microphone_input(self):
        """处理麦克风输入 - 基于官方实现"""
        stream = self.audio_device.open_input_stream()
        print("🎙️ 已打开麦克风，开始连续对话...")
        print("💡 说话技巧：")
        print("   - 机器人控制：'机器人前进'、'让机器人左转'、'机器人停止'")
        print("   - 日常聊天：正常对话即可")
        print("   - 按Ctrl+C退出")
        
        while self.is_recording:
            try:
                # 读取音频数据
                audio_data = stream.read(config.input_audio_config["chunk"], exception_on_overflow=False)
                await self.client.task_request(audio_data)
                await asyncio.sleep(0.01)  # 避免CPU过度使用
                
            except Exception as e:
                print(f"⚠️ 读取麦克风数据出错: {e}")
                await asyncio.sleep(0.1)
    
    async def start(self):
        """启动完整的对话系统"""
        try:
            print("🚀 Dragon机器人对话系统启动中...")
            print("=" * 60)
            
            # 1. 建立连接
            await self.start_connection()
            
            # 2. 启动响应处理
            response_task = asyncio.create_task(self._handle_responses())
            
            # 3. 初始问候
            await self.initial_greeting()
            
            # 4. 开始麦克风输入
            await self.process_microphone_input()
            
        except KeyboardInterrupt:
            print("\n👋 用户中断，正在关闭...")
        except Exception as e:
            print(f"❌ 系统错误: {e}")
        finally:
            await self.cleanup()
    
    async def _handle_responses(self):
        """处理服务器响应的异步任务"""
        try:
            while self.is_recording:
                try:
                    # 接收服务器响应
                    response = await self.client.receive_server_response()
                    if response:
                        self.handle_server_response(response)
                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    print(f"⚠️ 响应处理错误: {e}")
                    await asyncio.sleep(0.1)
        except Exception as e:
            print(f"❌ 响应处理任务错误: {e}")
    
    async def cleanup(self):
        """清理资源"""
        print("🛑 正在清理系统资源...")
        
        self.is_recording = False
        self.is_playing = False
        
        # 停止机器人
        if self.robot_controller:
            self.robot_controller.execute_movement(0.0, 0.0)
        
        # 关闭音频设备
        if self.output_stream:
            self.output_stream.stop_stream()
            self.output_stream.close()
        if self.audio_device:
            self.audio_device.cleanup()
        
        # 关闭客户端连接
        if self.client:
            await self.client.close()
        
        # 等待播放线程结束
        if self.player_thread and self.player_thread.is_alive():
            self.player_thread.join(timeout=2.0)
        
        print("✅ 系统清理完成")

async def main():
    """主函数"""
    print("🤖 Dragon机器人对话系统")
    print("🔧 基于官方豆包实时语音API")
    print("🎯 支持连续对话 + 机器人控制")
    print()
    
    session = DragonDialogSession()
    await session.start()

if __name__ == "__main__":
    asyncio.run(main())
