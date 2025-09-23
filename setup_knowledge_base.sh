#!/bin/bash
"""
Dragon机器人知识库快速设置脚本
"""

echo "🧠 Dragon机器人本地知识库设置"
echo "=================================="

# 检查Python环境
echo "📦 检查Python环境..."
python3 --version
if [ $? -ne 0 ]; then
    echo "❌ Python3未安装"
    exit 1
fi

# 安装知识库依赖
echo "📦 安装知识库依赖..."
pip3 install -r requirements_knowledge.txt

if [ $? -eq 0 ]; then
    echo "✅ 依赖安装成功"
else
    echo "⚠️ 部分依赖安装失败，尝试单独安装..."
    pip3 install sentence-transformers scikit-learn numpy PyPDF2 python-docx pandas python-dotenv
fi

# 创建知识库目录结构
echo "📁 创建知识库目录..."
mkdir -p knowledge_base/{documents,metadata,indices}
mkdir -p docs/{manuals,guides,references}

echo "✅ 知识库目录创建完成"

# 创建示例文档
echo "📄 创建示例文档..."

cat > docs/manuals/robot_manual.txt << 'EOF'
Dragon机器人操作手册

## 基本控制指令
- 前进：机器人向前移动
- 后退：机器人向后移动  
- 左转：机器人向左转向
- 右转：机器人向右转向
- 停止：机器人停止所有运动

## 安全注意事项
1. 操作前确保周围环境安全
2. 避免在狭小空间内高速移动
3. 发现异常立即使用停止指令
4. 定期检查机器人状态

## 维护指南
- 每日检查电池电量
- 定期清洁传感器
- 检查关节润滑情况
- 软件更新和日志检查
EOF

cat > docs/guides/voice_commands.md << 'EOF'
# 语音指令指南

## 基本移动指令
- "机器人前进" / "往前走" / "向前移动"
- "机器人后退" / "往后退" / "向后移动"  
- "机器人左转" / "向左转" / "往左转"
- "机器人右转" / "向右转" / "往右转"
- "机器人停止" / "停下来" / "不要动"

## 对话功能
- 可以与机器人进行自然对话
- 询问技术问题会基于知识库回答
- 支持中文语音识别和语音回复

## 注意事项
- 说话要清晰，避免背景噪音
- 指令要简洁明确
- 等待机器人执行完成再发出下一个指令
EOF

cat > docs/references/faq.txt << 'EOF'
常见问题解答

Q: 机器人不响应语音指令怎么办？
A: 检查麦克风是否正常工作，确保网络连接稳定，语音要清晰。

Q: 如何添加新的控制指令？
A: 在代码中修改command_map字典，添加新的指令映射。

Q: 语音识别不准确怎么办？
A: 说话时要清晰，避免方言，确保环境安静。

Q: 如何更新知识库？
A: 使用knowledge_manager.py工具添加新文档到知识库。

Q: 机器人移动异常怎么办？
A: 立即使用"停止"指令，检查硬件连接和ROS状态。
EOF

echo "✅ 示例文档创建完成"

# 测试知识库功能
echo "🧪 测试知识库功能..."
python3 knowledge_manager.py --add-dir docs/ --category "系统文档"

if [ $? -eq 0 ]; then
    echo "✅ 知识库测试成功"
    
    # 显示统计信息
    echo "📊 知识库状态:"
    python3 knowledge_manager.py --stats
    
    echo ""
    echo "🎯 快速测试搜索:"
    python3 knowledge_manager.py --search "机器人操作方法" --top-k 2
    
else
    echo "⚠️ 知识库测试失败，请检查依赖安装"
fi

echo ""
echo "✅ Dragon机器人知识库设置完成！"
echo ""
echo "📚 使用方法:"
echo "1. 添加文档: python3 knowledge_manager.py --add your_document.pdf"
echo "2. 搜索测试: python3 knowledge_manager.py --search '你的问题'"
echo "3. 查看文档: python3 knowledge_manager.py --list"
echo "4. 启动系统: python3 dragon_robot_session.py"
echo ""
echo "🎤 现在你可以对机器人说话了，它会基于知识库智能回答！"
