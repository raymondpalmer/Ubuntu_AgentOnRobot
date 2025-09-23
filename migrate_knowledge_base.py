#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识库数据迁移脚本
从SimpleKnowledgeBase迁移到LangChain知识库

功能:
- 自动检测现有简化版知识库
- 迁移文档和元数据到LangChain系统
- 保持分类信息和文件结构
- 生成迁移报告

作者: Dragon Robot AI System
创建时间: 2024
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Tuple
import shutil
from datetime import datetime

# 导入知识库系统
from simple_knowledge_base import SimpleKnowledgeBase
from langchain_knowledge_base import LangChainKnowledgeBase

logger = logging.getLogger(__name__)

class KnowledgeBaseMigrator:
    """知识库迁移工具"""
    
    def __init__(self, 
                 simple_kb_dir: str = "knowledge_base",
                 langchain_kb_dir: str = "langchain_knowledge_base"):
        """
        初始化迁移工具
        
        Args:
            simple_kb_dir: 简化版知识库目录
            langchain_kb_dir: LangChain知识库目录
        """
        self.simple_kb_dir = Path(simple_kb_dir)
        self.langchain_kb_dir = Path(langchain_kb_dir)
        
        # 迁移日志
        self.migration_log = {
            "migration_date": datetime.now().isoformat(),
            "source_dir": str(self.simple_kb_dir),
            "target_dir": str(self.langchain_kb_dir),
            "migrated_documents": [],
            "failed_documents": [],
            "statistics": {}
        }
        
        logger.info(f"迁移工具初始化: {self.simple_kb_dir} -> {self.langchain_kb_dir}")
    
    def check_source_kb(self) -> Tuple[bool, Dict[str, Any]]:
        """
        检查源知识库状态
        
        Returns:
            Tuple[bool, Dict]: (是否存在, 统计信息)
        """
        try:
            if not self.simple_kb_dir.exists():
                logger.warning(f"源知识库目录不存在: {self.simple_kb_dir}")
                return False, {}
            
            # 初始化简化版知识库
            simple_kb = SimpleKnowledgeBase(str(self.simple_kb_dir))
            
            # 获取统计信息
            stats = {
                "documents_dir": str(self.simple_kb_dir / "documents"),
                "document_count": 0,
                "total_size": 0,
                "file_types": {},
                "categories": {}
            }
            
            documents_dir = self.simple_kb_dir / "documents"
            if documents_dir.exists():
                for file_path in documents_dir.rglob("*"):
                    if file_path.is_file():
                        stats["document_count"] += 1
                        stats["total_size"] += file_path.stat().st_size
                        
                        # 统计文件类型
                        file_ext = file_path.suffix.lower()
                        stats["file_types"][file_ext] = stats["file_types"].get(file_ext, 0) + 1
            
            # 检查元数据文件
            metadata_file = self.simple_kb_dir / "metadata.json"
            if metadata_file.exists():
                try:
                    with open(metadata_file, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                    
                    # 统计分类信息
                    for doc_info in metadata.get("documents", {}).values():
                        category = doc_info.get("category", "unknown")
                        stats["categories"][category] = stats["categories"].get(category, 0) + 1
                        
                except Exception as e:
                    logger.warning(f"读取元数据失败: {e}")
            
            logger.info(f"源知识库检查完成: {stats}")
            return True, stats
            
        except Exception as e:
            logger.error(f"检查源知识库失败: {e}")
            return False, {}
    
    def migrate_documents(self) -> bool:
        """
        迁移文档到LangChain知识库
        
        Returns:
            bool: 迁移是否成功
        """
        try:
            # 检查源知识库
            exists, source_stats = self.check_source_kb()
            if not exists:
                logger.error("源知识库不存在或无法访问")
                return False
            
            # 创建LangChain知识库
            logger.info("初始化LangChain知识库...")
            langchain_kb = LangChainKnowledgeBase(str(self.langchain_kb_dir))
            
            # 获取源文档列表
            documents_dir = self.simple_kb_dir / "documents"
            if not documents_dir.exists():
                logger.warning("源知识库没有documents目录")
                return True  # 空迁移也算成功
            
            # 加载源元数据
            source_metadata = self._load_source_metadata()
            
            # 迁移每个文档
            success_count = 0
            total_count = 0
            
            for file_path in documents_dir.rglob("*"):
                if file_path.is_file():
                    total_count += 1
                    
                    # 确定文档分类
                    category = self._get_document_category(file_path, source_metadata)
                    
                    # 迁移文档
                    if self._migrate_single_document(langchain_kb, file_path, category):
                        success_count += 1
                        self.migration_log["migrated_documents"].append({
                            "file": str(file_path),
                            "category": category,
                            "migrated_at": datetime.now().isoformat()
                        })
                    else:
                        self.migration_log["failed_documents"].append({
                            "file": str(file_path),
                            "category": category,
                            "error": "迁移失败"
                        })
            
            # 更新迁移统计
            self.migration_log["statistics"] = {
                "total_documents": total_count,
                "successful_migrations": success_count,
                "failed_migrations": total_count - success_count,
                "source_stats": source_stats,
                "target_stats": langchain_kb.get_stats()
            }
            
            # 保存迁移日志
            self._save_migration_log()
            
            logger.info(f"迁移完成: {success_count}/{total_count} 个文档成功迁移")
            return success_count > 0
            
        except Exception as e:
            logger.error(f"文档迁移失败: {e}")
            return False
    
    def _load_source_metadata(self) -> Dict[str, Any]:
        """加载源知识库元数据"""
        metadata_file = self.simple_kb_dir / "metadata.json"
        if metadata_file.exists():
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"加载源元数据失败: {e}")
        return {"documents": {}}
    
    def _get_document_category(self, file_path: Path, source_metadata: Dict[str, Any]) -> str:
        """获取文档分类"""
        # 从源元数据中查找分类
        for doc_path, doc_info in source_metadata.get("documents", {}).items():
            if Path(doc_path).name == file_path.name:
                return doc_info.get("category", "general")
        
        # 根据文件名或路径推断分类
        file_name = file_path.name.lower()
        if "robot" in file_name or "机器人" in file_name:
            return "robot"
        elif "voice" in file_name or "语音" in file_name:
            return "voice"
        elif "manual" in file_name or "说明" in file_name:
            return "manual"
        else:
            return "general"
    
    def _migrate_single_document(self, langchain_kb: LangChainKnowledgeBase, 
                                file_path: Path, category: str) -> bool:
        """
        迁移单个文档
        
        Args:
            langchain_kb: LangChain知识库实例
            file_path: 文档路径
            category: 文档分类
        
        Returns:
            bool: 是否成功
        """
        try:
            logger.info(f"迁移文档: {file_path.name}")
            
            # 复制文档到新的知识库目录
            target_doc_path = langchain_kb.documents_dir / file_path.name
            shutil.copy2(file_path, target_doc_path)
            
            # 添加到LangChain知识库
            success = langchain_kb.add_document(str(target_doc_path), category)
            
            if not success:
                # 如果添加失败，删除复制的文件
                if target_doc_path.exists():
                    target_doc_path.unlink()
                logger.error(f"文档添加到知识库失败: {file_path.name}")
                return False
            
            logger.info(f"文档迁移成功: {file_path.name}")
            return True
            
        except Exception as e:
            logger.error(f"迁移单个文档失败 {file_path.name}: {e}")
            return False
    
    def _save_migration_log(self):
        """保存迁移日志"""
        try:
            log_file = self.langchain_kb_dir / "migration_log.json"
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(self.migration_log, f, ensure_ascii=False, indent=2)
            logger.info(f"迁移日志已保存: {log_file}")
        except Exception as e:
            logger.error(f"保存迁移日志失败: {e}")
    
    def create_backup(self) -> bool:
        """
        创建源知识库备份
        
        Returns:
            bool: 备份是否成功
        """
        try:
            if not self.simple_kb_dir.exists():
                logger.warning("源知识库不存在，无需备份")
                return True
            
            backup_dir = self.simple_kb_dir.parent / f"{self.simple_kb_dir.name}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            logger.info(f"创建备份: {self.simple_kb_dir} -> {backup_dir}")
            shutil.copytree(self.simple_kb_dir, backup_dir)
            
            logger.info(f"备份创建成功: {backup_dir}")
            return True
            
        except Exception as e:
            logger.error(f"创建备份失败: {e}")
            return False
    
    def generate_migration_report(self) -> str:
        """
        生成迁移报告
        
        Returns:
            str: 报告文本
        """
        report = f"""
=== Dragon Robot 知识库迁移报告 ===

迁移时间: {self.migration_log['migration_date']}
源目录: {self.migration_log['source_dir']}
目标目录: {self.migration_log['target_dir']}

=== 迁移统计 ===
总文档数: {self.migration_log['statistics'].get('total_documents', 0)}
成功迁移: {self.migration_log['statistics'].get('successful_migrations', 0)}
失败数量: {self.migration_log['statistics'].get('failed_migrations', 0)}

=== 成功迁移的文档 ===
"""
        for doc in self.migration_log['migrated_documents']:
            report += f"- {Path(doc['file']).name} (分类: {doc['category']})\n"
        
        if self.migration_log['failed_documents']:
            report += "\n=== 迁移失败的文档 ===\n"
            for doc in self.migration_log['failed_documents']:
                report += f"- {Path(doc['file']).name} (错误: {doc['error']})\n"
        
        # 添加统计对比
        source_stats = self.migration_log['statistics'].get('source_stats', {})
        target_stats = self.migration_log['statistics'].get('target_stats', {})
        
        report += f"""
=== 知识库对比 ===
源知识库文档数: {source_stats.get('document_count', 0)}
目标知识库文档数: {target_stats.get('total_documents', 0)}
目标知识库分块数: {target_stats.get('total_chunks', 0)}

=== 迁移完成 ===
LangChain知识库已就绪，支持语义搜索和向量检索。
"""
        return report


def main():
    """主函数 - 执行迁移"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("=== Dragon Robot 知识库迁移工具 ===")
    print("将简化版知识库迁移到LangChain系统")
    
    # 创建迁移器
    migrator = KnowledgeBaseMigrator()
    
    # 检查源知识库
    print("\n1. 检查源知识库...")
    exists, stats = migrator.check_source_kb()
    
    if not exists:
        print("❌ 源知识库不存在或为空，无需迁移")
        return
    
    print(f"✅ 源知识库检查完成:")
    print(f"   - 文档数量: {stats.get('document_count', 0)}")
    print(f"   - 文件类型: {list(stats.get('file_types', {}).keys())}")
    print(f"   - 分类数量: {len(stats.get('categories', {}))}")
    
    # 询问是否创建备份
    backup_choice = input("\n2. 是否创建源知识库备份? (y/N): ").lower().strip()
    if backup_choice == 'y':
        print("创建备份中...")
        if migrator.create_backup():
            print("✅ 备份创建成功")
        else:
            print("❌ 备份创建失败")
            return
    
    # 执行迁移
    print("\n3. 开始迁移文档...")
    if migrator.migrate_documents():
        print("✅ 文档迁移完成")
        
        # 生成报告
        print("\n4. 生成迁移报告...")
        report = migrator.generate_migration_report()
        print(report)
        
        # 保存报告到文件
        report_file = Path("migration_report.txt")
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"📝 完整报告已保存到: {report_file}")
        
    else:
        print("❌ 文档迁移失败")
        return
    
    print("\n=== 迁移完成 ===")
    print("LangChain知识库已就绪，现在可以享受语义搜索功能！")


if __name__ == "__main__":
    main()