# 🤖 Dragon机器人语音控制系统

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)]()

🎤 基于豆包实时语音API的智能机器人语音控制系统，集成本地知识库功能，实现语音控制与智能问答的完美结合。

![Dragon Robot System](https://img.shields.io/badge/Dragon_Robot-Voice_Control-orange.svg)

## 🌟 核心特性

### 🎯 语音控制功能
- **🎙️ 实时语音识别** - 豆包ASR高精度语音转文字
- **🤖 智能机器人控制** - 语音指令自动控制机器人运动
- **💬 豆包语音对话** - 真实的豆包TTS语音回应
- **🔄 连续对话模式** - 支持不间断的语音交互体验
- **⚡ 混合智能模式** - 同时支持聊天和控制功能

### 🧠 知识库功能
- **📚 多格式文档支持** - PDF、Word、文本、Markdown等
- **🔍 智能文档检索** - 关键词匹配和语义搜索
- **💡 上下文增强对话** - 基于本地知识的智能回答
- **🛠️ 可视化管理工具** - 简单易用的知识库管理
- **🏷️ 分类标签系统** - 文档分类和快速定位

### 🎯 Prompt自定义系统
- **🎭 多角色配置** - 默认、友好、专业、技术等多种角色
- **🎪 场景适配** - 工业、家庭、教育等专门场景配置
- **💬 语言风格调节** - 自然、温暖、专业、活力、平和多种风格
- **📝 模板化管理** - 系统化的prompt模板和配置工具
- **🔧 动态配置更新** - 运行时无需重启即可更新配置

## 📁 项目结构

```
AgentOnRobot/
├── 🎯 核心系统
│   ├── dragon_robot_session.py          # 主程序 - 完整语音控制系统
│   ├── simple_knowledge_base.py         # 本地知识库核心引擎
│   ├── simple_kb_manager.py             # 知识库管理工具
│   ├── dragon_prompts_config.py         # Prompt配置系统
│   └── prompt_manager.py                # Prompt管理工具
│
├── 🛠️ 工具组件
│   ├── official_example/                # 豆包官方示例代码
│   ├── utils/                           # 工具函数库
│   ├── doubao_robot_voice_agent_starter/ # 开发组件包
│   ├── prompt_demo.py                   # Prompt演示脚本
│   └── setup_*.sh                       # 环境配置脚本
│
├── 📚 文档与演示
│   ├── docs/examples/                   # 演示知识库文档
│   ├── KNOWLEDGE_SYSTEM_GUIDE.md        # 知识库完整使用指南
│   ├── PROMPT_CUSTOMIZATION_GUIDE.md    # Prompt自定义指南
│   ├── README_KNOWLEDGE.md              # 知识库技术文档
│   └── demo_knowledge_system.sh         # 一键演示脚本
│
└── 🗃️ 数据存储
    ├── simple_knowledge_base/           # 知识库数据目录
    └── knowledge_base/                  # 备用知识库
```

## 🚀 快速开始

### 📋 环境要求

- **操作系统**: Linux (推荐Ubuntu 20.04+)
- **Python版本**: 3.8+
- **硬件要求**: 麦克风 + 扬声器
- **网络要求**: 稳定的互联网连接
- **存储空间**: 至少500MB

### ⚙️ 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/raymondpalmer/AgentOnRobot.git
cd AgentOnRobot
```

2. **环境配置**
```bash
# 自动配置环境
chmod +x setup_env.sh
./setup_env.sh

# 安装Python依赖
pip install -r requirements.txt

# 安装知识库依赖（可选）
pip install PyPDF2 python-docx openpyxl
```

3. **API配置**
```bash
# 复制配置模板
cp .env.example .env

# 编辑配置文件，添加豆包API密钥
nano .env
```

配置内容：
```env
DOUBAO_API_KEY=your_api_key_here
DOUBAO_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
DOUBAO_MODEL=doubao-lite
```

4. **知识库初始化**
```bash
# 一键设置演示知识库
chmod +x demo_knowledge_system.sh
./demo_knowledge_system.sh
```

5. **启动系统**
```bash
python3 dragon_robot_session.py
```

## 🎮 使用指南

### 🤖 机器人控制命令

| 语音指令 | 机器人动作 | 说明 |
|---------|-----------|------|
| "机器人前进" | 向前移动 | 默认移动1米 |
| "机器人后退" | 向后移动 | 注意后方安全 |
| "机器人左转" | 向左转向 | 转向90度 |
| "机器人右转" | 向右转向 | 转向90度 |
| "机器人停止" | 停止运动 | 紧急停止所有动作 |
| "抬起左手" | 左臂上举 | 抬起到90度 |
| "抬起右手" | 右臂上举 | 抬起到90度 |
| "放下左手" | 左臂下放 | 回到自然位置 |
| "放下右手" | 右臂下放 | 回到自然位置 |

### 🧠 知识库问答示例

| 用户提问 | 系统响应 | 知识来源 |
|---------|---------|---------|
| "机器人怎么操作？" | 详细操作指南 | 操作手册 |
| "语音识别不准确怎么办？" | 故障排除步骤 | FAQ文档 |
| "安全注意事项有哪些？" | 完整安全指南 | 安全文档 |
| "请假需要什么手续？" | 请假流程说明 | 规章制度 |

### 📚 知识库管理

#### 查看现有文档
```bash
python3 simple_kb_manager.py --list
```

#### 添加新文档
```bash
# 添加PDF文档
python3 simple_kb_manager.py --add "manual.pdf" --title "产品手册" --category "技术文档"

# 添加Word文档
python3 simple_kb_manager.py --add "report.docx" --title "项目报告" --category "项目文档"

# 添加文本文件
python3 simple_kb_manager.py --add "readme.txt" --title "使用说明" --category "帮助文档"
```

#### 搜索测试
```bash
python3 simple_kb_manager.py --search "机器人控制"
python3 simple_kb_manager.py --search "语音识别问题"
python3 simple_kb_manager.py --search "安全注意事项"
```

#### 查看统计信息
```bash
python3 simple_kb_manager.py --stats
```

### 🎯 自定义Prompt配置

#### 查看当前配置
```bash
python3 prompt_manager.py show
```

#### 测试不同角色
```bash
# 测试友好角色
python3 prompt_manager.py test friendly

# 测试专业角色  
python3 prompt_manager.py test professional

# 测试技术角色
python3 prompt_manager.py test technical
```

#### 配置管理
```bash
# 编辑配置文件
python3 prompt_manager.py edit

# 备份当前配置
python3 prompt_manager.py backup

# 验证配置文件
python3 prompt_manager.py validate

# 恢复配置
python3 prompt_manager.py restore <backup_file>
```

#### 运行演示
```bash
# 完整演示
python3 prompt_demo.py

# 交互式演示
python3 prompt_demo.py interactive
```

#### 在代码中使用
```python
from dragon_prompts_config import DragonRobotPrompts

# 创建配置实例
prompts = DragonRobotPrompts()

# 获取不同场景配置
industrial_config = prompts.get_session_config("industrial", "professional")
home_config = prompts.get_session_config("home", "warm")

# 添加自定义角色
prompts.add_custom_role("customer_service", "你是专业的客服助手...")
```

## 🎯 实际应用场景

### 🏢 企业办公
- **规章制度查询** - "请假流程是什么？"
- **技术文档检索** - "API接口怎么调用？"
- **操作手册指导** - "设备怎么维护？"
- **培训材料问答** - "新员工培训内容？"

### 🎓 教育培训
- **课程资料查询** - "第三章讲什么内容？"
- **实验指导获取** - "实验步骤是什么？"
- **理论知识问答** - "这个概念怎么理解？"
- **学习进度跟踪** - "下节课学什么？"

### 🔧 技术支持
- **故障排除指南** - "设备报错怎么处理？"
- **产品使用说明** - "功能怎么使用？"
- **维护保养指导** - "多久保养一次？"
- **安全操作规范** - "操作注意什么？"

### 🏥 智能客服
- **常见问题解答** - 基于FAQ文档自动回答
- **产品信息查询** - 基于产品手册提供信息
- **服务流程指导** - 基于服务文档引导操作
- **技术支持协助** - 基于技术文档提供帮助

### 🎭 多角色场景适配

#### 🏭 工业制造场景
- **安全监督角色** - 严格安全规范，及时风险警告
- **技术指导角色** - 专业术语，精确操作指导
- **质量检验角色** - 质量标准，检验流程指导

#### 🏠 家庭服务场景
- **生活助手角色** - 温和亲切，生活化建议
- **老人关怀角色** - 语速适中，重复重要信息
- **儿童教育角色** - 简单易懂，鼓励性语言

#### 🎓 教育培训场景
- **学习伙伴角色** - 启发引导，鼓励探索
- **专业导师角色** - 权威解答，系统性教学
- **实验指导角色** - 步骤详细，安全提醒

#### 🏢 商务服务场景
- **专业顾问角色** - 商务用语，数据支撑
- **客服代表角色** - 耐心解答，服务导向
- **技术支持角色** - 问题诊断，解决方案

## 🔧 技术架构

### 🏗️ 系统架构
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   语音输入层     │    │   智能处理层     │    │   执行输出层     │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ • 麦克风采集     │───▶│ • 语音识别       │───▶│ • 机器人控制     │
│ • 噪音过滤       │    │ • 意图识别       │    │ • 语音合成       │
│ • 音频预处理     │    │ • 知识库搜索     │    │ • 动作执行       │
└─────────────────┘    │ • 上下文增强     │    └─────────────────┘
                       │ • 豆包对话       │
                       └─────────────────┘
```

### 🧠 知识库技术栈
- **文档处理** - PyPDF2, python-docx, openpyxl
- **文本分析** - 智能分段、关键词提取
- **检索算法** - 关键词匹配 + 相似度计算
- **上下文管理** - 自动上下文增强和优化

### � Prompt系统架构
- **角色管理** - 多角色配置、动态切换
- **场景适配** - 工业、家庭、教育等专门配置
- **风格控制** - 语言风格、语调、用词管理
- **模板引擎** - 可配置的对话模板系统
- **配置热更新** - 运行时配置更新机制

### �🎤 语音技术栈
- **ASR引擎** - 豆包实时语音识别API
- **TTS引擎** - 豆包语音合成API  
- **音频处理** - PyAudio实时音频流处理
- **WebSocket** - 实时双向通信协议

## ⚙️ 配置选项

### 🌐 环境变量配置
```bash
# 豆包API配置
DOUBAO_API_KEY=your_api_key              # 必填：豆包API密钥
DOUBAO_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
DOUBAO_MODEL=doubao-lite                 # 模型选择

# 音频配置
AUDIO_SAMPLE_RATE=16000                  # 采样率
AUDIO_CHANNELS=1                         # 声道数
AUDIO_CHUNK_SIZE=1024                    # 音频块大小

# 知识库配置
KNOWLEDGE_BASE_DIR=simple_knowledge_base  # 知识库目录
MAX_CONTEXT_LENGTH=1000                   # 最大上下文长度
SEARCH_TOP_K=3                           # 搜索结果数量
```

### 🎚️ 系统参数调整
编辑 `simple_knowledge_base.py`:
```python
# 文档分割参数
max_length = 500          # 单个文档片段最大长度
overlap = 50             # 片段间重叠字符数

# 搜索参数
score_threshold = 0.3    # 搜索相似度阈值
max_results = 5          # 最大返回结果数

# 性能参数
cache_size = 1000        # 缓存大小
index_update_interval = 3600  # 索引更新间隔(秒)
```

### 🎯 Prompt系统配置
编辑 `dragon_prompts_config.py`:
```python
# 系统角色配置
self.system_roles = {
    "default": "你的默认角色描述...",
    "custom": "你的自定义角色..."
}

# 说话风格配置
self.speaking_styles = {
    "natural": "自然友好的语调...",
    "professional": "专业稳重的语调..."
}

# 场景配置
self.scenario_prompts = {
    "industrial": {
        "system_role": "工业场景专用角色...",
        "greeting": "工业问候语..."
    }
}

# 对话参数配置
self.dialog_config = {
    "max_tokens": 1500,
    "temperature": 0.7,
    "top_p": 0.9
}
```

## 🐛 故障排除

### 🎤 音频相关问题

#### 问题：语音识别不准确
**解决方案**：
```bash
# 1. 检查音频设备
python3 -c "import pyaudio; p=pyaudio.PyAudio(); [print(f'{i}: {p.get_device_info_by_index(i)[\"name\"]}') for i in range(p.get_device_count())]"

# 2. 调整音频设置
export PULSE_SERVER=tcp:localhost:4713  # WSL2音频配置

# 3. 测试麦克风
arecord -d 5 test.wav && aplay test.wav
```

#### 问题：没有语音输出
**解决方案**：
- 检查扬声器连接
- 验证音频驱动安装
- 确认音量设置正确

### 🌐 网络连接问题

#### 问题：API调用失败
**解决方案**：
```bash
# 1. 测试网络连接
ping ark.cn-beijing.volces.com

# 2. 检查API密钥
python3 check_api_config.py

# 3. 验证配置文件
cat .env | grep DOUBAO
```

### 📚 知识库相关问题

#### 问题：文档添加失败
**解决方案**：
- 检查文件格式是否支持
- 确认文件路径正确
- 验证文件编码为UTF-8

#### 问题：搜索无结果
**解决方案**：
- 使用更具体的关键词
- 检查文档内容是否包含相关信息
- 尝试重建索引

## 📊 性能优化

### 🚀 系统优化建议
1. **硬件优化**
   - 使用SSD存储提高索引速度
   - 增加内存减少磁盘I/O
   - 使用有线网络确保稳定连接

2. **软件优化**
   - 定期清理知识库索引
   - 控制文档数量和大小
   - 优化搜索关键词

3. **配置优化**
   - 调整音频缓冲区大小
   - 优化知识库搜索参数
   - 配置合适的并发数

### 📈 监控指标
```bash
# 系统状态监控
python3 simple_kb_manager.py --stats

# 性能测试
python3 simple_kb_manager.py --test

# 资源使用情况
htop
df -h
```

## 📖 详细文档

- 📘 [完整使用指南](KNOWLEDGE_SYSTEM_GUIDE.md) - 详细的功能说明和使用教程
- 📗 [知识库技术文档](README_KNOWLEDGE.md) - 技术架构和API文档  
- 📙 [音频设置指南](AUDIO_SETUP_GUIDE.md) - 音频配置和故障排除
- 📕 [WSL2配置指南](WSL2_AUDIO_GUIDE.md) - Windows子系统音频设置
- 📔 [GitHub设置指南](GITHUB_SETUP.md) - 项目部署和版本管理
- 📓 [项目完成报告](PROJECT_COMPLETION_REPORT.md) - 开发历程和技术总结

## 🤝 贡献指南

我们欢迎所有形式的贡献！

### 🔧 开发贡献
1. Fork 本项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建Pull Request

### 📝 文档贡献
- 改进使用说明
- 添加示例代码
- 翻译文档
- 修复错误

### 🐛 问题报告
在提交Issue时，请提供：
- 详细的问题描述
- 复现步骤
- 系统环境信息
- 相关日志和截图

## 📋 更新日志

### v2.0.0 (2025-09-10) - 知识库集成版本
- ✨ 新增本地知识库功能
- 🚀 支持PDF、Word、文本等多格式文档
- 🔍 集成智能文档检索和上下文增强
- 🛠️ 添加可视化知识库管理工具
- 📚 提供完整的演示文档和使用指南

### v1.0.0 - 基础语音控制版本
- 🎤 实现基础语音识别功能
- 🤖 支持机器人基本控制命令
- 💬 集成豆包语音对话功能
- 🔄 实现连续对话模式

## 📄 开源协议

本项目基于 [MIT协议](LICENSE) 开源。

## 🌟 致谢

感谢以下项目和技术的支持：
- [豆包AI](https://www.volcengine.com/product/doubao) - 提供强大的语音AI能力
- [PyAudio](https://pypi.org/project/PyAudio/) - 音频处理核心库
- [PyPDF2](https://pypi.org/project/PyPDF2/) - PDF文档处理
- [python-docx](https://python-docx.readthedocs.io/) - Word文档处理

## 📞 联系我们

- **项目主页**: [GitHub Repository](https://github.com/raymondpalmer/AgentOnRobot)
- **问题反馈**: [GitHub Issues](https://github.com/raymondpalmer/AgentOnRobot/issues)
- **功能建议**: [GitHub Discussions](https://github.com/raymondpalmer/AgentOnRobot/discussions)

---

<div align="center">

**🎯 让语音控制机器人变得简单而智能！**

**🧠 集成本地知识库，让对话更有深度！**

[![⭐ Star this repo](https://img.shields.io/badge/⭐-Star_this_repo-yellow.svg)](https://github.com/raymondpalmer/AgentOnRobot)
[![🍴 Fork this repo](https://img.shields.io/badge/🍴-Fork_this_repo-blue.svg)](https://github.com/raymondpalmer/AgentOnRobot/fork)
[![📝 Report Bug](https://img.shields.io/badge/📝-Report_Bug-red.svg)](https://github.com/raymondpalmer/AgentOnRobot/issues)

Made with ❤️ by Dragon Robot Team

</div>
