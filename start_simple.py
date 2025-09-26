#!/usr/bin/env python3
"""
简化版Dragon语音机器人启动器 - 跳过LangChain知识库
仅启动基础语音识别和机器人控制功能
"""

import os
import sys

# 临时禁用LangChain知识库模块
os.environ['DISABLE_LANGCHAIN_KB'] = '1'

# 动态加入官方示例路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OFFICIAL_DIR = os.path.join(BASE_DIR, 'official_example')
if OFFICIAL_DIR not in sys.path:
    sys.path.append(OFFICIAL_DIR)

try:
    print("🚀 启动Dragon语音机器人系统...")
    print("📋 功能说明:")
    print("  - 语音识别和TTS播放")
    print("  - 机器人控制命令 (cmd_1 到 cmd_6)")
    print("  - 基础对话功能")
    print("  ⚠️  知识库功能已禁用")
    print("-" * 50)
    
    # 导入并运行主系统
    from dragon_official_exact import main
    main()
    
except KeyboardInterrupt:
    print("\n👋 用户退出系统")
except Exception as e:
    print(f"\n❌ 启动失败: {e}")
    print("💡 建议检查:")
    print("  1. API配置是否正确 (setup_env.sh)")
    print("  2. 音频设备是否可用")
    print("  3. 网络连接是否正常")