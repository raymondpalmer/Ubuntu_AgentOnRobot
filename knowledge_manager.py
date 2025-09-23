"""
知识库管理命令行工具
支持添加、搜索、管理知识库文档
"""

import argparse
import os
import sys
from knowledge_base import LocalKnowledgeBase
import json

def print_banner():
    """打印工具横幅"""
    print("=" * 60)
    print("🧠 Dragon机器人本地知识库管理工具")
    print("支持格式: PDF, Word, 文本, CSV, Markdown等")
    print("=" * 60)

def add_file_command(kb: LocalKnowledgeBase, args):
    """添加文件命令"""
    if not os.path.exists(args.add):
        print(f"❌ 文件不存在: {args.add}")
        return
    
    title = args.title or os.path.basename(args.add)
    metadata = {}
    
    if args.category:
        metadata['category'] = args.category
    if args.tags:
        metadata['tags'] = [tag.strip() for tag in args.tags.split(',')]
    
    success = kb.add_document(args.add, title=title, metadata=metadata)
    
    if success:
        print(f"✅ 文件添加成功: {title}")
        
        # 重新构建索引
        print("🔄 正在重新构建搜索索引...")
        kb.build_index()
        kb.save_knowledge_base()
        print("💾 知识库已保存")
    else:
        print(f"❌ 文件添加失败: {args.add}")

def add_directory_command(kb: LocalKnowledgeBase, args):
    """添加目录命令"""
    if not os.path.exists(args.add_dir):
        print(f"❌ 目录不存在: {args.add_dir}")
        return
    
    print(f"📁 正在扫描目录: {args.add_dir}")
    recursive = not args.no_recursive
    
    added_count = kb.add_directory(args.add_dir, recursive=recursive)
    
    if added_count > 0:
        print(f"✅ 成功添加 {added_count} 个文档")
        
        # 重新构建索引
        print("🔄 正在构建搜索索引...")
        kb.build_index()
        kb.save_knowledge_base()
        print("💾 知识库已保存")
    else:
        print("⚠️ 没有找到支持的文档文件")

def search_command(kb: LocalKnowledgeBase, args):
    """搜索命令"""
    print(f"🔍 搜索查询: '{args.search}'")
    print("-" * 50)
    
    results = kb.search(args.search, top_k=args.top_k or 5)
    
    if not results:
        print("❌ 没有找到相关结果")
        return
    
    for i, result in enumerate(results, 1):
        score = result.get('score', 0)
        print(f"\n📄 结果 {i} (相似度: {score:.3f})")
        print(f"标题: {result['title']}")
        print(f"来源: {result['source']}")
        print(f"类型: {result.get('file_type', 'unknown')}")
        
        content = result['content']
        if len(content) > 200:
            content = content[:200] + "..."
        print(f"内容预览: {content}")
        print("-" * 30)

def list_command(kb: LocalKnowledgeBase, args):
    """列出文档命令"""
    documents = kb.list_documents()
    
    if not documents:
        print("📚 知识库为空")
        return
    
    print(f"📚 知识库包含 {len(documents)} 个文档:")
    print("-" * 60)
    
    for i, doc in enumerate(documents, 1):
        print(f"{i:3d}. {doc['title']}")
        print(f"     文件: {doc['file_path']}")
        print(f"     类型: {doc['file_type']}")
        print(f"     片段: {doc['chunks_count']} 个")
        print(f"     时间: {doc['added_at'][:19]}")
        print()

def stats_command(kb: LocalKnowledgeBase, args):
    """统计信息命令"""
    stats = kb.get_statistics()
    
    print("📊 知识库统计信息:")
    print("-" * 30)
    print(f"文档总数: {stats['total_files']}")
    print(f"片段总数: {stats['total_chunks']}")
    print(f"搜索引擎: {stats['search_engine']}")
    print(f"更新时间: {stats['last_updated'][:19]}")
    
    print("\n📋 文件类型分布:")
    for file_type, count in stats['file_types'].items():
        print(f"  {file_type}: {count} 个片段")

def remove_command(kb: LocalKnowledgeBase, args):
    """移除文档命令"""
    if not os.path.exists(args.remove):
        print(f"❌ 文件不存在: {args.remove}")
        return
    
    success = kb.remove_document(args.remove)
    
    if success:
        print(f"✅ 文档移除成功: {args.remove}")
        kb.save_knowledge_base()
        print("💾 知识库已保存")
    else:
        print(f"❌ 文档移除失败或不存在: {args.remove}")

def rebuild_command(kb: LocalKnowledgeBase, args):
    """重建索引命令"""
    if not kb.documents:
        print("⚠️ 知识库为空，无需重建索引")
        return
    
    print("🔄 正在重建搜索索引...")
    kb.build_index()
    kb.save_knowledge_base()
    print("✅ 索引重建完成")

def clear_command(kb: LocalKnowledgeBase, args):
    """清空知识库命令"""
    if not args.confirm:
        print("⚠️ 此操作将删除所有知识库数据，请使用 --confirm 确认")
        return
    
    kb.documents = []
    kb.metadata = {}
    kb.save_knowledge_base()
    print("✅ 知识库已清空")

def export_command(kb: LocalKnowledgeBase, args):
    """导出知识库命令"""
    export_data = {
        'documents': kb.documents,
        'metadata': kb.metadata,
        'stats': kb.get_statistics()
    }
    
    output_file = args.export or 'knowledge_base_export.json'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 知识库已导出到: {output_file}")

def test_command(kb: LocalKnowledgeBase, args):
    """测试命令"""
    test_queries = [
        "机器人操作方法",
        "安全规定",
        "技术文档",
        "项目介绍",
        "使用说明"
    ]
    
    print("🧪 知识库搜索测试:")
    print("-" * 40)
    
    for query in test_queries:
        results = kb.search(query, top_k=2)
        print(f"\n查询: '{query}'")
        if results:
            print(f"  找到 {len(results)} 个结果，最佳匹配: {results[0]['title']}")
        else:
            print("  没有找到结果")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="Dragon机器人本地知识库管理工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 添加单个文件
  python knowledge_manager.py --add document.pdf --title "技术文档"
  
  # 批量添加目录
  python knowledge_manager.py --add-dir ./docs/ --category "技术文档"
  
  # 搜索知识库
  python knowledge_manager.py --search "机器人操作方法" --top-k 3
  
  # 查看统计信息
  python knowledge_manager.py --stats
  
  # 列出所有文档
  python knowledge_manager.py --list
        """
    )
    
    # 文件操作
    parser.add_argument('--add', type=str, help='添加单个文件到知识库')
    parser.add_argument('--add-dir', type=str, help='批量添加目录中的文件')
    parser.add_argument('--remove', type=str, help='从知识库移除文件')
    parser.add_argument('--title', type=str, help='文档标题')
    parser.add_argument('--category', type=str, help='文档分类')
    parser.add_argument('--tags', type=str, help='文档标签(逗号分隔)')
    parser.add_argument('--no-recursive', action='store_true', help='不递归扫描子目录')
    
    # 搜索操作
    parser.add_argument('--search', type=str, help='搜索知识库')
    parser.add_argument('--top-k', type=int, default=5, help='搜索结果数量')
    
    # 信息查看
    parser.add_argument('--list', action='store_true', help='列出所有文档')
    parser.add_argument('--stats', action='store_true', help='显示统计信息')
    
    # 管理操作
    parser.add_argument('--rebuild', action='store_true', help='重建搜索索引')
    parser.add_argument('--clear', action='store_true', help='清空知识库')
    parser.add_argument('--confirm', action='store_true', help='确认危险操作')
    
    # 导入导出
    parser.add_argument('--export', type=str, help='导出知识库到JSON文件')
    
    # 测试功能
    parser.add_argument('--test', action='store_true', help='运行搜索测试')
    
    # 配置选项
    parser.add_argument('--kb-dir', type=str, default='knowledge_base', help='知识库目录路径')
    
    args = parser.parse_args()
    
    # 如果没有参数，显示帮助
    if len(sys.argv) == 1:
        print_banner()
        parser.print_help()
        return
    
    print_banner()
    
    try:
        # 初始化知识库
        print(f"📂 知识库目录: {args.kb_dir}")
        kb = LocalKnowledgeBase(knowledge_dir=args.kb_dir)
        
        # 执行命令
        if args.add:
            add_file_command(kb, args)
        elif args.add_dir:
            add_directory_command(kb, args)
        elif args.search:
            search_command(kb, args)
        elif args.list:
            list_command(kb, args)
        elif args.stats:
            stats_command(kb, args)
        elif args.remove:
            remove_command(kb, args)
        elif args.rebuild:
            rebuild_command(kb, args)
        elif args.clear:
            clear_command(kb, args)
        elif args.export:
            export_command(kb, args)
        elif args.test:
            test_command(kb, args)
        else:
            print("⚠️ 请指定要执行的操作")
            parser.print_help()
            
    except KeyboardInterrupt:
        print("\n👋 操作已取消")
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
