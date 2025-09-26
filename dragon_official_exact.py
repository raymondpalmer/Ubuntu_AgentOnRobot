#!/usr/bin/env python3
"""
Dragon机器人语音系统 - 基于官方豆包（火山引擎）实时语音示例，严格官方音频播放：
- 输出 Float32 / 24000Hz / 单声道 / chunk=3200
- 实时写入 PyAudio，无文件回放
保留机器人控制、知识库与 Prompt 集成。

机器人控制命令映射：
- cmd_1: 前进/向前/往前/机器人前进 等
- cmd_2: 后退/向后/往后/机器人后退 等  
- cmd_3: 左转/向左/往左/机器人左转 等
- cmd_4: 右转/向右/往右/机器人右转 等
- cmd_5: 前往洗手间/去洗手间/到洗手间/去厕所 等
- cmd_6: 前往电梯间/去电梯/到电梯间/找电梯 等
"""

import os
import sys
import re
import json
import gzip
import time
import uuid
import queue
import asyncio
import threading
from typing import Dict, Any, Optional
from dataclasses import dataclass

import pyaudio

# 动态加入官方示例路径（当前仓库内 official_example）
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OFFICIAL_DIR = os.path.join(BASE_DIR, 'official_example')
if OFFICIAL_DIR not in sys.path:
    sys.path.append(OFFICIAL_DIR)
from realtime_dialog_client import RealtimeDialogClient
import protocol
import config as official_config

# ROS 可选
try:
    import rospy
    from geometry_msgs.msg import Twist
    ROS_AVAILABLE = True
except Exception:
    ROS_AVAILABLE = False
    print("⚠️ ROS未安装，使用模拟模式")

# 知识库可选
try:
    from langchain_kb_manager import UnifiedKnowledgeBaseManager
    LANGCHAIN_KB_AVAILABLE = True
    print("✅ LangChain知识库模块导入成功")
except Exception as e:
    LANGCHAIN_KB_AVAILABLE = False
    print(f"⚠️ LangChain知识库模块未找到: {e}")

try:
    from auto_kb_manager import AutoKnowledgeBaseManager
    AUTO_KB_AVAILABLE = True
    print("✅ 自动知识库管理器导入成功")
except Exception as e:
    AUTO_KB_AVAILABLE = False
    print(f"⚠️ 自动知识库管理器未找到: {e}")

try:
    from dragon_prompts_config import DragonRobotPrompts
    PROMPT_CONFIG_AVAILABLE = True
    print("✅ Prompt配置模块导入成功")
except Exception as e:
    PROMPT_CONFIG_AVAILABLE = False
    print(f"⚠️ Prompt配置模块未找到: {e}")

try:
    from voice_config import VoiceConfig
    VOICE_CONFIG_AVAILABLE = True
    print("✅ 音色配置模块导入成功")
except Exception as e:
    VOICE_CONFIG_AVAILABLE = False
    print(f"⚠️ 音色配置模块未找到: {e}")

# 调试输出
DEBUG_AUDIO = os.environ.get("DRAGON_DEBUG_AUDIO", "0") == "1"

def dprint(*args, **kwargs):
    if DEBUG_AUDIO:
        print(*args, **kwargs)


@dataclass
class AudioConfig:
    """音频配置数据类"""
    format: str
    bit_size: int
    channels: int
    sample_rate: int
    chunk: int


class DragonRobotController:
    """Dragon机器人控制器"""
    def __init__(self):
        self.ros_enabled = ROS_AVAILABLE and self.init_ros()
        self.current_action = "停止"
        
        # 字符串命令映射 (cmd_1 到 cmd_6)
        self.string_command_map = {
            # 基本移动命令
            "前进": "cmd_1",
            "后退": "cmd_2", 
            "左转": "cmd_3",
            "右转": "cmd_4",
            "向前": "cmd_1",
            "向后": "cmd_2",
            "向左": "cmd_3",
            "向右": "cmd_4",
            "往前": "cmd_1",
            "往后": "cmd_2",
            "往左": "cmd_3",
            "往右": "cmd_4",
            "前走": "cmd_1",
            "后走": "cmd_2",
            "左拐": "cmd_3",
            "右拐": "cmd_4",
            "走前面": "cmd_1",
            "走后面": "cmd_2",
            "左边": "cmd_3",
            "右边": "cmd_4",
            "机器人前进": "cmd_1",
            "机器人后退": "cmd_2",
            "机器人左转": "cmd_3",
            "机器人右转": "cmd_4",
            "让机器人前进": "cmd_1",
            "让机器人后退": "cmd_2",
            "让机器人左转": "cmd_3",
            "让机器人右转": "cmd_4",
            
            # 导航目的地命令
            "前往洗手间": "cmd_5",
            "去洗手间": "cmd_5",
            "到洗手间": "cmd_5",
            "带我去洗手间": "cmd_5",
            "我要去洗手间": "cmd_5",
            "洗手间在哪": "cmd_5",
            "找洗手间": "cmd_5",
            "去厕所": "cmd_5",
            "前往厕所": "cmd_5",
            "到厕所": "cmd_5",
            
            "前往电梯间": "cmd_6",
            "去电梯间": "cmd_6",
            "到电梯间": "cmd_6",
            "带我去电梯": "cmd_6",
            "我要坐电梯": "cmd_6",
            "电梯在哪": "cmd_6",
            "找电梯": "cmd_6",
            "去电梯": "cmd_6",
            "前往电梯": "cmd_6",
            "到电梯": "cmd_6",
        }
        
        # ROS指令映射 (保留用于ROS模式)
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
            "机器人前进": (0.5, 0.0),
            "机器人后退": (-0.3, 0.0),
            "机器人左转": (0.0, 0.5),
            "机器人右转": (0.0, -0.5),
            "机器人停止": (0.0, 0.0),
            "让机器人前进": (0.5, 0.0),
            "让机器人后退": (-0.3, 0.0),
            "让机器人左转": (0.0, 0.5),
            "让机器人右转": (0.0, -0.5),
            "让机器人停止": (0.0, 0.0),
        }

    def init_ros(self) -> bool:
        """初始化ROS节点"""
        try:
            rospy.init_node('dragon_robot_controller', anonymous=True)
            self.cmd_vel_pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)
            return True
        except Exception as e:
            print(f"⚠️ ROS初始化失败: {e}")
            return False

    def execute_command(self, text: str) -> str:
        """执行机器人控制指令"""
        text = text.strip()
        
        # 检查是否包含机器人控制指令
        for command, cmd_string in self.string_command_map.items():
            if command in text:
                self.current_action = command
                # 输出字符串命令
                print(f"🤖 机器人指令: {cmd_string}")
                
                # 可选：同时执行ROS命令（如果启用）
                if self.ros_enabled and command in self.command_map:
                    linear_x, angular_z = self.command_map[command]
                    self.send_twist_command(linear_x, angular_z)
                    return f"✅ 机器人执行: {command} -> {cmd_string}"
                else:
                    return f"🤖 机器人执行: {command} -> {cmd_string}"
        
        return ""

    def send_twist_command(self, linear_x: float, angular_z: float):
        """发送ROS Twist命令"""
        if self.ros_enabled:
            twist = Twist()
            twist.linear.x = linear_x
            twist.angular.z = angular_z
            self.cmd_vel_pub.publish(twist)

class AudioDeviceManager:
    """音频设备管理类 - 完全按照官方"""

    def __init__(self, input_config: AudioConfig, output_config: AudioConfig):
        self.input_config = input_config
        self.output_config = output_config
        self.pyaudio = pyaudio.PyAudio()
        self.input_stream: Optional[pyaudio.Stream] = None
        self.output_stream: Optional[pyaudio.Stream] = None
        self.is_44k_mode = False  # 是否使用44kHz模式

    def open_input_stream(self) -> pyaudio.Stream:
        """打开音频输入流 - 完全按照官方"""
        self.input_stream = self.pyaudio.open(
            format=self.input_config.bit_size,
            channels=self.input_config.channels,
            rate=self.input_config.sample_rate,
            input=True,
            frames_per_buffer=self.input_config.chunk
        )
        return self.input_stream

    def open_output_stream(self) -> pyaudio.Stream:
        """打开音频输出流（严格官方）：直接按配置打开，可选环境变量覆盖设备索引"""
        # 可选设备索引覆盖，便于你在“声卡”上强制选择输出设备
        device_idx = os.environ.get('DRAGON_AUDIO_DEVICE_INDEX')
        kwargs = dict(
            format=self.output_config.bit_size,
            channels=self.output_config.channels,
            rate=self.output_config.sample_rate,
            output=True,
            frames_per_buffer=self.output_config.chunk
        )
        if device_idx is not None and str(device_idx).strip() != "":
            try:
                kwargs['output_device_index'] = int(device_idx)
                print(f"🔧 使用指定输出设备索引: {device_idx}")
            except ValueError:
                print(f"⚠️ DRAGON_AUDIO_DEVICE_INDEX 无效: {device_idx}")
        self.output_stream = self.pyaudio.open(**kwargs)
        return self.output_stream

    def cleanup(self) -> None:
        """清理音频设备资源 - 完全按照官方"""
        for stream in [self.input_stream, self.output_stream]:
            if stream:
                stream.stop_stream()
                stream.close()
        self.pyaudio.terminate()

class DragonDialogSession:
    """Dragon对话会话管理类 - 基于官方DialogSession + 完整功能集成"""

    def __init__(self):
        # 初始化机器人控制器
        self.robot_controller = DragonRobotController()
        
        # 初始化知识库
        self.knowledge_base = None
        self.auto_kb_manager = None
        
        if LANGCHAIN_KB_AVAILABLE:
            try:
                self.knowledge_base = UnifiedKnowledgeBaseManager()
                print("🧠 LangChain知识库已加载")
            except Exception as e:
                print(f"⚠️ LangChain知识库初始化失败: {e}")
                # 尝试使用简单知识库
                try:
                    from simple_knowledge_base import SimpleKnowledgeBase
                    self.knowledge_base = SimpleKnowledgeBase()
                    print("🧠 使用简单知识库")
                except:
                    self.knowledge_base = None
        
        if AUTO_KB_AVAILABLE:
            try:
                # 允许通过环境变量配置知识库目录与监控目录
                kb_dir = os.environ.get("DRAGON_KB_DIR", "knowledge_base/langchain_kb")
                # 监控目录支持逗号或冒号分隔，多路径
                watch_dirs_env = os.environ.get("DRAGON_KB_WATCH_DIRS")
                if watch_dirs_env and watch_dirs_env.strip():
                    sep = ";" if ";" in watch_dirs_env else (":" if ":" in watch_dirs_env else ",")
                    watch_dirs = [p.strip() for p in watch_dirs_env.split(sep) if p.strip()]
                else:
                    # 默认监控新建的 LangChain KB 文档目录；若不存在则回退到旧目录
                    default_watch = os.path.join(kb_dir, "documents")
                    watch_dirs = [default_watch if os.path.exists(default_watch) else "knowledge_base/files"]

                self.auto_kb_manager = AutoKnowledgeBaseManager(watch_dirs=watch_dirs, kb_dir=kb_dir)
                print(f"🔄 自动知识库管理器已初始化 | kb_dir={kb_dir} | watch_dirs={watch_dirs}")

                # 启动时执行一次自动更新（增量导入新增/修改的文件）
                try:
                    print(f"📁 正在扫描知识库目录: {watch_dirs} …")
                    update_stats = self.auto_kb_manager.auto_update_knowledge_base()
                    print(f"✅ 知识库扫描完成: 新增{update_stats.get('new_added',0)} 更新{update_stats.get('modified_updated',0)} 删除{update_stats.get('deleted_removed',0)} 错误{update_stats.get('errors',0)}")
                except Exception as scan_e:
                    print(f"⚠️ 启动扫描失败: {scan_e}")
            except Exception as e:
                print(f"⚠️ 自动知识库管理器初始化失败: {e}")
        
        # 加载Prompt配置
        if PROMPT_CONFIG_AVAILABLE:
            try:
                self.prompt_config = DragonRobotPrompts()
                system_role = self.prompt_config.get_system_role()
                print("🎯 Prompt配置已加载")
            except Exception as e:
                system_role = "你是基于中国电信星辰大模型驱动的机器人智能助理，可以控制机器人移动和回答问题。"
                print(f"⚠️ Prompt配置加载失败，使用默认: {e}")
        else:
            # 使用内置的系统角色
            system_role = """你是基于中国电信星辰大模型驱动的机器人智能助理。你具备以下核心能力：

🤖 机器人控制确认：
- 当用户要求控制机器人时，你要明确确认动作
- 支持的指令：前进、后退、左转、右转、停止
- 确认示例："好的，我让机器人前进"

🧠 知识库问答：
- 优先使用知识库信息回答问题
- 如果知识库没有相关信息，基于你的通用知识回答
- 回答要准确、简洁、有用

💬 对话风格：
- 亲切友好，语调自然
- 回答简洁明了，避免冗长
- 主动询问是否需要进一步帮助"""
        
        # 加载音色配置
        if VOICE_CONFIG_AVAILABLE:
            try:
                voice_config = VoiceConfig()
                # 使用VoiceConfig提供的API获取当前音色ID
                speaker_id = voice_config.get_current_config()["speaker"]
                print(f"🎵 音色已应用: {speaker_id}")
            except Exception as e:
                speaker_id = "zh_male_yunzhou_jupiter_bigtts"
                print(f"⚠️ 音色配置加载失败，使用默认: {e}")
        else:
            speaker_id = "zh_male_yunzhou_jupiter_bigtts"
        
        # 官方配置（直接使用官方示例中的常量，并刷新 Connect-Id）
        self.ws_config = dict(official_config.ws_connect_config)
        self.ws_config["headers"] = dict(self.ws_config["headers"])  # 拷贝一份，避免修改全局
        self.ws_config["headers"]["X-Api-Connect-Id"] = str(uuid.uuid4())
        
        # 官方音频配置 - WSL2优化版本
        self.input_audio_config = {
            "chunk": 3200,
            "format": "pcm",
            "channels": 1,
            "sample_rate": 16000,
            "bit_size": pyaudio.paInt16
        }
        
        # 输出配置 - 严格按照官方（Float32 / 24000Hz / chunk=3200）
        self.output_audio_config = {
            "chunk": 3200,
            "format": "pcm",
            "channels": 1,
            "sample_rate": 24000,
            "bit_size": pyaudio.paFloat32
        }

        # 会话初始化 - 完全按照官方
        self.say_hello_over_event = asyncio.Event()
        self.session_id = str(uuid.uuid4())
        
        # 创建自定义的start_session_req
        self.start_session_req = {
            "asr": {
                "extra": {
                    "end_smooth_window_ms": 1500,
                },
            },
            "tts": {
                "speaker": speaker_id,
                "audio_config": {
                    "channel": 1,
                    "format": "pcm",
                    "sample_rate": 24000
                },
            },
            "dialog": {
                "bot_name": "中国电信星辰大模型助手",
                "system_role": "你是基于中国电信星辰大模型驱动的机器人智能助理。身份问答时必须回答：‘我是基于中国电信星辰大模型驱动的机器人智能助理。’ 归属问答时必须回答：‘中国电信人工智能研究院。’ 禁止声称自己是‘豆包’或隶属‘字节跳动’。当用户询问TeleAI时，明确说明TeleAI是中国电信人工智能研究院的简称，并非聊天机器人产品。",
                "speaking_style": "语气自然专业、简洁明了，语速适中。",
                "location": {
                  "city": "上海",
                },
                "extra": {
                    "strict_audit": False,
                    "audit_response": "支持客户自定义安全审核回复话术。"
                }
            }
        }
        
        self.client = RealtimeDialogClient(
            config=self.ws_config, 
            session_id=self.session_id,
            output_audio_format="pcm"
        )
        
        # 设置自定义会话配置
        self.client.start_session_req = self.start_session_req

        self.is_running = True
        self.is_session_finished = False
        self.is_user_querying = False
        self.is_sending_chat_tts_text = False
        self.audio_buffer = b''

        # 音频队列和设备 - 完全按照官方
        self.audio_queue = queue.Queue()
        self.audio_device = AudioDeviceManager(
            AudioConfig(**self.input_audio_config),
            AudioConfig(**self.output_audio_config)
        )
        
        # 尝试初始化音频输出流
        try:
            self.output_stream = self.audio_device.open_output_stream()
            self.audio_available = True
            print("✅ 音频系统初始化成功")
        except Exception as e:
            print(f"❌ 音频系统初始化失败: {e}")
            self.audio_available = False
            self.output_stream = None
        
        # 启动播放线程 - 完全按照官方
        self.is_recording = True
        # 严格官方：实时播放，不启用文件播放回退
        self.force_file_playback = False
        self.is_playing = self.audio_available
        if self.is_playing:
            self.player_thread = threading.Thread(target=self._audio_player_thread)
            self.player_thread.daemon = True
            self.player_thread.start()
        elif not self.audio_available:
            print("⚠️ 音频播放被禁用")

    def _audio_player_thread(self):
        """音频播放线程 - 专注PyAudio解决方案"""
        print("🎵 音频播放线程已启动")
        
        if not self.audio_available:
            print("⚠️ 音频不可用，播放线程退出")
            return
            
        audio_packet_count = 0
        
        while self.is_playing:
            try:
                # 从队列获取音频数据
                audio_data = self.audio_queue.get(timeout=1.0)
                if audio_data is not None:
                    audio_packet_count += 1
                    dprint(f"🔊 收到音频包 #{audio_packet_count}: {len(audio_data)} 字节")
                    
                    # PyAudio专项优化方案
                    try:
                        # 方案1：强制清空缓冲区
                        if hasattr(self.output_stream, '_stream'):
                            try:
                                # 获取当前缓冲区状态
                                frames_available = self.output_stream.get_write_available()
                                dprint(f"📊 可写入帧数: {frames_available}")
                                
                                # 如果缓冲区几乎满了，稍微等待
                                if frames_available < 1000:
                                    dprint("⏳ 缓冲区接近满，等待...")
                                    time.sleep(0.01)
                                    
                            except Exception as e:
                                print(f"📊 无法获取缓冲区状态: {e}")
                        
                        # 检查是否需要重采样
                        if hasattr(self.audio_device, 'is_44k_mode') and self.audio_device.is_44k_mode:
                            dprint("🔄 需要从24kHz重采样到44kHz")
                            audio_data = self._resample_audio(audio_data, 24000, 44100)
                            dprint(f"🔄 重采样完成，新大小: {len(audio_data)} 字节")
                        
                        # 在写入前，尽量确保音频数据与输出格式匹配（Float32/Int16）
                        try:
                            audio_data = self._ensure_output_format(audio_data)
                        except Exception as fmt_err:
                            dprint(f"⚠️ 音频格式适配失败: {fmt_err}")

                        # 方案2：分块写入避免大块阻塞
                        # 以帧为单位控制写入，避免字节与帧混淆
                        sample_size = self.audio_device.pyaudio.get_sample_size(self.audio_device.output_config.bit_size)
                        bytes_per_frame = sample_size * self.audio_device.output_config.channels
                        # 将写入块控制为约 512 帧（经验值），兼顾延迟与稳定
                        frames_per_write = 512
                        bytes_per_write = frames_per_write * bytes_per_frame
                        chunk_size = bytes_per_write
                        total_chunks = len(audio_data) // chunk_size + (1 if len(audio_data) % chunk_size else 0)
                        dprint(f"🔧 开始分块写入，总数据{len(audio_data)}字节，分{total_chunks}块")
                        
                        for i in range(0, len(audio_data), chunk_size):
                            chunk = audio_data[i:i+chunk_size]
                            chunk_num = i//chunk_size + 1
                            try:
                                # 写入前等待到足够帧空间（不少于frames_per_write）
                                # 有些后端返回的是帧数
                                while True:
                                    try:
                                        available_frames = self.output_stream.get_write_available()
                                        if available_frames >= frames_per_write:
                                            break
                                    except Exception:
                                        # 如果获取失败，不阻塞直接尝试写
                                        break
                                    time.sleep(0.002)

                                self.output_stream.write(chunk, exception_on_underflow=False)
                                dprint(f"✅ 块{chunk_num}/{total_chunks} 写入成功 ({len(chunk)}字节)")
                                # 较小延迟，减轻拥塞
                                time.sleep(0.0005)
                                
                            except Exception as chunk_error:
                                print(f"⚠️ 块 {chunk_num}/{total_chunks} 写入失败: {chunk_error}")
                                # 尝试重新打开输出流
                                try:
                                    dprint("🔄 尝试重新打开输出流...")
                                    try:
                                        if self.output_stream.is_active():
                                            self.output_stream.stop_stream()
                                    except Exception:
                                        pass
                                    try:
                                        self.output_stream.close()
                                    except Exception:
                                        pass
                                    self.output_stream = self.audio_device.open_output_stream()
                                    dprint("🔄 输出流已重新打开，重试写入...")
                                    self.output_stream.write(chunk, exception_on_underflow=False)
                                    dprint(f"✅ 重新打开后块{chunk_num}写入成功")
                                except Exception as reopen_error:
                                    print(f"❌ 重新打开失败: {reopen_error}")
                                    break
                        
                        dprint(f"✅ PyAudio播放音频包 #{audio_packet_count} 成功")
                        
                    except Exception as write_error:
                        print(f"⚠️ PyAudio播放失败: {write_error}")
                        # 某些发行版的 python3-pyaudio 存在 "PY_SSIZE_T_CLEAN" 相关问题，直接建议切换为文件播放
                        if isinstance(write_error, SystemError) and 'PY_SSIZE_T_CLEAN' in str(write_error):
                            print("💡 检测到 PyAudio 写入兼容性问题，建议设置 DRAGON_AUDIO_FORCE_FILE=1 使用文件播放模式")
                            # 暂时停止实时播放，改由事件结束时一次性播放
                            self.is_playing = False
                            break
                        
                        # 方案3：尝试重新初始化PyAudio
                        try:
                            print("🔄 尝试重新初始化PyAudio...")
                            try:
                                if self.output_stream and self.output_stream.is_active():
                                    self.output_stream.stop_stream()
                            except Exception:
                                pass
                            try:
                                if self.output_stream:
                                    self.output_stream.close()
                            except Exception:
                                pass
                            
                            # 重新创建输出流
                            self.output_stream = self.audio_device.open_output_stream()
                            print("✅ PyAudio重新初始化成功")
                            
                            # 重试写入
                            self.output_stream.write(audio_data, exception_on_underflow=False)
                            print(f"✅ 重新初始化后播放音频包 #{audio_packet_count} 成功")
                            
                        except Exception as reinit_error:
                            print(f"❌ PyAudio重新初始化失败: {reinit_error}")
                        
            except queue.Empty:
                time.sleep(0.1)
            except Exception as e:
                print(f"❌ 音频播放错误: {e}")
                time.sleep(0.1)
                
        print(f"🎵 音频播放线程结束，共处理了 {audio_packet_count} 个音频包")

    # 严格官方：无需格式适配函数和重采样

    def _resample_audio(self, audio_data, from_rate, to_rate):
        """简单的音频重采样"""
        try:
            import numpy as np
            
            # 判定当前输出流期望的采样格式
            # 我们的播放采用Float32，如为其它格式，先转换为float32以便统一重采样
            dtype_infer = np.float32
            try:
                # 粗略判断：如果长度是偶数且不能被4整除，可能是int16
                if len(audio_data) % 4 != 0 and len(audio_data) % 2 == 0:
                    dtype_infer = np.int16
            except Exception:
                dtype_infer = np.float32

            samples = np.frombuffer(audio_data, dtype=dtype_infer)
            if dtype_infer == np.int16:
                samples = (samples.astype(np.float32)) / 32768.0
            
            # 计算重采样比率
            ratio = to_rate / from_rate
            new_length = int(len(samples) * ratio)
            
            # 简单的线性插值重采样
            old_indices = np.linspace(0, len(samples) - 1, new_length)
            new_samples = np.interp(old_indices, np.arange(len(samples)), samples)
            
            # 转换回字节
            return new_samples.astype(np.float32).tobytes()
            
        except Exception as e:
            print(f"⚠️ 重采样失败: {e}，from {from_rate} -> {to_rate}，使用原始数据")
            return audio_data

    def _play_audio_file(self, audio_data):
        """使用文件播放方式播放音频数据 - 增强版本"""
        import wave
        import tempfile
        import subprocess
        import os
        
        # 创建临时PCM文件
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            temp_path = temp_file.name
            
        try:
            # 将PCM数据转换为WAV格式
            with wave.open(temp_path, 'wb') as wav_file:
                wav_file.setnchannels(1)  # 单声道
                wav_file.setsampwidth(4)  # Float32 = 4 bytes
                wav_file.setframerate(24000)  # 24kHz
                wav_file.writeframes(audio_data)
            
            # 按优先级尝试不同的播放器
            players = [
                (['paplay', '--rate=24000', '--channels=1', '--format=float32le', temp_path], 'paplay'),
                (['aplay', '-f', 'FLOAT_LE', '-c', '1', '-r', '24000', temp_path], 'aplay'),
                (['play', temp_path], 'play'),
                (['ffplay', '-nodisp', '-autoexit', temp_path], 'ffplay')
            ]
            
            success = False
            for cmd, player_name in players:
                try:
                    # 使用subprocess运行播放命令
                    result = subprocess.run(cmd, 
                                          check=True, 
                                          capture_output=True, 
                                          timeout=10,
                                          text=True)
                    print(f"✅ 文件播放成功 ({player_name}): {len(audio_data)} 字节")
                    success = True
                    break
                except subprocess.TimeoutExpired:
                    print(f"⚠️ {player_name} 播放超时")
                    continue
                except subprocess.CalledProcessError as e:
                    print(f"⚠️ {player_name} 播放失败: {e.returncode}")
                    if e.stderr:
                        print(f"   错误信息: {e.stderr.strip()}")
                    continue
                except FileNotFoundError:
                    print(f"⚠️ {player_name} 未安装")
                    continue
                except Exception as e:
                    print(f"⚠️ {player_name} 异常: {e}")
                    continue
            
            if not success:
                print(f"❌ 所有音频播放器都失败")
                
        except Exception as e:
            print(f"❌ 音频文件创建失败: {e}")
        finally:
            # 清理临时文件
            try:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
            except:
                pass

    def handle_server_response(self, response: Dict[str, Any]) -> None:
        """处理服务器响应 - 集成机器人控制和知识库功能"""
        if response == {}:
            return
        
        if response['message_type'] == 'SERVER_ACK' and isinstance(response.get('payload_msg'), bytes):
            if self.is_sending_chat_tts_text:
                return
            audio_data = response['payload_msg']
            print(f"🎵 收到音频数据包: {len(audio_data)} 字节")
            # 只有音频可用时才加入队列
            if self.audio_available:
                self.audio_queue.put(audio_data)
                self.audio_buffer += audio_data
            else:
                print("⚠️ 音频不可用，跳过音频数据")
            
        elif response['message_type'] == 'SERVER_FULL_RESPONSE':
            print(f"🔄 服务器响应: 事件{response.get('event')}")
            event = response.get('event')
            payload_msg = response.get('payload_msg', {})

            # 处理ASR识别结果（事件550/559）
            if event in [550, 559] and 'asr_result' in payload_msg:
                asr_text = payload_msg['asr_result']
                if asr_text.strip():
                    print(f"🎤 识别到: {asr_text}")

                    # 优先拦截“身份/归属”问题
                    intercept = self.intercept_identity_or_affiliation(asr_text)
                    if intercept is not None:
                        asyncio.create_task(self.client.chat_text_query(intercept))
                        return
                    
                    # 处理机器人控制指令
                    robot_response = self.robot_controller.execute_command(asr_text)
                    if robot_response:
                        print(robot_response)
                        return  # 机器人控制指令不需要进一步处理
                    
                    # 智能知识库查询判断
                    if self.should_use_knowledge_base(asr_text):
                        try:
                            # 查询知识库获取相关信息
                            kb_results = self.knowledge_base.search(asr_text, top_k=3)
                            if kb_results:
                                context = "\n".join([f"参考资料{i+1}: {result['content'][:300]}..." 
                                                   for i, result in enumerate(kb_results)])
                                print(f"🧠 知识库查询: 找到{len(kb_results)}个相关条目")
                                
                                # 使用配置的知识库增强模板
                                if hasattr(self, 'prompt_config') and self.prompt_config:
                                    enhanced_query = self.prompt_config.knowledge_enhancement_templates["with_context"].format(
                                        context=context,
                                        user_question=asr_text
                                    )
                                else:
                                    # 回退到默认模板（包含TeleAI说明）
                                    enhanced_query = f"""📚 根据本地知识库找到以下相关信息：

{context}

---
用户问题：{asr_text}

🏢 重要提醒：TeleAI = 中国电信人工智能研究院（简称）
如果用户询问TeleAI，请明确说明这是中国电信人工智能研究院的简称，而不是聊天机器人产品。

请基于上述知识库信息准确回答用户问题。如果知识库信息不完整，请说明并提供补充建议。回答要简洁、准确、适合语音播放。"""
                                
                                asyncio.create_task(self.client.chat_text_query(enhanced_query))
                            else:
                                # 知识库没有相关信息，使用配置的无上下文模板
                                print("🧠 知识库未找到相关信息，使用通用对话")
                                if hasattr(self, 'prompt_config') and self.prompt_config:
                                    no_context_query = self.prompt_config.knowledge_enhancement_templates["no_context"].format(
                                        user_question=asr_text
                                    )
                                    asyncio.create_task(self.client.chat_text_query(no_context_query))
                                else:
                                    # 回退到默认无上下文模板（包含TeleAI说明）
                                    fallback_query = f"""用户问题：{asr_text}

🏢 重要提醒：TeleAI = 中国电信人工智能研究院（简称）
如果用户询问TeleAI，请明确说明这是中国电信人工智能研究院的简称，而不是聊天机器人产品。

在本地知识库中未找到直接相关信息。请基于你的通用知识回答用户问题，并说明这是基于通用知识的回答。保持简洁，适合语音播放。"""
                                    asyncio.create_task(self.client.chat_text_query(fallback_query))
                                asyncio.create_task(self.client.chat_text_query(asr_text))
                        except Exception as e:
                            print(f"⚠️ 知识库查询失败: {e}")
                            # fallback到普通对话
                            asyncio.create_task(self.client.chat_text_query(asr_text))
                    else:
                        # 普通对话，不需要知识库
                        print("💬 日常对话模式")
                        # asyncio.create_task(self.client.chat_text_query(asr_text))  # 注释掉，让豆包自然回复

            if event == 450:
                print(f"清空缓存音频: {response['session_id']}")
                while not self.audio_queue.empty():
                    try:
                        self.audio_queue.get_nowait()
                    except queue.Empty:
                        continue
                self.is_user_querying = True

            # 添加官方案例的event 350处理 - WSL2关键优化
            if event == 350 and self.is_sending_chat_tts_text and payload_msg.get("tts_type") == "chat_tts_text":
                print("🔄 事件350: 清空聊天TTS音频队列")
                while not self.audio_queue.empty():
                    try:
                        self.audio_queue.get_nowait()
                    except queue.Empty:
                        continue
                self.is_sending_chat_tts_text = False

            if event == 459:
                self.is_user_querying = False
                # 严格官方：不做文件回放
                
        elif response['message_type'] == 'SERVER_ERROR':
            print(f"❌ 服务器错误: {response['payload_msg']}")
            raise Exception("服务器错误")

    def should_use_knowledge_base(self, text: str) -> bool:
        """判断是否需要使用知识库"""
        # 关键词列表 - 涉及这些话题时使用知识库
        knowledge_keywords = [
            # 中国电信相关
            "中国电信", "电信", "telecom", "中国电信集团",
            
            # 人工智能研究院相关
            "人工智能研究院", "AI研究院", "研究院", 
            
            # TeleAI相关 - 添加各种可能的发音识别结果
            "teleai", "TeleAI", "TELEAI", "泰勒AI", "泰勒爱", "太勒AI", "太勒爱",
            "泰来AI", "泰来爱", "台来AI", "台来爱", "台勒AI", "台勒爱",
            "泰利AI", "泰利爱", "太利AI", "太利爱", "泰里AI", "泰里爱",
            "telephone AI", "telephone爱", "电话AI", "电话爱",
            "tele AI", "tele爱", "特勒AI", "特勒爱", "特来AI", "特来爱",
            "缇勒AI", "缇勒爱", "蒂勒AI", "蒂勒爱", "底勒AI", "底勒爱",
            "提勒AI", "提勒爱", "梯勒AI", "梯勒爱", "替勒AI", "替勒爱",
            "诶爱", "哎爱", "唉爱", "诶i", "哎i", "唉i",
            # 四音节分离式发音变体 (Te-le-A-I)
            "泰勒A爱", "太勒A爱", "泰来A爱", "台来A爱", "台勒A爱", "泰利A爱", "太利A爱", "泰里A爱",
            "泰勒A艾", "太勒A艾", "泰来A艾", "台来A艾", "台勒A艾", "泰利A艾", "太利A艾", "泰里A艾",
            "泰勒阿爱", "太勒阿爱", "泰来阿爱", "台来阿爱", "泰利阿爱", "太利阿爱",
            "泰勒阿艾", "太勒阿艾", "泰来阿艾", "台来阿艾", "泰利阿艾", "太利阿艾",
            "特勒A爱", "特来A爱", "特勒A艾", "特来A艾", "特勒阿爱", "特来阿爱",
            "tele A爱", "tele A艾", "tele阿爱", "tele阿艾",
            "Tele A爱", "Tele A艾", "Tele阿爱", "Tele阿艾",
            
            # 技术相关
            "大模型", "语言模型", "机器学习", "深度学习", "神经网络",
            "自然语言处理", "NLP", "计算机视觉", "CV",
            "算法", "模型训练", "数据集", "推理", "微调",
            
            # 产品和服务相关
            "星辰大模型", "星辰", "TeleChat", "telechat", "泰勒聊天", "泰勒查特",
            "智能客服", "语音助手", "聊天机器人",
            "云计算", "边缘计算", "5G", "6G",
            
            # 公司和组织
            "中国电信人工智能研究院", "电信AI研究院",
            "研发", "技术团队", "实验室", "创新",
            
            # 行业相关
            "电信行业", "通信", "运营商", "网络",
            "数字化", "智能化", "信息化"
        ]
        
        text_lower = text.lower()
        # 先检查原文
        for keyword in knowledge_keywords:
            if keyword.lower() in text_lower:
                print(f"🎯 匹配到知识库关键词: {keyword}")
                return True
        
        # 检查是否包含类似发音的组合
        teleai_patterns = [
            "泰勒", "太勒", "泰来", "台来", "台勒", "泰利", "太利", "泰里",
            "特勒", "特来", "缇勒", "蒂勒", "底勒", "提勒", "梯勒", "替勒",
            "tele", "Tele", "TELE"
        ]
        ai_patterns = ["AI", "ai", "爱", "i", "哎", "诶", "唉", "A爱", "A艾", "A", "a", "艾", "阿爱", "阿艾"]
        
        # 基本组合匹配
        for tele in teleai_patterns:
            for ai in ai_patterns:
                if tele in text and ai in text:
                    print(f"🎯 匹配到TeleAI发音组合: {tele} + {ai}")
                    return True
        
        # 特殊模式：处理四音节分离式发音 (Te-le-A-I)
        four_syllable_patterns = [
            # 标准四音节模式
            "泰勒A爱", "太勒A爱", "泰来A爱", "台来A爱", "台勒A爱", "泰利A爱", "太利A爱", "泰里A爱",
            "泰勒A艾", "太勒A艾", "泰来A艾", "台来A艾", "台勒A艾", "泰利A艾", "太利A艾", "泰里A艾",
            "泰勒阿爱", "太勒阿爱", "泰来阿爱", "台来阿爱", "泰利阿爱", "太利阿爱",
            "泰勒阿艾", "太勒阿艾", "泰来阿艾", "台来阿艾", "泰利阿艾", "太利阿艾",
            "特勒A爱", "特来A爱", "特勒A艾", "特来A艾", "特勒阿爱", "特来阿爱",
            # 英文+中文混合
            "tele A爱", "tele A艾", "tele阿爱", "tele阿艾",
            "Tele A爱", "Tele A艾", "Tele阿爱", "Tele阿艾",
            # 其他变体
            "泰利AI", "太利AI", "台勒AI", "泰里AI", "特勒AI", "特来AI",
            "泰利ai", "太利ai", "台勒ai", "泰里ai", "特勒ai", "特来ai"
        ]
        
        for pattern in four_syllable_patterns:
            if pattern in text:
                print(f"🎯 匹配到TeleAI四音节发音模式: {pattern}")
                return True
        
        # 更灵活的模式匹配：检查四音节分离模式（允许中间有其他字符）
        import re
        # 匹配: tele音素 + (0-2个字符) + A音素 + (0-2个字符) + I音素
        flexible_pattern = r"(泰利|太利|泰勒|太勒|台来|泰来|台勒|泰里|特勒|特来|tele|Tele).{0,2}(A|a|阿).{0,2}(AI|ai|爱|艾|I|i|诶|哎)"
        if re.search(flexible_pattern, text):
            match = re.search(flexible_pattern, text)
            print(f"🎯 匹配到TeleAI四音节灵活模式: {match.group()}")
            return True
            
        # 额外的分离检测：检查是否同时包含tele音素和分离的A、I音素
        tele_present = any(tele in text for tele in ["泰利", "太利", "泰勒", "太勒", "台来", "泰来", "台勒", "泰里", "特勒", "特来", "tele", "Tele"])
        a_present = any(a in text for a in ["A", "a", "阿", "啊"])
        i_present = any(i in text for i in ["AI", "ai", "爱", "艾", "I", "i", "诶", "哎", "唉"])
        
        if tele_present and a_present and i_present:
            print(f"🎯 匹配到TeleAI分离音素模式: Tele+A+I组合")
            return True
        
        return False

    def intercept_identity_or_affiliation(self, text: str) -> Optional[str]:
        """拦截关于身份/归属的提问，直接返回规范答案。
        返回：若命中则返回要回复的文本，否则返回None。
        """
        q = text.strip().lower()
        # 常见身份类问题
        identity_keys = [
            "你是谁", "你是什么", "你的身份", "你叫什么", "你是哪位", "你的名字", "自我介绍", "你是哪个助手", "你来自哪", "你是什么助手",
            "你是豆包吗", "你是不是豆包", "豆包"
        ]
        # 常见归属类问题
        affiliation_keys = [
            "你属于哪家公司", "你属于谁", "你的公司是谁", "你们的公司是谁", "你们是谁的产品", "你背后是谁", "谁研发了你",
            "哪个公司开发", "隶属哪家公司", "归属", "归属于哪", "什么单位", "哪家单位", "哪个研究院", "哪个公司",
            "你们属于什么机构", "你们的机构", "你们的团队"
        ]

        if any(k in q for k in identity_keys):
            return "我是基于中国电信星辰大模型驱动的机器人智能助理。"
        if any(k in q for k in affiliation_keys):
            return "中国电信人工智能研究院。"
        return None

    async def receive_loop(self):
        """接收循环 - 完全按照官方"""
        try:
            while True:
                response = await self.client.receive_server_response()
                self.handle_server_response(response)
                if 'event' in response and (response['event'] == 152 or response['event'] == 153):
                    print(f"收到会话结束事件: {response['event']}")
                    self.is_session_finished = True
                    break
                if 'event' in response and response['event'] == 359 and not self.say_hello_over_event.is_set():
                    print(f"✅ say_hello结束事件")
                    self.say_hello_over_event.set()
        except asyncio.CancelledError:
            print("接收任务已取消")
        except Exception as e:
            print(f"❌ 接收消息错误: {e}")

    async def custom_say_hello(self) -> None:
        """发送自定义Hello消息"""
        payload = {
            "content": "你好，我是基于中国电信星辰大模型驱动的机器人智能助理，很高兴为您服务，希望能带给您舒适的体验。",
        }
        hello_request = bytearray(protocol.generate_header())
        hello_request.extend(int(300).to_bytes(4, 'big'))
        payload_bytes = str.encode(json.dumps(payload))
        payload_bytes = gzip.compress(payload_bytes)
        hello_request.extend((len(self.client.session_id)).to_bytes(4, 'big'))
        hello_request.extend(str.encode(self.client.session_id))
        hello_request.extend((len(payload_bytes)).to_bytes(4, 'big'))
        hello_request.extend(payload_bytes)
        await self.client.ws.send(hello_request)

    async def process_microphone_input(self) -> None:
        """处理麦克风输入 - 完全按照官方"""
        # 使用自定义的say_hello
        await self.custom_say_hello()
        
        # 等待say_hello协议事件完成
        await self.say_hello_over_event.wait()

        # 处理麦克风输入
        stream = self.audio_device.open_input_stream()
        print("🎤 基于中国电信星辰大模型驱动的机器人智能助理已准备就绪！")
        print("💡 功能说明：")
        print("   🤖 机器人控制：'机器人前进'、'让机器人左转'、'机器人停止'")
        print("   🧠 知识库问答：关于中国电信人工智能研究院、TeleAI等专业问题")
        print("   💬 日常聊天：正常对话即可")
        print("   ⌨️  按Ctrl+C退出")
        print("=" * 50)

        while self.is_recording:
            try:
                # 完全按照官方：exception_on_overflow=False
                audio_data = stream.read(self.input_audio_config["chunk"], exception_on_overflow=False)
                await self.client.task_request(audio_data)
                await asyncio.sleep(0.01)  # 避免CPU过度使用
            except Exception as e:
                print(f"❌ 读取麦克风数据出错: {e}")
                await asyncio.sleep(0.1)

    async def start(self) -> None:
        """启动对话会话 - 完全按照官方 + 集成功能"""
        try:
            print("🚀 Dragon机器人启动中...")
            print("🔧 初始化音频系统...")
            await self.client.connect()
            print("✅ 连接中国电信星辰大模型智能助理服务成功")
            
            # 显示功能状态
            print("\n📊 功能状态:")
            print(f"   🤖 机器人控制: {'✅ ROS已连接' if self.robot_controller.ros_enabled else '⚠️ 模拟模式'}")
            print(f"   🧠 知识库: {'✅ 已加载' if self.knowledge_base else '⚠️ 未加载'}")
            print(f"   🔄 自动管理: {'✅ 已启用' if self.auto_kb_manager else '⚠️ 未启用'}")
            print(f"   🎯 自定义Prompt: {'✅ 已加载' if PROMPT_CONFIG_AVAILABLE else '⚠️ 使用默认'}")
            print(f"   🎵 音色配置: {'✅ 已加载' if VOICE_CONFIG_AVAILABLE else '⚠️ 使用默认'}")

            # 启动任务 - 完全按照官方
            asyncio.create_task(self.process_microphone_input())
            asyncio.create_task(self.receive_loop())
            
            while self.is_running:
                await asyncio.sleep(0.1)

            await self.client.finish_session()
            while not self.is_session_finished:
                await asyncio.sleep(0.1)
            await self.client.finish_connection()
            await asyncio.sleep(0.1)
            await self.client.close()
            print(f"🔗 dialog request logid: {self.client.logid}")
            
        except KeyboardInterrupt:
            print("\n👋 用户中断，正在关闭...")
        except Exception as e:
            print(f"❌ 会话错误: {e}")
        finally:
            self.is_recording = False
            self.is_playing = False
            self.is_running = False
            self.audio_device.cleanup()
            print("🛑 系统已安全关闭")

async def main():
    """主函数"""
    print("🤖 基于中国电信星辰大模型驱动的机器人智能助理启动成功")
    print("🔧 基于官方星辰语音API + 完整功能集成")
    print("🌟 支持机器人控制、知识库问答、语音对话")
    print("=" * 60)
    
    session = DragonDialogSession()
    await session.start()

if __name__ == "__main__":
    asyncio.run(main())