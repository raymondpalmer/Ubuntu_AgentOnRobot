# Dragon机器人语音控制系统

🎤 基于豆包实时语音API的智能机器人语音控制系统，集成本地知识库功能

## 🚀 系统特色

- **🎙️ 实时语音识别** - 豆包ASR实时语音转文字
- **🤖 智能机器人控制** - 语音指令自动控制机器人运动
- **💬 豆包语音对话** - 真实的豆包TTS语音回应
- **🔄 连续对话** - 支持不间断的语音交互
- **⚡ 混合模式** - 同时支持聊天和控制功能
- **🧠 本地知识库** - 支持PDF、Word、文本等多格式文档智能检索

## 📁 项目结构

```
dragon-robot-voice-system/
├── dragon_robot_session.py          # 🎯 主程序 - 完整的语音控制系统
├── simple_knowledge_base.py         # 🧠 简化版知识库系统
├── simple_kb_manager.py             # 🛠️ 知识库管理工具
├── setup_knowledge_demo.sh          # 🔧 知识库演示设置脚本
├── official_example/                # 📚 豆包官方示例代码
├── utils/                           # 🛠️ 工具函数库
├── doubao_robot_voice_agent_starter/ # 📦 开发组件包
└── docs/                            # 📖 文档和示例知识库
```

## 🎯 核心功能演示

### 语音控制示例
```
用户: "你好，让机器人前进"
系统: ✅ 机器人执行前进
豆包: "好的，机器人已经向前移动了！"

用户: "机器人向左转"  
系统: ✅ 机器人执行左转
豆包: "收到，机器人已经向左转了！"
```

### 知识库问答示例
```
用户: "机器人怎么操作？"
系统: 🧠 搜索本地知识库...
豆包: "根据操作手册，机器人支持以下控制命令：1.机器人前进-控制机器人向前移动..."

用户: "语音识别不准确怎么办？"
系统: 🧠 搜索本地知识库...
豆包: "根据常见问题解答，请检查以下几点：确保麦克风正常工作、调节适当的音量..."
```

## 🚀 快速开始

### 1. 环境准备
```bash
# 配置环境
chmod +x setup_env.sh
./setup_env.sh

# 安装基础依赖
pip install -r requirements.txt

# 安装知识库依赖（可选）
pip install PyPDF2 python-docx
```

### 2. 配置API密钥
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，添加你的豆包API密钥
# DOUBAO_API_KEY=your_api_key_here
```

### 3. 设置知识库（可选但推荐）
```bash
# 一键设置演示知识库
./setup_knowledge_demo.sh

# 或手动添加文档
python3 simple_kb_manager.py --add "你的文档.pdf" --title "文档标题" --category "分类"
```

### 4. 启动系统
```bash
# 运行主程序
python3 dragon_robot_session.py
```

## 🧠 知识库功能

### 支持的文件格式
- **PDF文档** - 自动提取文本内容
- **Word文档** (.docx, .doc) - 支持段落和格式
- **文本文件** (.txt, .md) - 纯文本和Markdown
- **Python/JS文件** - 代码文档和注释

### 知识库管理命令
```bash
# 添加单个文档
python3 simple_kb_manager.py --add "file.pdf" --title "标题" --category "分类"

# 搜索知识库
python3 simple_kb_manager.py --search "关键词"

# 查看文档列表
python3 simple_kb_manager.py --list

# 查看统计信息
python3 simple_kb_manager.py --stats

# 功能测试
python3 simple_kb_manager.py --test
```

### 使用示例
```bash
# 添加技术文档
python3 simple_kb_manager.py --add "robot_manual.pdf" --title "机器人操作手册" --category "技术文档"

# 添加FAQ文档
python3 simple_kb_manager.py --add "faq.md" --title "常见问题" --category "帮助文档"

# 搜索相关信息
python3 simple_kb_manager.py --search "机器人控制"
```

## 🎮 支持的机器人控制命令

| 语音指令 | 机器人动作 | 备注 |
|---------|-----------|------|
| "机器人前进" | 向前移动 | 基础移动 |
| "机器人后退" | 向后移动 | 基础移动 |
| "机器人左转" | 向左转向 | 转向控制 |
| "机器人右转" | 向右转向 | 转向控制 |
| "机器人停止" | 停止运动 | 安全控制 |
| "抬起左手" | 左臂上举 | 关节控制 |
| "放下右手" | 右臂下放 | 关节控制 |

## 💡 知识库问答示例

| 用户提问 | 知识库搜索 | 智能回答 |
|---------|-----------|---------|
| "机器人怎么控制？" | 搜索操作手册 | 基于文档回答控制方法 |
| "语音识别不准确" | 搜索FAQ文档 | 提供故障排除建议 |
| "请假需要什么手续？" | 搜索规章制度 | 基于公司制度回答 |
| "安全注意事项" | 搜索安全文档 | 提供安全操作指南 |

## 🔧 技术架构

### 核心组件
- **WebSocket客户端** - 与豆包实时语音API通信
- **音频处理模块** - 实时音频捕获和播放
- **机器人控制接口** - ROS2动作路由器
- **智能指令解析** - 语音指令到机器人动作的映射
- **本地知识库** - 文档检索和上下文增强

### 知识库技术栈
- **文档处理** - PyPDF2, python-docx
- **文本分割** - 智能段落和句子分割
- **关键词搜索** - 基于词汇匹配的相似度计算
- **上下文增强** - 自动为用户查询添加相关背景信息

## 📋 系统要求

- **操作系统**: Linux (推荐Ubuntu 20.04+)
- **Python版本**: 3.8+
- **音频设备**: 麦克风和扬声器
- **网络连接**: 稳定的互联网连接
- **ROS2环境**: (可选) 用于实际机器人控制
- **存储空间**: 至少100MB用于知识库索引

## 🎛️ 配置选项

### 环境变量
```bash
# 豆包API配置
DOUBAO_API_KEY=your_api_key
DOUBAO_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
DOUBAO_MODEL=doubao-lite

# 音频配置
AUDIO_SAMPLE_RATE=16000
AUDIO_CHANNELS=1

# 知识库配置
KNOWLEDGE_BASE_DIR=simple_knowledge_base
MAX_CONTEXT_LENGTH=1000
```

## 🐛 常见问题

### 音频问题
```bash
# 检查音频设备
python -c "import pyaudio; p=pyaudio.PyAudio(); print([p.get_device_info_by_index(i) for i in range(p.get_device_count())])"

# WSL2音频配置
export PULSE_SERVER=tcp:localhost:4713
```

### 知识库问题
- **搜索无结果**: 检查文档是否正确添加，尝试不同关键词
- **文档添加失败**: 确认文件格式支持，检查文件权限
- **编码问题**: 使用UTF-8编码保存文本文件

### 网络连接
- 确保网络连接稳定
- 检查API密钥是否正确
- 验证豆包API服务状态

## 📊 性能优化

### 知识库优化
- **文档分割**: 控制文档片段大小，提高搜索精度
- **关键词匹配**: 使用同义词和相关词提高召回率
- **缓存机制**: 频繁查询的结果进行缓存
- **索引管理**: 定期清理和重建索引

## 📚 更多文档

- [音频设置指南](AUDIO_SETUP_GUIDE.md)
- [WSL2音频配置](WSL2_AUDIO_GUIDE.md)  
- [GitHub设置指南](GITHUB_SETUP.md)
- [项目完成报告](PROJECT_COMPLETION_REPORT.md)

## 🎯 使用场景

### 企业办公
- 公司规章制度查询
- 技术文档检索
- 操作手册指导
- 培训材料问答

### 教育培训
- 课程资料查询
- 实验指导获取
- 理论知识问答
- 学习进度跟踪

### 技术支持
- 故障排除指南
- 产品使用说明
- 维护保养指导
- 安全操作规范

## 📄 许可证

本项目基于MIT许可证开源。详见 [LICENSE](LICENSE) 文件。

## 🤝 贡献

欢迎提交问题和拉取请求！

## 📧 联系

如有问题，请通过GitHub Issues联系。

---

*🎯 让语音控制机器人变得简单而智能！集成本地知识库，让对话更有深度！*
