# 📁 自动知识库文件管理指南

## 🎯 概述

现在您可以直接将文档放入 `/home/ray/agent/knowledge_base/files/` 文件夹，系统会在启动时自动扫描并更新知识库！

## 📂 文件存放位置

### Windows访问路径
```
\\wsl.localhost\Ubuntu-22.04\home\ray\agent\knowledge_base\files\
```

### Linux路径
```
/home/ray/agent/knowledge_base/files/
```

## 📋 支持的文件格式

- **PDF文件** (.pdf) - 手册、报告、说明书
- **Word文档** (.docx, .doc) - 公司文档、操作指南  
- **文本文件** (.txt) - 简单文档、配置说明
- **Markdown** (.md, .markdown) - 技术文档、README文件

## 🔄 自动更新机制

### 启动时自动扫描
当您启动Dragon机器人系统时，系统会：

1. **自动扫描** `knowledge_base/files/` 目录
2. **检测新文件** - 自动添加到知识库
3. **检测修改** - 更新已变更的文档
4. **智能分类** - 根据文件名和内容自动分类
5. **显示报告** - 告知更新结果

### 智能分类规则

系统会根据文件名和内容自动分类：

| 分类 | 关键词 | 示例文件名 |
|------|--------|------------|
| `manual` | 手册、说明书、guide | robot_manual.pdf |
| `policy` | 制度、规章、政策 | company_policy.docx |
| `tech` | 技术、开发、api | api_docs.md |
| `faq` | 问答、帮助、help | common_questions.txt |
| `robot` | 机器人、控制 | robot_control.pdf |
| `official` | 官方、readme | official_guide.md |

## 🚀 使用方法

### 方法1: 直接拖拽文件（推荐）

1. **打开文件夹**：
   ```
   \\wsl.localhost\Ubuntu-22.04\home\ray\agent\knowledge_base\files\
   ```

2. **拖拽文件**：直接将PDF、Word、TXT等文件拖入此文件夹

3. **启动系统**：运行Dragon机器人，系统自动更新知识库
   ```bash
   cd /home/ray/agent
   python3 dragon_robot_session.py
   ```

4. **查看结果**：启动过程中会显示更新报告

### 方法2: 手动触发更新

如果系统已经在运行，可以手动触发更新：

```bash
# 扫描并更新知识库
python3 auto_kb_manager.py --scan

# 查看自动管理器状态
python3 auto_kb_manager.py --status

# 强制重新扫描所有文件
python3 auto_kb_manager.py --force-rescan
```

## 📊 启动时的输出示例

```
🧠 LangChain知识库已加载 (后端: langchain)
🔄 自动知识库管理器已初始化
📁 正在扫描 knowledge_base/files 目录...
✅ 成功添加到知识库: robot_manual.pdf (分类: robot)
✅ 成功添加到知识库: company_policy.docx (分类: policy)
✅ 自动更新完成: 新增2个，更新0个文档
📚 最终统计 - 文档数: 3, 分块数: 15
```

## 📁 推荐的文件组织方式

### 直接放入主目录
```
knowledge_base/files/
├── robot_manual.pdf          # 机器人操作手册
├── safety_policy.docx        # 安全管理制度
├── api_documentation.md      # API技术文档
├── faq_common_issues.txt     # 常见问题解答
└── official_readme.md        # 官方说明文档
```

### 或者使用子文件夹组织（同样会被扫描）
```
knowledge_base/files/
├── manuals/
│   ├── robot_operation.pdf
│   └── maintenance_guide.docx
├── policies/
│   ├── safety_rules.pdf
│   └── work_procedures.docx
└── technical/
    ├── api_docs.md
    └── configuration.txt
```

## 🔧 手动管理工具

### 查看知识库状态
```bash
python3 auto_kb_manager.py --status
```

### 强制重新处理所有文件
```bash
python3 auto_kb_manager.py --force-rescan
```

### 监控特定目录
```bash
python3 auto_kb_manager.py --watch-dir custom_docs/ --scan
```

## 💡 使用技巧

### 1. 文件命名建议
- **描述性名称**：`robot_operation_manual_v2.pdf`
- **包含版本**：`api_docs_2024.md`
- **添加日期**：`safety_policy_20240901.docx`

### 2. 内容组织建议
- **一个主题一个文件**：不要将所有内容混在一个大文件中
- **标准格式**：使用统一的标题和段落格式
- **关键词优化**：在文档中包含用户可能搜索的关键词

### 3. 更新最佳实践
- **替换旧版本**：直接替换同名文件，系统会自动检测更新
- **删除过时文档**：删除不需要的文件，系统会检测到变化
- **定期维护**：定期检查和更新文档内容

## 🎮 在语音对话中使用

添加文档后，就可以在语音对话中直接询问：

### 示例对话
- **用户**："机器人怎么进行日常维护？"
- **系统**：自动搜索 `robot_manual.pdf` → 基于文档内容回答

- **用户**："公司的安全规定是什么？"
- **系统**：搜索 `safety_policy.docx` → 提供准确的制度信息

## 🆘 故障排除

### 文件没有被自动添加？
1. 检查文件格式是否支持（.pdf, .docx, .txt, .md）
2. 确认文件确实在 `knowledge_base/files/` 目录中
3. 查看启动日志是否有错误信息
4. 手动运行 `python3 auto_kb_manager.py --scan`

### 搜索不到文档内容？
1. 确认文档已成功添加（查看启动日志）
2. 尝试使用文档中的确切词汇搜索
3. 检查文档内容是否为纯文本（扫描版PDF可能识别不了）

### 文件更新没有被检测到？
1. 文件名或内容确实发生了变化
2. 重启Dragon机器人系统
3. 使用 `--force-rescan` 强制重新扫描

## 📈 高级功能

### 自定义监控目录
```python
# 在代码中自定义
auto_manager = AutoKnowledgeBaseManager(
    watch_dirs=["knowledge_base/files", "custom_docs", "shared_documents"]
)
```

### 自定义分类规则
可以修改 `auto_kb_manager.py` 中的 `category_rules` 来自定义分类逻辑。

---

🤖 **Dragon Robot AI System - 中国电信星辰大模型驱动**

现在您只需要将文档拖拽到指定文件夹，系统就会自动处理一切！🎉