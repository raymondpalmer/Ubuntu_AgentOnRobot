#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于LangChain的智能知识库系统
支持向量搜索和语义检索的高级知识库实现

主要功能:
- 文档向量化存储(使用ChromaDB)
- 语义相似度搜索
- 多格式文档处理(PDF、Word、TXT)
- 上下文增强检索
- 知识库管理和维护

作者: Dragon Robot AI System
创建时间: 2024
"""

import os
import logging
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import json
from datetime import datetime

# LangChain核心组件
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    TextLoader
)
from langchain_core.documents import Document

# 文档处理工具
import PyPDF2
import docx
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

class LangChainKnowledgeBase:
    """
    基于LangChain的高级知识库系统
    
    主要特性:
    - 使用HuggingFace中文预训练模型进行文本嵌入
    - ChromaDB作为向量数据库
    - 支持增量更新和批量导入
    - 语义相似度搜索
    - 文档元数据管理
    """
    
    def __init__(self, 
                 knowledge_base_dir: str = "knowledge_base",
                 model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
                 chunk_size: int = 500,
                 chunk_overlap: int = 50):
        """
        初始化LangChain知识库
        
        Args:
            knowledge_base_dir: 知识库存储目录
            model_name: 文本嵌入模型名称(支持中文)
            chunk_size: 文档分块大小
            chunk_overlap: 分块重叠大小
        """
        self.knowledge_base_dir = Path(knowledge_base_dir)
        self.knowledge_base_dir.mkdir(exist_ok=True)
        
        # 向量数据库目录
        self.vector_db_dir = self.knowledge_base_dir / "vector_db"
        self.vector_db_dir.mkdir(exist_ok=True)
        
        # 文档存储目录
        self.documents_dir = self.knowledge_base_dir / "documents"
        self.documents_dir.mkdir(exist_ok=True)
        
        # 元数据存储
        self.metadata_file = self.knowledge_base_dir / "metadata.json"
        
        # 文本分割器配置
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # 初始化嵌入模型
        logger.info(f"初始化嵌入模型: {model_name}")
        self.embeddings = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs={'device': 'cpu'},  # 如果有GPU可以改为'cuda'
            encode_kwargs={'normalize_embeddings': True}
        )
        
        # 初始化文本分割器
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", "。", "！", "？", ".", "!", "?", " "]
        )
        
        # 初始化向量数据库
        self.vector_store = self._initialize_vector_store()
        
        # 加载元数据
        self.metadata = self._load_metadata()
        
        logger.info("LangChain知识库初始化完成")
    
    def _initialize_vector_store(self) -> Chroma:
        """初始化ChromaDB向量数据库"""
        try:
            # 尝试加载现有的向量数据库
            vector_store = Chroma(
                persist_directory=str(self.vector_db_dir),
                embedding_function=self.embeddings,
                collection_name="dragon_knowledge_base"
            )
            logger.info("成功加载现有向量数据库")
            return vector_store
        except Exception as e:
            # 创建新的向量数据库
            logger.info(f"创建新的向量数据库: {e}")
            vector_store = Chroma(
                persist_directory=str(self.vector_db_dir),
                embedding_function=self.embeddings,
                collection_name="dragon_knowledge_base"
            )
            return vector_store
    
    def _load_metadata(self) -> Dict[str, Any]:
        """加载文档元数据"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"元数据加载失败: {e}")
                return {"documents": {}, "last_updated": None}
        else:
            return {"documents": {}, "last_updated": None}
    
    def _save_metadata(self):
        """保存文档元数据"""
        self.metadata["last_updated"] = datetime.now().isoformat()
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"元数据保存失败: {e}")
    
    def add_document(self, file_path: str, category: str = "general") -> bool:
        """
        添加文档到知识库
        
        Args:
            file_path: 文档文件路径
            category: 文档分类
        
        Returns:
            bool: 添加是否成功
        """
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                logger.error(f"文件不存在: {file_path}")
                return False
            
            # 检查文件类型
            file_ext = file_path.suffix.lower()
            supported_formats = ['.pdf', '.docx', '.txt', '.md']
            
            if file_ext not in supported_formats:
                logger.error(f"不支持的文件格式: {file_ext}")
                return False
            
            # 加载文档
            documents = self._load_document(file_path)
            if not documents:
                logger.error(f"文档加载失败: {file_path}")
                return False
            
            # 检查文档内容是否为空 (可能是扫描版PDF)
            total_content = ""
            for doc in documents:
                if doc.page_content:
                    total_content += doc.page_content.strip()
            
            if not total_content:
                logger.warning(f"文档内容为空，可能是扫描版PDF: {file_path.name}")
                # 对于扫描版PDF，我们可以选择跳过或尝试OCR
                # 目前先跳过，后续可以集成OCR功能
                return False
            
            # 为文档添加元数据
            for doc in documents:
                doc.metadata.update({
                    "source": str(file_path),
                    "category": category,
                    "filename": file_path.name,
                    "file_type": file_ext,
                    "added_time": datetime.now().isoformat()
                })
            
            # 分割文档
            chunks = self.text_splitter.split_documents(documents)
            logger.info(f"文档分割为 {len(chunks)} 个片段")
            
            # 检查是否有有效内容
            if len(chunks) == 0:
                logger.warning(f"文档内容为空，跳过添加: {file_path.name}")
                return False
            
            # 过滤空白内容的分块
            valid_chunks = []
            for chunk in chunks:
                if chunk.page_content and chunk.page_content.strip():
                    valid_chunks.append(chunk)
            
            if len(valid_chunks) == 0:
                logger.warning(f"文档只包含空白内容，跳过添加: {file_path.name}")
                return False
            
            logger.info(f"过滤后有效片段数: {len(valid_chunks)}")
            
            # 添加到向量数据库
            self.vector_store.add_documents(valid_chunks)
            
            # 持久化向量数据库
            self.vector_store.persist()
            
            # 更新元数据
            file_id = str(file_path)
            self.metadata["documents"][file_id] = {
                "filename": file_path.name,
                "category": category,
                "file_type": file_ext,
                "chunks_count": len(valid_chunks),
                "added_time": datetime.now().isoformat()
            }
            self._save_metadata()
            
            logger.info(f"成功添加文档: {file_path.name}")
            return True
            
        except Exception as e:
            logger.error(f"添加文档失败: {e}")
            return False
    
    def _load_document(self, file_path: Path) -> List[Document]:
        """
        根据文件类型加载文档
        
        Args:
            file_path: 文件路径
        
        Returns:
            List[Document]: 文档列表
        """
        try:
            file_ext = file_path.suffix.lower()
            
            if file_ext == '.pdf':
                # 先尝试常规PDF加载
                loader = PyPDFLoader(str(file_path))
                docs = loader.load()
                
                # 检查是否有有效内容
                has_content = any(doc.page_content.strip() for doc in docs)
                
                if not has_content:
                    # 尝试OCR加载
                    logger.info(f"文档内容为空，尝试OCR: {file_path.name}")
                    try:
                        from ocr_enhanced_loader import OCREnhancedLoader
                        ocr_loader = OCREnhancedLoader()
                        ocr_docs = ocr_loader.load_document_with_ocr(file_path)
                        if ocr_docs:
                            logger.info(f"OCR成功提取文档: {file_path.name}")
                            return ocr_docs
                        else:
                            logger.warning(f"文档内容为空，可能是扫描版PDF: {file_path.name}")
                            return []
                    except Exception as e:
                        logger.warning(f"OCR处理失败: {e}")
                        return []
                
                return docs
            
            elif file_ext == '.docx':
                loader = Docx2txtLoader(str(file_path))
                return loader.load()
            
            elif file_ext in ['.txt', '.md']:
                loader = TextLoader(str(file_path), encoding='utf-8')
                return loader.load()
            
            else:
                logger.error(f"不支持的文件格式: {file_ext}")
                return []
                
        except Exception as e:
            logger.error(f"文档加载错误: {e}")
            return []
    
    def search(self, query: str, top_k: int = 5, score_threshold: float = 0.0) -> List[Dict[str, Any]]:
        """
        语义搜索知识库
        
        Args:
            query: 搜索查询
            top_k: 返回结果数量
            score_threshold: 相似度阈值
        
        Returns:
            List[Dict]: 搜索结果列表
        """
        try:
            if not query.strip():
                return []
            
            # 执行相似度搜索
            results = self.vector_store.similarity_search_with_score(
                query=query,
                k=top_k
            )
            
            # 格式化结果
            formatted_results = []
            for doc, score in results:
                if score >= score_threshold:
                    result = {
                        "content": doc.page_content,
                        "metadata": doc.metadata,
                        "similarity_score": float(score),
                        "source": doc.metadata.get("source", "未知"),
                        "category": doc.metadata.get("category", "general"),
                        "filename": doc.metadata.get("filename", "未知文件")
                    }
                    formatted_results.append(result)
            
            logger.info(f"搜索查询: '{query}' - 找到 {len(formatted_results)} 个相关结果")
            return formatted_results
            
        except Exception as e:
            logger.error(f"搜索失败: {e}")
            return []
    
    def get_relevant_context(self, query: str, max_context_length: int = 2000) -> str:
        """
        获取查询相关的上下文信息
        
        Args:
            query: 查询文本
            max_context_length: 最大上下文长度
        
        Returns:
            str: 相关上下文
        """
        try:
            results = self.search(query, top_k=3)
            
            if not results:
                return "抱歉，在知识库中没有找到相关信息。"
            
            context_parts = []
            current_length = 0
            
            for result in results:
                content = result["content"]
                source = result["filename"]
                
                # 添加来源标识
                formatted_content = f"[来源: {source}]\n{content}\n"
                
                if current_length + len(formatted_content) <= max_context_length:
                    context_parts.append(formatted_content)
                    current_length += len(formatted_content)
                else:
                    # 截断内容以适应长度限制
                    remaining_length = max_context_length - current_length
                    if remaining_length > 100:  # 至少保留100字符
                        truncated_content = content[:remaining_length-50] + "..."
                        formatted_content = f"[来源: {source}]\n{truncated_content}\n"
                        context_parts.append(formatted_content)
                    break
            
            context = "\n".join(context_parts)
            return context if context else "知识库中的相关信息较少，无法提供详细回答。"
            
        except Exception as e:
            logger.error(f"获取上下文失败: {e}")
            return "获取知识库信息时出现错误。"
    
    def list_documents(self) -> List[Dict[str, Any]]:
        """列出知识库中的所有文档"""
        docs = []
        for file_id, info in self.metadata["documents"].items():
            docs.append({
                "path": file_id,
                "filename": info["filename"],
                "category": info["category"],
                "file_type": info["file_type"],
                "chunks_count": info["chunks_count"],
                "added_time": info["added_time"]
            })
        return docs
    
    def remove_document(self, file_path: str) -> bool:
        """
        从知识库中移除文档
        
        Args:
            file_path: 文档路径
        
        Returns:
            bool: 是否成功移除
        """
        try:
            file_id = str(file_path)
            
            if file_id not in self.metadata["documents"]:
                logger.warning(f"文档不存在于知识库中: {file_path}")
                return False
            
            # 从向量数据库中删除相关文档
            # 注意: ChromaDB的删除操作比较复杂，这里使用过滤方式
            # 实际应用中可能需要重建向量数据库
            
            # 从元数据中移除
            del self.metadata["documents"][file_id]
            self._save_metadata()
            
            logger.info(f"成功移除文档: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"移除文档失败: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """获取知识库统计信息"""
        try:
            total_docs = len(self.metadata["documents"])
            total_chunks = sum(doc["chunks_count"] for doc in self.metadata["documents"].values())
            
            categories = {}
            for doc in self.metadata["documents"].values():
                category = doc["category"]
                categories[category] = categories.get(category, 0) + 1
            
            return {
                "total_documents": total_docs,
                "total_chunks": total_chunks,
                "categories": categories,
                "last_updated": self.metadata.get("last_updated"),
                "vector_db_path": str(self.vector_db_dir),
                "model_name": "paraphrase-multilingual-MiniLM-L12-v2"
            }
            
        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            return {}
    
    def rebuild_index(self) -> bool:
        """重建向量索引"""
        try:
            logger.info("开始重建向量索引...")
            
            # 备份当前元数据
            docs_to_rebuild = list(self.metadata["documents"].keys())
            
            # 清空向量数据库
            self.vector_store = Chroma(
                persist_directory=str(self.vector_db_dir),
                embedding_function=self.embeddings,
                collection_name="dragon_knowledge_base"
            )
            
            # 重新添加所有文档
            success_count = 0
            for file_path in docs_to_rebuild:
                if Path(file_path).exists():
                    doc_info = self.metadata["documents"][file_path]
                    if self.add_document(file_path, doc_info["category"]):
                        success_count += 1
                else:
                    logger.warning(f"文件不存在，跳过: {file_path}")
            
            logger.info(f"索引重建完成，成功重建 {success_count} 个文档")
            return True
            
        except Exception as e:
            logger.error(f"索引重建失败: {e}")
            return False


# 便捷函数
def create_knowledge_base(kb_dir: str = "knowledge_base") -> LangChainKnowledgeBase:
    """创建知识库实例"""
    return LangChainKnowledgeBase(knowledge_base_dir=kb_dir)


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(level=logging.INFO)
    
    # 创建知识库实例
    kb = create_knowledge_base("test_knowledge_base")
    
    # 打印统计信息
    stats = kb.get_stats()
    print("知识库统计信息:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # 测试搜索
    results = kb.search("测试查询")
    print(f"\n搜索结果数量: {len(results)}")