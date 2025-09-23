"""
多格式本地知识库系统
支持PDF、Word、文本文件等格式
集成向量搜索和语义检索
"""

import os
import json
import pickle
import hashlib
from typing import List, Dict, Tuple, Optional
from datetime import datetime
import logging

# 文档处理相关
import PyPDF2
import docx
from docx import Document
import pandas as pd

# 向量处理相关
try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    from sklearn.metrics.pairwise import cosine_similarity
    VECTOR_AVAILABLE = True
except ImportError:
    VECTOR_AVAILABLE = False
    print("⚠️ 向量搜索库未安装，将使用关键词搜索")

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentProcessor:
    """文档处理器 - 支持多种格式"""
    
    @staticmethod
    def extract_text_from_pdf(file_path: str) -> str:
        """从PDF文件提取文本"""
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
    def extract_text_from_txt(file_path: str, encoding: str = 'utf-8') -> str:
        """从文本文件提取文本"""
        try:
            with open(file_path, 'r', encoding=encoding) as file:
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
    
    @staticmethod
    def extract_text_from_csv(file_path: str) -> str:
        """从CSV文件提取文本"""
        try:
            df = pd.read_csv(file_path)
            # 将DataFrame转换为文本描述
            text = f"CSV文件内容摘要：\n"
            text += f"共{len(df)}行，{len(df.columns)}列\n"
            text += f"列名：{', '.join(df.columns)}\n\n"
            
            # 添加前几行数据作为示例
            text += "数据示例：\n"
            text += df.head(5).to_string(index=False)
            
            return text
        except Exception as e:
            logger.error(f"CSV文件处理失败 {file_path}: {e}")
            return ""
    
    @classmethod
    def extract_text(cls, file_path: str) -> Tuple[str, str]:
        """根据文件扩展名提取文本"""
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == '.pdf':
            return cls.extract_text_from_pdf(file_path), 'pdf'
        elif ext in ['.docx', '.doc']:
            return cls.extract_text_from_docx(file_path), 'docx'
        elif ext in ['.txt', '.md', '.py', '.js', '.html', '.css', '.json']:
            return cls.extract_text_from_txt(file_path), 'text'
        elif ext == '.csv':
            return cls.extract_text_from_csv(file_path), 'csv'
        else:
            logger.warning(f"不支持的文件格式: {ext}")
            return "", 'unknown'

class TextSplitter:
    """文本分割器"""
    
    @staticmethod
    def split_by_paragraphs(text: str, max_length: int = 500, overlap: int = 50) -> List[str]:
        """按段落分割文本，支持重叠"""
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        chunks = []
        current_chunk = ""
        
        for paragraph in paragraphs:
            # 如果单个段落太长，进一步分割
            if len(paragraph) > max_length:
                sub_chunks = TextSplitter.split_by_sentences(paragraph, max_length)
                for sub_chunk in sub_chunks:
                    if len(current_chunk) + len(sub_chunk) <= max_length:
                        current_chunk += sub_chunk + "\n"
                    else:
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                        current_chunk = sub_chunk + "\n"
            else:
                if len(current_chunk) + len(paragraph) <= max_length:
                    current_chunk += paragraph + "\n\n"
                else:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = paragraph + "\n\n"
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        # 添加重叠
        if overlap > 0 and len(chunks) > 1:
            overlapped_chunks = []
            for i, chunk in enumerate(chunks):
                if i == 0:
                    overlapped_chunks.append(chunk)
                else:
                    # 从前一个chunk的末尾取一些文本作为重叠
                    prev_chunk = chunks[i-1]
                    overlap_text = prev_chunk[-overlap:] if len(prev_chunk) > overlap else prev_chunk
                    overlapped_chunks.append(overlap_text + "\n" + chunk)
            return overlapped_chunks
        
        return chunks
    
    @staticmethod
    def split_by_sentences(text: str, max_length: int = 500) -> List[str]:
        """按句子分割文本"""
        import re
        sentences = re.split(r'[.!?。！？]+', text)
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            if len(current_chunk) + len(sentence) <= max_length:
                current_chunk += sentence + "。"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + "。"
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks

class VectorSearchEngine:
    """向量搜索引擎"""
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        if not VECTOR_AVAILABLE:
            raise ImportError("向量搜索依赖未安装")
        
        self.model = SentenceTransformer(model_name)
        self.embeddings = None
        self.documents = []
    
    def build_index(self, documents: List[Dict]):
        """构建向量索引"""
        self.documents = documents
        texts = [doc['content'] for doc in documents]
        
        logger.info(f"正在构建 {len(texts)} 个文档的向量索引...")
        self.embeddings = self.model.encode(texts, show_progress_bar=True)
        logger.info("向量索引构建完成")
    
    def search(self, query: str, top_k: int = 5, threshold: float = 0.3) -> List[Dict]:
        """向量搜索"""
        if self.embeddings is None:
            return []
        
        query_embedding = self.model.encode([query])
        similarities = cosine_similarity(query_embedding, self.embeddings)[0]
        
        # 获取最相关的文档
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            if similarities[idx] > threshold:
                result = self.documents[idx].copy()
                result['score'] = float(similarities[idx])
                results.append(result)
        
        return results
    
    def save_index(self, file_path: str):
        """保存向量索引"""
        if self.embeddings is not None:
            with open(file_path, 'wb') as f:
                pickle.dump({
                    'embeddings': self.embeddings,
                    'documents': self.documents
                }, f)
    
    def load_index(self, file_path: str):
        """加载向量索引"""
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                data = pickle.load(f)
                self.embeddings = data['embeddings']
                self.documents = data['documents']
            return True
        return False

class KeywordSearchEngine:
    """关键词搜索引擎（备用方案）"""
    
    def __init__(self):
        self.documents = []
    
    def build_index(self, documents: List[Dict]):
        """构建关键词索引"""
        self.documents = documents
        logger.info(f"关键词搜索引擎已加载 {len(documents)} 个文档")
    
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """关键词搜索"""
        query_words = set(query.lower().split())
        results = []
        
        for doc in self.documents:
            content_words = set(doc['content'].lower().split())
            # 计算关键词重叠度
            overlap = len(query_words.intersection(content_words))
            if overlap > 0:
                score = overlap / len(query_words)
                result = doc.copy()
                result['score'] = score
                results.append(result)
        
        # 按得分排序
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:top_k]

class LocalKnowledgeBase:
    """本地知识库主类"""
    
    def __init__(self, knowledge_dir: str = "knowledge_base"):
        self.knowledge_dir = knowledge_dir
        self.documents = []
        self.metadata = {}
        
        # 初始化搜索引擎
        if VECTOR_AVAILABLE:
            try:
                self.search_engine = VectorSearchEngine()
                self.search_type = "vector"
                logger.info("使用向量搜索引擎")
            except Exception as e:
                logger.warning(f"向量搜索初始化失败: {e}")
                self.search_engine = KeywordSearchEngine()
                self.search_type = "keyword"
        else:
            self.search_engine = KeywordSearchEngine()
            self.search_type = "keyword"
            logger.info("使用关键词搜索引擎")
        
        self.ensure_directories()
        self.load_knowledge_base()
    
    def ensure_directories(self):
        """确保必要的目录存在"""
        dirs = [
            self.knowledge_dir,
            f"{self.knowledge_dir}/documents",
            f"{self.knowledge_dir}/metadata",
            f"{self.knowledge_dir}/indices"
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
    
    def add_document(self, file_path: str, title: str = None, metadata: Dict = None) -> bool:
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
        content, file_type = DocumentProcessor.extract_text(file_path)
        if not content:
            logger.error(f"无法提取文件内容: {file_path}")
            return False
        
        # 分割文本
        chunks = TextSplitter.split_by_paragraphs(content, max_length=500, overlap=50)
        
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
                'chunk_index': i,
                'total_chunks': len(chunks),
                'created_at': datetime.now().isoformat(),
                'file_hash': file_hash
            }
            
            if metadata:
                doc.update(metadata)
            
            self.documents.append(doc)
        
        # 保存元数据
        self.metadata[file_hash] = {
            'file_path': file_path,
            'title': title,
            'file_type': file_type,
            'chunks_count': len(chunks),
            'added_at': datetime.now().isoformat()
        }
        
        logger.info(f"✅ 已添加文档: {title} ({len(chunks)}个片段)")
        return True
    
    def add_directory(self, dir_path: str, recursive: bool = True) -> int:
        """批量添加目录中的文档"""
        if not os.path.exists(dir_path):
            logger.error(f"目录不存在: {dir_path}")
            return 0
        
        added_count = 0
        supported_extensions = {'.pdf', '.docx', '.doc', '.txt', '.md', '.csv', '.py', '.js', '.html'}
        
        for root, dirs, files in os.walk(dir_path):
            for file in files:
                file_path = os.path.join(root, file)
                ext = os.path.splitext(file)[1].lower()
                
                if ext in supported_extensions:
                    if self.add_document(file_path):
                        added_count += 1
            
            if not recursive:
                break
        
        logger.info(f"✅ 批量添加完成，共添加 {added_count} 个文档")
        return added_count
    
    def build_index(self):
        """构建搜索索引"""
        if not self.documents:
            logger.warning("没有文档，无法构建索引")
            return
        
        self.search_engine.build_index(self.documents)
        self.save_index()
        logger.info("搜索索引构建完成")
    
    def search(self, query: str, top_k: int = 5, file_type: str = None) -> List[Dict]:
        """搜索知识库"""
        if not self.documents:
            return []
        
        # 如果指定了文件类型，先过滤
        documents = self.documents
        if file_type:
            documents = [doc for doc in self.documents if doc.get('file_type') == file_type]
            
            # 临时构建索引
            if documents:
                temp_engine = VectorSearchEngine() if self.search_type == "vector" else KeywordSearchEngine()
                temp_engine.build_index(documents)
                return temp_engine.search(query, top_k)
        
        return self.search_engine.search(query, top_k)
    
    def get_context_for_query(self, query: str, max_context_length: int = 1500) -> str:
        """为查询获取相关上下文"""
        results = self.search(query, top_k=3)
        
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
        
        if os.path.exists(docs_path):
            with open(docs_path, 'r', encoding='utf-8') as f:
                self.documents = json.load(f)
            logger.info(f"📚 已加载 {len(self.documents)} 个文档片段")
        
        if os.path.exists(meta_path):
            with open(meta_path, 'r', encoding='utf-8') as f:
                self.metadata = json.load(f)
            logger.info(f"📋 已加载 {len(self.metadata)} 个文件的元数据")
        
        # 加载索引
        self.load_index()
    
    def save_index(self):
        """保存搜索索引"""
        if self.search_type == "vector":
            index_path = f"{self.knowledge_dir}/indices/vector_index.pkl"
            self.search_engine.save_index(index_path)
    
    def load_index(self):
        """加载搜索索引"""
        if self.search_type == "vector":
            index_path = f"{self.knowledge_dir}/indices/vector_index.pkl"
            if self.search_engine.load_index(index_path):
                logger.info("向量索引已加载")
                return
        
        # 如果有文档但没有索引，重新构建
        if self.documents:
            self.search_engine.build_index(self.documents)
    
    def get_statistics(self) -> Dict:
        """获取知识库统计信息"""
        file_types = {}
        total_chunks = len(self.documents)
        total_files = len(self.metadata)
        
        for doc in self.documents:
            file_type = doc.get('file_type', 'unknown')
            file_types[file_type] = file_types.get(file_type, 0) + 1
        
        return {
            'total_files': total_files,
            'total_chunks': total_chunks,
            'file_types': file_types,
            'search_engine': self.search_type,
            'last_updated': datetime.now().isoformat()
        }
    
    def list_documents(self) -> List[Dict]:
        """列出所有文档"""
        return list(self.metadata.values())
    
    def remove_document(self, file_path: str) -> bool:
        """移除文档"""
        file_hash = self.get_file_hash(file_path)
        if file_hash not in self.metadata:
            logger.warning(f"文档不在知识库中: {file_path}")
            return False
        
        # 移除文档片段
        self.documents = [doc for doc in self.documents if doc['file_hash'] != file_hash]
        
        # 移除元数据
        del self.metadata[file_hash]
        
        # 重新构建索引
        if self.documents:
            self.search_engine.build_index(self.documents)
        
        logger.info(f"✅ 已移除文档: {file_path}")
        return True

# 测试函数
if __name__ == "__main__":
    # 创建知识库实例
    kb = LocalKnowledgeBase()
    
    # 示例用法
    print("🧠 本地知识库系统测试")
    print(f"搜索引擎: {kb.search_type}")
    print(f"当前文档数量: {len(kb.documents)}")
    
    # 获取统计信息
    stats = kb.get_statistics()
    print("📊 知识库统计:", json.dumps(stats, indent=2, ensure_ascii=False))
