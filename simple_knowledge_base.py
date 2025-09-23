"""
简化版本地知识库 - 无向量依赖
纯关键词搜索，支持多种文件格式
"""

import os
import json
import hashlib
from typing import List, Dict, Optional
from datetime import datetime
import logging

# 文档处理相关
try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleDocumentProcessor:
    """简单文档处理器"""
    
    @staticmethod
    def extract_text_from_pdf(file_path: str) -> str:
        """从PDF文件提取文本"""
        if not PDF_AVAILABLE:
            return ""
        try:
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f"PDF处理失败 {file_path}: {e}")
            return ""
    
    @staticmethod
    def extract_text_from_docx(file_path: str) -> str:
        """从Word文档提取文本"""
        if not DOCX_AVAILABLE:
            return ""
        try:
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f"Word文档处理失败 {file_path}: {e}")
            return ""
    
    @staticmethod
    def extract_text_from_txt(file_path: str) -> str:
        """从文本文件提取文本"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read().strip()
        except UnicodeDecodeError:
            # 尝试其他编码
            encodings = ['gbk', 'gb2312', 'latin-1']
            for enc in encodings:
                try:
                    with open(file_path, 'r', encoding=enc) as file:
                        return file.read().strip()
                except:
                    continue
            logger.error(f"无法读取文件 {file_path}: 编码问题")
            return ""
        except Exception as e:
            logger.error(f"文本文件处理失败 {file_path}: {e}")
            return ""
    
    @classmethod
    def extract_text(cls, file_path: str) -> tuple[str, str]:
        """根据文件扩展名提取文本"""
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == '.pdf':
            return cls.extract_text_from_pdf(file_path), 'PDF'
        elif ext in ['.docx', '.doc']:
            return cls.extract_text_from_docx(file_path), 'Word'
        elif ext in ['.txt', '.md', '.py', '.js', '.html', '.css', '.json']:
            return cls.extract_text_from_txt(file_path), '文本'
        else:
            logger.warning(f"不支持的文件格式: {ext}")
            return "", '未知'

class SimpleTextSplitter:
    """简单文本分割器"""
    
    @staticmethod
    def split_text(text: str, max_length: int = 500) -> List[str]:
        """按段落和长度分割文本"""
        if len(text) <= max_length:
            return [text]
        
        # 按段落分割
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        chunks = []
        current_chunk = ""
        
        for paragraph in paragraphs:
            # 如果单个段落太长，按句子分割
            if len(paragraph) > max_length:
                sentences = [s.strip() for s in paragraph.split('。') if s.strip()]
                for sentence in sentences:
                    if len(current_chunk) + len(sentence) <= max_length:
                        current_chunk += sentence + "。"
                    else:
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                        current_chunk = sentence + "。"
            else:
                if len(current_chunk) + len(paragraph) <= max_length:
                    current_chunk += paragraph + "\n\n"
                else:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = paragraph + "\n\n"
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks

class SimpleKnowledgeBase:
    """简化版本地知识库"""
    
    def __init__(self, knowledge_dir: str = "simple_knowledge_base"):
        self.knowledge_dir = knowledge_dir
        self.documents = []
        self.metadata = {}
        
        self.ensure_directories()
        self.load_knowledge_base()
    
    def ensure_directories(self):
        """确保必要的目录存在"""
        dirs = [
            self.knowledge_dir,
            f"{self.knowledge_dir}/documents",
            f"{self.knowledge_dir}/metadata"
        ]
        
        for dir_path in dirs:
            os.makedirs(dir_path, exist_ok=True)
    
    def get_file_hash(self, file_path: str) -> str:
        """计算文件哈希值"""
        hasher = hashlib.md5()
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except:
            return ""
    
    def add_document(self, file_path: str, title: str = None, category: str = None) -> bool:
        """添加文档到知识库"""
        if not os.path.exists(file_path):
            logger.error(f"文件不存在: {file_path}")
            return False
        
        # 检查文件是否已经添加过
        file_hash = self.get_file_hash(file_path)
        if file_hash in self.metadata:
            logger.info(f"文件已存在于知识库: {file_path}")
            return True
        
        # 提取文本内容
        content, file_type = SimpleDocumentProcessor.extract_text(file_path)
        if not content:
            logger.error(f"无法提取文件内容: {file_path}")
            return False
        
        # 分割文本
        chunks = SimpleTextSplitter.split_text(content, max_length=500)
        
        title = title or os.path.basename(file_path)
        doc_id = len(self.documents)
        
        # 添加文档片段
        for i, chunk in enumerate(chunks):
            doc = {
                'id': f"{doc_id}_{i}",
                'title': f"{title} (第{i+1}段)",
                'content': chunk,
                'source': file_path,
                'file_type': file_type,
                'category': category or '未分类',
                'chunk_index': i,
                'total_chunks': len(chunks),
                'created_at': datetime.now().isoformat(),
                'file_hash': file_hash
            }
            
            self.documents.append(doc)
        
        # 保存元数据
        self.metadata[file_hash] = {
            'file_path': file_path,
            'title': title,
            'file_type': file_type,
            'category': category or '未分类',
            'chunks_count': len(chunks),
            'added_at': datetime.now().isoformat()
        }
        
        logger.info(f"✅ 已添加文档: {title} ({len(chunks)}个片段)")
        return True
    
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """简单关键词搜索"""
        if not self.documents:
            return []
        
        query_words = set(query.lower().split())
        results = []
        
        for doc in self.documents:
            content_lower = doc['content'].lower()
            title_lower = doc['title'].lower()
            
            # 计算匹配度
            content_matches = sum(1 for word in query_words if word in content_lower)
            title_matches = sum(1 for word in query_words if word in title_lower)
            
            # 标题匹配权重更高
            total_score = content_matches + (title_matches * 2)
            
            if total_score > 0:
                result = doc.copy()
                result['score'] = total_score / len(query_words)
                results.append(result)
        
        # 按得分排序
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:top_k]
    
    def get_context_for_query(self, query: str, max_context_length: int = 1000) -> str:
        """为查询获取相关上下文"""
        results = self.search(query, top_k=2)
        
        if not results:
            return ""
        
        context = "📚 基于本地知识库的相关信息：\n\n"
        current_length = len(context)
        
        for i, result in enumerate(results, 1):
            section = f"{i}. 【{result['title']}】\n{result['content']}\n\n"
            
            if current_length + len(section) > max_context_length:
                break
            
            context += section
            current_length += len(section)
        
        context += "---\n请基于以上知识库信息回答用户问题。如果知识库中没有相关信息，请正常回答。\n\n"
        return context
    
    def save_knowledge_base(self):
        """保存知识库"""
        # 保存文档
        docs_path = f"{self.knowledge_dir}/documents/documents.json"
        with open(docs_path, 'w', encoding='utf-8') as f:
            json.dump(self.documents, f, ensure_ascii=False, indent=2)
        
        # 保存元数据
        meta_path = f"{self.knowledge_dir}/metadata/metadata.json"
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=2)
        
        logger.info("知识库已保存")
    
    def load_knowledge_base(self):
        """加载知识库"""
        docs_path = f"{self.knowledge_dir}/documents/documents.json"
        meta_path = f"{self.knowledge_dir}/metadata/metadata.json"
        
        try:
            if os.path.exists(docs_path):
                with open(docs_path, 'r', encoding='utf-8') as f:
                    self.documents = json.load(f)
                logger.info(f"📚 已加载 {len(self.documents)} 个文档片段")
            
            if os.path.exists(meta_path):
                with open(meta_path, 'r', encoding='utf-8') as f:
                    self.metadata = json.load(f)
                logger.info(f"📋 已加载 {len(self.metadata)} 个文件的元数据")
        except Exception as e:
            logger.error(f"加载知识库失败: {e}")
    
    def list_documents(self) -> List[Dict]:
        """列出所有文档"""
        return list(self.metadata.values())
    
    def get_statistics(self) -> Dict:
        """获取知识库统计信息"""
        file_types = {}
        categories = {}
        
        for doc in self.documents:
            file_type = doc.get('file_type', '未知')
            category = doc.get('category', '未分类')
            
            file_types[file_type] = file_types.get(file_type, 0) + 1
            categories[category] = categories.get(category, 0) + 1
        
        return {
            'total_files': len(self.metadata),
            'total_chunks': len(self.documents),
            'file_types': file_types,
            'categories': categories,
            'last_updated': datetime.now().isoformat()
        }

# 测试函数
if __name__ == "__main__":
    # 创建知识库实例
    kb = SimpleKnowledgeBase()
    
    # 示例用法
    print("🧠 简化版本地知识库系统测试")
    print(f"当前文档数量: {len(kb.documents)}")
    
    # 测试搜索
    if kb.documents:
        test_query = "机器人"
        print(f"\n🔍 测试搜索: '{test_query}'")
        results = kb.search(test_query)
        for i, result in enumerate(results, 1):
            print(f"{i}. {result['title']} (得分: {result['score']:.2f})")
            print(f"   {result['content'][:100]}...")
    
    # 获取统计信息
    stats = kb.get_statistics()
    print(f"\n📊 知识库统计: {json.dumps(stats, indent=2, ensure_ascii=False)}")
