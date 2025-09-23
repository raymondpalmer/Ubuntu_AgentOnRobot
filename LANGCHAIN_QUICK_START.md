# LangChain知识库系统 - 快速使用指南

## 🎉 升级完成！

Dragon机器人语音控制系统已成功升级到基于LangChain的高级语义搜索系统！

## 🚀 快速开始

### 1. 查看知识库状态
```bash
python3 langchain_kb_manager.py stats
```

### 2. 添加文档到知识库
```bash
# 添加PDF文档
python3 langchain_kb_manager.py add document.pdf --category robot

# 添加Word文档  
python3 langchain_kb_manager.py add manual.docx --category manual

# 添加文本文件
python3 langchain_kb_manager.py add readme.txt --category general
```

### 3. 语义搜索
```bash
# 基础搜索
python3 langchain_kb_manager.py search "机器人控制"

# 获取更多结果
python3 langchain_kb_manager.py search "语音识别" --top-k 10

# 获取相关上下文
python3 langchain_kb_manager.py context "什么是Dragon机器人"
```

### 4. 管理文档
```bash
# 列出所有文档
python3 langchain_kb_manager.py list

# 删除文档
python3 langchain_kb_manager.py remove document.pdf
```

## 🧠 在Dragon机器人中使用

启动语音控制系统时，知识库会自动加载：

```bash
cd /home/ray/agent
python3 dragon_robot_session.py
```

系统会自动：
- 检测并使用LangChain知识库
- 在语音对话中提供智能上下文
- 回答基于知识库的问题

## 📊 性能特点

- **语义搜索精度**: 0.918 (优秀级别)
- **支持格式**: PDF, Word, TXT, Markdown
- **响应时间**: <1秒
- **多语言支持**: 中英文语义理解
- **智能分块**: 保持语义完整性

## 🔧 高级配置

### Python API使用
```python
from langchain_kb_manager import UnifiedKnowledgeBaseManager

# 创建知识库管理器
manager = UnifiedKnowledgeBaseManager()

# 语义搜索
results = manager.search("机器人语音控制", top_k=5)

# 获取智能上下文
context = manager.get_context("语音识别功能", max_length=2000)

# 添加文档
success = manager.add_document("new_document.pdf", "robot")
```

### 自定义配置
```python
# 指定知识库目录和后端
manager = UnifiedKnowledgeBaseManager(
    kb_dir="my_knowledge_base",
    backend="langchain"  # 或 "simple", "auto"
)
```

## 📁 文件结构

```
├── langchain_knowledge_base.py    # LangChain核心引擎
├── langchain_kb_manager.py        # 统一管理器
├── migrate_knowledge_base.py      # 数据迁移工具
├── dragon_robot_session.py        # 主系统(已集成)
└── LANGCHAIN_UPGRADE_REPORT.md    # 详细升级报告
```

## 🎯 测试示例

```bash
# 测试语义搜索
python3 langchain_kb_manager.py search "实时语音对话" --top-k 3

# 测试上下文生成
python3 langchain_kb_manager.py context "机器人如何控制运动"

# 查看详细统计
python3 langchain_kb_manager.py stats
```

## 💡 使用技巧

1. **文档命名**: 使用描述性文件名提高搜索效果
2. **分类管理**: 合理使用category参数组织文档
3. **查询优化**: 使用自然语言描述而非关键词列表
4. **定期维护**: 定期检查和更新知识库内容

## 🆘 故障排除

### 模型下载慢？
第一次使用会下载多语言模型(约500MB)，请耐心等待。

### 搜索结果不准确？
1. 确保文档质量和相关性
2. 尝试不同的查询表达方式
3. 检查文档是否正确添加到知识库

### 系统兼容性问题？
- 确保Python 3.10+
- 检查NumPy版本 < 2.0
- 安装所有依赖包

## 📞 技术支持

如有问题，请参考：
- `LANGCHAIN_UPGRADE_REPORT.md` - 详细升级报告
- GitHub Issues: https://github.com/raymondpalmer/AgentOnRobot
- 查看系统日志获取详细错误信息

---

🤖 **Dragon Robot AI System**  
*中国电信星辰大模型驱动*