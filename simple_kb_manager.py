#!/usr/bin/env python3
"""
简化版知识库管理工具
"""

import argparse
import os
import sys
from simple_knowledge_base import SimpleKnowledgeBase

def print_banner():
    """打印工具横幅"""
    print("=" * 60)
    print("🧠 Dragon机器人简化版知识库管理工具")
    print("支持格式: PDF, Word, 文本, Markdown等")
    print("=" * 60)

def main():
    print_banner()
    
    parser = argparse.ArgumentParser(description='简化版知识库管理工具')
    parser.add_argument('--add', type=str, help='添加文件到知识库')
    parser.add_argument('--title', type=str, help='文件标题')
    parser.add_argument('--category', type=str, help='文档分类')
    parser.add_argument('--search', type=str, help='搜索知识库')
    parser.add_argument('--list', action='store_true', help='列出所有文档')
    parser.add_argument('--stats', action='store_true', help='显示统计信息')
    parser.add_argument('--test', action='store_true', help='测试知识库功能')
    
    args = parser.parse_args()
    
    # 创建知识库实例
    kb = SimpleKnowledgeBase()
    
    if args.add:
        # 添加文件
        if not os.path.exists(args.add):
            print(f"❌ 文件不存在: {args.add}")
            return
        
        title = args.title or os.path.basename(args.add)
        success = kb.add_document(args.add, title=title, category=args.category)
        
        if success:
            kb.save_knowledge_base()
            print(f"✅ 文件添加成功: {title}")
        else:
            print(f"❌ 文件添加失败: {args.add}")
    
    elif args.search:
        # 搜索
        print(f"🔍 搜索查询: '{args.search}'")
        print("-" * 50)
        
        results = kb.search(args.search, top_k=5)
        
        if not results:
            print("❌ 没有找到相关结果")
            return
        
        for i, result in enumerate(results, 1):
            print(f"\n📄 结果 {i} (得分: {result['score']:.2f})")
            print(f"标题: {result['title']}")
            print(f"来源: {result['source']}")
            print(f"类型: {result['file_type']}")
            print(f"分类: {result['category']}")
            
            content = result['content']
            if len(content) > 200:
                content = content[:200] + "..."
            print(f"内容预览: {content}")
            print("-" * 30)
    
    elif args.list:
        # 列出文档
        documents = kb.list_documents()
        
        if not documents:
            print("📚 知识库为空")
            return
        
        print(f"📚 知识库包含 {len(documents)} 个文档:")
        print("-" * 60)
        
        for i, doc in enumerate(documents, 1):
            print(f"  {i}. {doc['title']}")
            print(f"     文件: {doc['file_path']}")
            print(f"     类型: {doc['file_type']}")
            print(f"     分类: {doc['category']}")
            print(f"     片段: {doc['chunks_count']} 个")
            print(f"     时间: {doc['added_at'][:19]}")
            print()
    
    elif args.stats:
        # 显示统计信息
        stats = kb.get_statistics()
        
        print("📊 知识库统计信息:")
        print(f"  📁 总文件数: {stats['total_files']}")
        print(f"  📄 总片段数: {stats['total_chunks']}")
        
        print(f"  📈 文件类型分布:")
        for file_type, count in stats['file_types'].items():
            print(f"    - {file_type}: {count} 个片段")
        
        print(f"  🏷️ 分类分布:")
        for category, count in stats['categories'].items():
            print(f"    - {category}: {count} 个片段")
        
        print(f"  🕒 最后更新: {stats['last_updated'][:19]}")
    
    elif args.test:
        # 测试功能
        print("🔧 测试知识库功能...")
        
        # 显示统计信息
        stats = kb.get_statistics()
        print(f"当前包含 {stats['total_files']} 个文档，{stats['total_chunks']} 个片段")
        
        if stats['total_chunks'] > 0:
            # 测试搜索
            test_queries = ["机器人", "操作", "问题", "规定"]
            
            for query in test_queries:
                print(f"\n🔍 测试搜索: '{query}'")
                results = kb.search(query, top_k=2)
                
                if results:
                    for result in results:
                        print(f"  - {result['title']} (得分: {result['score']:.2f})")
                else:
                    print("  - 无结果")
        else:
            print("知识库为空，请先添加文档")
    
    else:
        # 显示默认信息
        stats = kb.get_statistics()
        print(f"📂 知识库目录: {kb.knowledge_dir}")
        print(f"📊 当前状态: {stats['total_files']} 个文档，{stats['total_chunks']} 个片段")
        print()
        print("💡 使用示例:")
        print("  添加文档: python3 simple_kb_manager.py --add 'file.txt' --title 'My Document'")
        print("  搜索内容: python3 simple_kb_manager.py --search '关键词'")
        print("  查看列表: python3 simple_kb_manager.py --list")
        print("  查看统计: python3 simple_kb_manager.py --stats")
        print("  功能测试: python3 simple_kb_manager.py --test")

if __name__ == "__main__":
    main()
