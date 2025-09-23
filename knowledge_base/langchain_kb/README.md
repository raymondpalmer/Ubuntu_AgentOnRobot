# LangChain 知识库文件夹

- documents/: 放原始文档（pdf, docx, txt, md）
- vector_db/: 向量数据库（Chroma）持久化目录
- metadata.json: 可选的文档元数据（由系统自动生成/更新）

将你的文件放到 `documents/` 目录后，可以通过 `langchain_knowledge_base.py` 的 `add_document()` 方法导入并向量化。

示例（Python代码）：

```python
from langchain_knowledge_base import LangChainKnowledgeBase
kb = LangChainKnowledgeBase(knowledge_base_dir="knowledge_base/langchain_kb")
kb.add_document("knowledge_base/langchain_kb/documents/你的文件.pdf", category="teleai")
print(kb.get_stats())
```
