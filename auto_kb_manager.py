#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动知识库管理器
监控指定文件夹，自动添加新文档到LangChain知识库

功能:
- 启动时自动扫描文件夹
- 检测新增、修改、删除的文件
- 自动分类和添加到知识库
- 支持多种文件格式
- 智能去重和更新

作者: Dragon Robot AI System
创建时间: 2024
"""

import os
import json
import logging
import hashlib
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple
from datetime import datetime
import time

# 导入知识库管理器
try:
    from langchain_kb_manager import UnifiedKnowledgeBaseManager
    KB_AVAILABLE = True
except ImportError:
    KB_AVAILABLE = False
    print("⚠️ 知识库管理器未找到")

logger = logging.getLogger(__name__)

class AutoKnowledgeBaseManager:
    """自动知识库管理器"""
    
    def __init__(self, 
                 watch_dirs: List[str] = None,
                 kb_dir: str = "knowledge_base",
                 metadata_file: str = "auto_kb_metadata.json"):
        """
        初始化自动管理器
        
        Args:
            watch_dirs: 监控的文件夹列表
            kb_dir: 知识库目录
            metadata_file: 元数据文件
        """
        # 默认监控目录
        if watch_dirs is None:
            watch_dirs = ["knowledge_base/files"]
        
        self.watch_dirs = [Path(d) for d in watch_dirs]
        self.kb_dir = kb_dir
        self.metadata_file = Path(metadata_file)
        
        # 支持的文件格式
        self.supported_formats = {'.pdf', '.docx', '.doc', '.txt', '.md', '.markdown'}
        
        # 文件元数据
        self.file_metadata = self._load_metadata()
        
        # 初始化知识库管理器
        if KB_AVAILABLE:
            self.kb_manager = UnifiedKnowledgeBaseManager(kb_dir=kb_dir)
            logger.info("✅ 知识库管理器初始化成功")
        else:
            self.kb_manager = None
            logger.error("❌ 知识库管理器初始化失败")
        
        # 分类规则
        self.category_rules = {
            'manual': ['手册', '说明书', 'manual', 'guide', '指南'],
            'policy': ['制度', '规章', '政策', 'policy', '管理'],
            'tech': ['技术', '开发', 'api', 'tech', '配置', 'config'],
            'faq': ['问答', 'faq', '常见问题', 'help', '帮助'],
            'robot': ['机器人', 'robot', '控制', 'control'],
            'official': ['官方', 'official', 'readme', 'example']
        }
        
        logger.info(f"自动知识库管理器初始化完成，监控目录: {[str(d) for d in self.watch_dirs]}")
    
    def _load_metadata(self) -> Dict[str, Dict]:
        """加载文件元数据"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"元数据加载失败: {e}")
        
        return {
            "last_scan": None,
            "files": {},
            "scan_count": 0
        }
    
    def _save_metadata(self):
        """保存文件元数据"""
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.file_metadata, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"元数据保存失败: {e}")
    
    def _get_file_hash(self, file_path: Path) -> str:
        """计算文件MD5哈希值"""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            logger.warning(f"计算文件哈希失败 {file_path}: {e}")
            return ""
    
    def _detect_category(self, file_path: Path) -> str:
        """智能检测文件分类"""
        file_name = file_path.name.lower()
        file_content = ""
        
        # 尝试读取文件内容片段进行分类
        try:
            if file_path.suffix.lower() == '.txt':
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    file_content = f.read(500).lower()  # 只读前500字符
        except:
            pass
        
        # 根据文件名和内容检测分类
        search_text = f"{file_name} {file_content}"
        
        for category, keywords in self.category_rules.items():
            if any(keyword in search_text for keyword in keywords):
                return category
        
        # 根据文件夹名称推断
        parent_name = file_path.parent.name.lower()
        for category, keywords in self.category_rules.items():
            if any(keyword in parent_name for keyword in keywords):
                return category
        
        return "general"
    
    def scan_directories(self) -> Tuple[List[Path], List[Path], List[str]]:
        """
        扫描监控目录，检测文件变化
        
        Returns:
            Tuple[新文件列表, 修改文件列表, 删除文件列表]
        """
        current_files = {}
        new_files = []
        modified_files = []
        
        # 扫描所有监控目录
        for watch_dir in self.watch_dirs:
            if not watch_dir.exists():
                logger.warning(f"监控目录不存在: {watch_dir}")
                continue
            
            logger.info(f"扫描目录: {watch_dir}")
            
            for file_path in watch_dir.rglob("*"):
                if (file_path.is_file() and 
                    file_path.suffix.lower() in self.supported_formats):
                    
                    file_key = str(file_path)
                    current_files[file_key] = file_path
                    
                    # 计算文件信息
                    file_stat = file_path.stat()
                    file_size = file_stat.st_size
                    file_hash = self._get_file_hash(file_path)
                    
                    # 检查是否为新文件或修改的文件
                    if file_key not in self.file_metadata["files"]:
                        # 新文件
                        new_files.append(file_path)
                        logger.info(f"发现新文件: {file_path.name}")
                    else:
                        # 检查是否修改
                        old_info = self.file_metadata["files"][file_key]
                        if (old_info.get("hash") != file_hash or 
                            old_info.get("size") != file_size):
                            modified_files.append(file_path)
                            logger.info(f"文件已修改: {file_path.name}")
                    
                    # 更新元数据
                    self.file_metadata["files"][file_key] = {
                        "size": file_size,
                        "hash": file_hash,
                        "last_modified": file_stat.st_mtime,
                        "last_checked": time.time(),
                        "category": self._detect_category(file_path)
                    }
        
        # 检测删除的文件
        deleted_files = []
        for file_key in list(self.file_metadata["files"].keys()):
            if file_key not in current_files:
                deleted_files.append(file_key)
                del self.file_metadata["files"][file_key]
                logger.info(f"文件已删除: {Path(file_key).name}")
        
        # 更新扫描统计
        self.file_metadata["last_scan"] = datetime.now().isoformat()
        self.file_metadata["scan_count"] = self.file_metadata.get("scan_count", 0) + 1
        
        return new_files, modified_files, deleted_files
    
    def add_file_to_kb(self, file_path: Path) -> bool:
        """添加文件到知识库"""
        if not self.kb_manager:
            logger.error("知识库管理器未初始化")
            return False
        
        try:
            category = self._detect_category(file_path)
            success = self.kb_manager.add_document(str(file_path), category)
            
            if success:
                logger.info(f"✅ 成功添加到知识库: {file_path.name} (分类: {category})")
                
                # 更新元数据
                file_key = str(file_path)
                if file_key in self.file_metadata["files"]:
                    self.file_metadata["files"][file_key]["in_kb"] = True
                    self.file_metadata["files"][file_key]["added_time"] = time.time()
                    self.file_metadata["files"][file_key]["status"] = "success"
                
                return True
            else:
                logger.warning(f"⚠️ 跳过文档（可能是扫描版或空内容）: {file_path.name}")
                
                # 记录跳过状态
                file_key = str(file_path)
                if file_key in self.file_metadata["files"]:
                    self.file_metadata["files"][file_key]["in_kb"] = False
                    self.file_metadata["files"][file_key]["status"] = "skipped_empty_content"
                    self.file_metadata["files"][file_key]["skip_reason"] = "Empty content or scanned PDF"
                
                return False
                
        except Exception as e:
            logger.error(f"添加文件到知识库时出错 {file_path.name}: {e}")
            return False
    
    def auto_update_knowledge_base(self) -> Dict[str, int]:
        """自动更新知识库"""
        logger.info("🔄 开始自动更新知识库...")
        
        # 扫描文件变化
        new_files, modified_files, deleted_files = self.scan_directories()
        
        stats = {
            "new_added": 0,
            "modified_updated": 0,
            "deleted_removed": 0,
            "errors": 0
        }
        
        # 处理新文件
        for file_path in new_files:
            if self.add_file_to_kb(file_path):
                stats["new_added"] += 1
            else:
                stats["errors"] += 1
        
        # 处理修改的文件（重新添加）
        for file_path in modified_files:
            if self.add_file_to_kb(file_path):
                stats["modified_updated"] += 1
            else:
                stats["errors"] += 1
        
        # 处理删除的文件（知识库中的清理需要重建索引）
        if deleted_files:
            stats["deleted_removed"] = len(deleted_files)
            logger.info(f"📝 检测到 {len(deleted_files)} 个文件被删除，建议重建知识库索引")
        
        # 保存元数据
        self._save_metadata()
        
        # 生成更新报告
        total_processed = stats["new_added"] + stats["modified_updated"]
        logger.info(f"🎉 知识库更新完成: 新增{stats['new_added']}个，更新{stats['modified_updated']}个，删除{stats['deleted_removed']}个")
        
        if stats["errors"] > 0:
            logger.warning(f"⚠️ 处理过程中出现 {stats['errors']} 个错误")
        
        return stats
    
    def get_status(self) -> Dict:
        """获取自动管理器状态"""
        if not self.kb_manager:
            kb_stats = {"error": "知识库管理器未初始化"}
        else:
            kb_stats = self.kb_manager.get_stats()
        
        return {
            "watch_directories": [str(d) for d in self.watch_dirs],
            "supported_formats": list(self.supported_formats),
            "total_files": len(self.file_metadata["files"]),
            "last_scan": self.file_metadata.get("last_scan"),
            "scan_count": self.file_metadata.get("scan_count", 0),
            "knowledge_base": kb_stats,
            "categories": list(self.category_rules.keys())
        }
    
    def force_rescan(self) -> Dict[str, int]:
        """强制重新扫描并更新所有文件"""
        logger.info("🔄 强制重新扫描所有文件...")
        
        # 清空已有记录，强制重新处理所有文件
        self.file_metadata["files"] = {}
        
        return self.auto_update_knowledge_base()


def main():
    """命令行主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="自动知识库管理器")
    parser.add_argument("--watch-dir", action="append", 
                       help="添加监控目录 (可指定多个)")
    parser.add_argument("--scan", action="store_true", 
                       help="执行一次扫描更新")
    parser.add_argument("--force-rescan", action="store_true", 
                       help="强制重新扫描所有文件")
    parser.add_argument("--status", action="store_true", 
                       help="显示状态信息")
    parser.add_argument("--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR"], 
                       default="INFO", help="日志级别")
    
    args = parser.parse_args()
    
    # 设置日志
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 确定监控目录
    watch_dirs = args.watch_dir if args.watch_dir else ["knowledge_base/files"]
    
    # 创建自动管理器
    auto_manager = AutoKnowledgeBaseManager(watch_dirs=watch_dirs)
    
    if args.status:
        # 显示状态
        status = auto_manager.get_status()
        print("=== 自动知识库管理器状态 ===")
        for key, value in status.items():
            if isinstance(value, dict):
                print(f"{key}:")
                for sub_key, sub_value in value.items():
                    print(f"  {sub_key}: {sub_value}")
            else:
                print(f"{key}: {value}")
    
    elif args.force_rescan:
        # 强制重新扫描
        stats = auto_manager.force_rescan()
        print(f"强制重新扫描完成: {stats}")
    
    elif args.scan:
        # 执行扫描更新
        stats = auto_manager.auto_update_knowledge_base()
        print(f"扫描更新完成: {stats}")
    
    else:
        print("使用 --help 查看可用选项")
        print("\n快速开始:")
        print("  python3 auto_kb_manager.py --scan        # 扫描并更新知识库")
        print("  python3 auto_kb_manager.py --status      # 查看状态")
        print("  python3 auto_kb_manager.py --force-rescan # 强制重新扫描")


if __name__ == "__main__":
    main()