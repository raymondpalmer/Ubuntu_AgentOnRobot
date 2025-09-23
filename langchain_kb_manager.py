#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LangChain知识库管理工具
支持简化版和LangChain两种知识库后端

功能:
- 统一的知识库管理接口
- 自动检测知识库类型
- 文档添加、删除、搜索操作
- 知识库统计和维护
- 批量操作支持

作者: Dragon Robot AI System
创建时间: 2024
"""

import os
import sys
import argparse
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import json
from datetime import datetime

# 添加当前目录到路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# 导入知识库模块
try:
    from simple_knowledge_base import SimpleKnowledgeBase
    SIMPLE_KB_AVAILABLE = True
except ImportError:
    print("Warning: SimpleKnowledgeBase not available")
    SIMPLE_KB_AVAILABLE = False

try:
    from langchain_knowledge_base import LangChainKnowledgeBase
    LANGCHAIN_KB_AVAILABLE = True
except ImportError:
    print("Warning: LangChainKnowledgeBase not available")
    LANGCHAIN_KB_AVAILABLE = False

# 迁移工具
try:
    from migrate_knowledge_base import KnowledgeBaseMigrator
    MIGRATION_AVAILABLE = True
except ImportError:
    print("Warning: Migration tool not available")
    MIGRATION_AVAILABLE = False

logger = logging.getLogger(__name__)

class UnifiedKnowledgeBaseManager:
    """统一知识库管理器"""
    
    def __init__(self, kb_dir: str = "knowledge_base", backend: str = "auto"):
        """
        初始化知识库管理器
        
        Args:
            kb_dir: 知识库目录
            backend: 后端类型 ("simple", "langchain", "auto")
        """
        self.kb_dir = Path(kb_dir)
        self.backend = backend
        self.kb_instance = None
        
        # 自动检测或初始化知识库
        self._initialize_knowledge_base()
    
    def _initialize_knowledge_base(self):
        """初始化知识库实例"""
        if self.backend == "auto":
            self.backend = self._detect_kb_type()
        
        if self.backend == "langchain" and LANGCHAIN_KB_AVAILABLE:
            try:
                self.kb_instance = LangChainKnowledgeBase(str(self.kb_dir))
                logger.info("使用LangChain知识库")
            except Exception as e:
                logger.error(f"LangChain知识库初始化失败: {e}")
                self._fallback_to_simple()
        
        elif self.backend == "simple" and SIMPLE_KB_AVAILABLE:
            try:
                self.kb_instance = SimpleKnowledgeBase(str(self.kb_dir))
                logger.info("使用简化版知识库")
            except Exception as e:
                logger.error(f"简化版知识库初始化失败: {e}")
                self.kb_instance = None
        
        else:
            logger.error(f"不支持的知识库后端: {self.backend}")
            self.kb_instance = None
    
    def _detect_kb_type(self) -> str:
        """自动检测知识库类型"""
        if not self.kb_dir.exists():
            # 新知识库，优先使用LangChain
            return "langchain" if LANGCHAIN_KB_AVAILABLE else "simple"
        
        # 检查LangChain特有文件
        vector_db_dir = self.kb_dir / "vector_db"
        if vector_db_dir.exists():
            return "langchain"
        
        # 检查简化版特有文件
        simple_index = self.kb_dir / "index.json"
        if simple_index.exists():
            return "simple"
        
        # 默认选择
        return "langchain" if LANGCHAIN_KB_AVAILABLE else "simple"
    
    def _fallback_to_simple(self):
        """回退到简化版知识库"""
        if SIMPLE_KB_AVAILABLE:
            try:
                self.backend = "simple"
                self.kb_instance = SimpleKnowledgeBase(str(self.kb_dir))
                logger.info("已回退到简化版知识库")
            except Exception as e:
                logger.error(f"回退到简化版知识库也失败: {e}")
                self.kb_instance = None
    
    def add_document(self, file_path: str, category: str = "general") -> bool:
        """添加文档"""
        if not self.kb_instance:
            logger.error("知识库未初始化")
            return False
        
        try:
            return self.kb_instance.add_document(file_path, category)
        except Exception as e:
            logger.error(f"添加文档失败: {e}")
            return False
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """搜索知识库"""
        if not self.kb_instance:
            logger.error("知识库未初始化")
            return []
        
        try:
            if hasattr(self.kb_instance, 'search'):
                return self.kb_instance.search(query, top_k)
            else:
                # 简化版知识库使用不同的方法名
                results = self.kb_instance.search_documents(query)
                return results[:top_k] if results else []
        except Exception as e:
            logger.error(f"搜索失败: {e}")
            return []
    
    def get_context(self, query: str, max_length: int = 2000) -> str:
        """获取相关上下文"""
        if not self.kb_instance:
            return "知识库未初始化"
        
        try:
            if hasattr(self.kb_instance, 'get_relevant_context'):
                return self.kb_instance.get_relevant_context(query, max_length)
            else:
                # 简化版知识库的替代方法
                results = self.search(query, 3)
                if not results:
                    return "未找到相关信息"
                
                context_parts = []
                current_length = 0
                
                for result in results:
                    content = result.get("content", "")
                    if current_length + len(content) <= max_length:
                        context_parts.append(content)
                        current_length += len(content)
                    else:
                        break
                
                return "\n\n".join(context_parts) if context_parts else "未找到相关信息"
        except Exception as e:
            logger.error(f"获取上下文失败: {e}")
            return "获取信息时出现错误"
    
    def list_documents(self) -> List[Dict[str, Any]]:
        """列出所有文档"""
        if not self.kb_instance:
            return []
        
        try:
            return self.kb_instance.list_documents()
        except Exception as e:
            logger.error(f"列出文档失败: {e}")
            return []
    
    def remove_document(self, file_path: str) -> bool:
        """删除文档"""
        if not self.kb_instance:
            logger.error("知识库未初始化")
            return False
        
        try:
            return self.kb_instance.remove_document(file_path)
        except Exception as e:
            logger.error(f"删除文档失败: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        if not self.kb_instance:
            return {"error": "知识库未初始化"}
        
        try:
            stats = self.kb_instance.get_stats()
            stats["backend_type"] = self.backend
            stats["backend_available"] = {
                "simple": SIMPLE_KB_AVAILABLE,
                "langchain": LANGCHAIN_KB_AVAILABLE
            }
            return stats
        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            return {"error": str(e)}
    
    def migrate_to_langchain(self) -> bool:
        """迁移到LangChain知识库"""
        if not MIGRATION_AVAILABLE:
            logger.error("迁移工具不可用")
            return False
        
        if self.backend == "langchain":
            logger.info("已经是LangChain知识库")
            return True
        
        try:
            migrator = KnowledgeBaseMigrator(
                simple_kb_dir=str(self.kb_dir),
                langchain_kb_dir=str(self.kb_dir) + "_langchain"
            )
            
            if migrator.migrate_documents():
                # 迁移成功，切换到新的知识库
                self.kb_dir = Path(str(self.kb_dir) + "_langchain")
                self.backend = "langchain"
                self._initialize_knowledge_base()
                logger.info("成功迁移到LangChain知识库")
                return True
            else:
                logger.error("迁移失败")
                return False
                
        except Exception as e:
            logger.error(f"迁移过程出错: {e}")
            return False


def main():
    """命令行主函数"""
    parser = argparse.ArgumentParser(description="Dragon Robot 知识库管理工具")
    parser.add_argument("--kb-dir", default="knowledge_base", help="知识库目录")
    parser.add_argument("--backend", choices=["simple", "langchain", "auto"], 
                       default="auto", help="知识库后端类型")
    parser.add_argument("--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR"], 
                       default="INFO", help="日志级别")
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # 添加文档命令
    add_parser = subparsers.add_parser("add", help="添加文档")
    add_parser.add_argument("file_path", help="文档文件路径")
    add_parser.add_argument("--category", default="general", help="文档分类")
    
    # 搜索命令
    search_parser = subparsers.add_parser("search", help="搜索文档")
    search_parser.add_argument("query", help="搜索查询")
    search_parser.add_argument("--top-k", type=int, default=5, help="返回结果数量")
    
    # 上下文命令
    context_parser = subparsers.add_parser("context", help="获取相关上下文")
    context_parser.add_argument("query", help="查询文本")
    context_parser.add_argument("--max-length", type=int, default=2000, help="最大长度")
    
    # 列表命令
    list_parser = subparsers.add_parser("list", help="列出所有文档")
    
    # 删除命令
    remove_parser = subparsers.add_parser("remove", help="删除文档")
    remove_parser.add_argument("file_path", help="要删除的文档路径")
    
    # 统计命令
    stats_parser = subparsers.add_parser("stats", help="显示统计信息")
    
    # 迁移命令
    migrate_parser = subparsers.add_parser("migrate", help="迁移到LangChain")
    
    args = parser.parse_args()
    
    # 设置日志
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 创建管理器
    manager = UnifiedKnowledgeBaseManager(args.kb_dir, args.backend)
    
    if not args.command:
        print("使用 --help 查看可用命令")
        return
    
    # 执行命令
    if args.command == "add":
        if manager.add_document(args.file_path, args.category):
            print(f"✅ 成功添加文档: {args.file_path}")
        else:
            print(f"❌ 添加文档失败: {args.file_path}")
    
    elif args.command == "search":
        results = manager.search(args.query, args.top_k)
        print(f"搜索查询: '{args.query}'")
        print(f"找到 {len(results)} 个结果:")
        
        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result.get('filename', '未知文件')}")
            print(f"   分类: {result.get('category', '未知')}")
            if 'similarity_score' in result:
                print(f"   相似度: {result['similarity_score']:.3f}")
            content = result.get('content', '')
            print(f"   内容预览: {content[:200]}...")
    
    elif args.command == "context":
        context = manager.get_context(args.query, args.max_length)
        print(f"查询: '{args.query}'")
        print(f"相关上下文:\n{context}")
    
    elif args.command == "list":
        docs = manager.list_documents()
        print(f"知识库中共有 {len(docs)} 个文档:")
        
        for doc in docs:
            print(f"- {doc.get('filename', '未知文件')} (分类: {doc.get('category', '未知')})")
    
    elif args.command == "remove":
        if manager.remove_document(args.file_path):
            print(f"✅ 成功删除文档: {args.file_path}")
        else:
            print(f"❌ 删除文档失败: {args.file_path}")
    
    elif args.command == "stats":
        stats = manager.get_stats()
        print("=== 知识库统计信息 ===")
        for key, value in stats.items():
            if isinstance(value, dict):
                print(f"{key}:")
                for sub_key, sub_value in value.items():
                    print(f"  {sub_key}: {sub_value}")
            else:
                print(f"{key}: {value}")
    
    elif args.command == "migrate":
        print("开始迁移到LangChain知识库...")
        if manager.migrate_to_langchain():
            print("✅ 迁移成功")
        else:
            print("❌ 迁移失败")


if __name__ == "__main__":
    main()