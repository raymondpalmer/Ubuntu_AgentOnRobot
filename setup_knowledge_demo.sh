#!/bin/bash
# Dragon机器人知识库快速设置脚本

echo "🧠 Dragon机器人知识库系统设置"
echo "================================"

# 创建知识库目录
echo "📁 创建知识库目录..."
mkdir -p knowledge_base/{documents,metadata,indices,files}
mkdir -p docs/examples

# 创建示例文档
echo "📝 创建示例文档..."

cat > docs/examples/机器人操作手册.txt << 'EOF'
Dragon机器人操作手册

一、基本控制命令
1. 机器人前进 - 控制机器人向前移动
2. 机器人后退 - 控制机器人向后移动
3. 机器人左转 - 控制机器人向左转向
4. 机器人右转 - 控制机器人向右转向
5. 机器人停止 - 立即停止机器人运动

二、关节控制命令
1. 抬起左手 - 左臂向上抬起90度
2. 抬起右手 - 右臂向上抬起90度
3. 放下左手 - 左臂放下到0度位置
4. 放下右手 - 右臂放下到0度位置

三、安全注意事项
1. 使用前请确保周围环境安全
2. 机器人运动时请保持安全距离
3. 遇到紧急情况立即说"机器人停止"
4. 定期检查机器人关节状态

四、故障排除
1. 如果语音识别不准确，请调节麦克风音量
2. 如果机器人无响应，请检查ROS连接状态
3. 如果音频播放异常，请检查音频设备配置
EOF

cat > docs/examples/常见问题.md << 'EOF'
# Dragon机器人常见问题解答

## 语音相关问题

### Q: 为什么语音识别不准确？
A: 请检查以下几点：
- 确保麦克风正常工作
- 调节适当的音量
- 在安静环境中使用
- 说话清晰、语速适中

### Q: 为什么没有语音回复？
A: 可能的原因：
- 音频设备配置问题
- 网络连接异常
- API密钥未正确配置

## 机器人控制问题

### Q: 机器人不执行命令怎么办？
A: 请检查：
- ROS系统是否正常运行
- 机器人硬件连接状态
- 确认使用正确的语音指令

### Q: 支持哪些控制命令？
A: 当前支持的命令包括：
- 基本移动：前进、后退、左转、右转、停止
- 关节控制：抬手、放手等动作

## 系统配置问题

### Q: 如何配置API密钥？
A: 编辑.env文件，添加：
```
DOUBAO_API_KEY=your_api_key_here
DOUBAO_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
```

### Q: 如何添加自定义知识库？
A: 使用知识库管理工具：
```bash
python knowledge_manager.py --add "文件路径" --title "文档标题"
```
EOF

cat > docs/examples/公司规章制度.txt << 'EOF'
某公司员工管理规定

第一章 考勤制度
1. 员工应按时上下班，工作时间为9:00-18:00
2. 请假需提前申请，病假需提供医院证明
3. 迟到早退按相关规定扣除绩效

第二章 行为规范
1. 员工应着装整洁，符合公司形象要求
2. 工作时间内不得从事与工作无关的活动
3. 保持良好的团队协作精神

第三章 安全规定
1. 严格遵守机器人操作安全规范
2. 不得在无人监督情况下操作危险设备
3. 发现安全隐患应立即报告

第四章 保密条款
1. 不得泄露公司技术机密
2. 客户信息需严格保密
3. 离职后仍需履行保密义务
EOF

# 添加文档到知识库
echo "📚 添加示例文档到知识库..."
python knowledge_manager.py --add "docs/examples/机器人操作手册.txt" --title "机器人操作手册" --category "技术文档"
python knowledge_manager.py --add "docs/examples/常见问题.md" --title "常见问题解答" --category "帮助文档"
python knowledge_manager.py --add "docs/examples/公司规章制度.txt" --title "公司管理规定" --category "规章制度"

# 构建索引
echo "🔄 构建知识库索引..."
python knowledge_manager.py --build

echo ""
echo "✅ 知识库设置完成！"
echo ""
echo "📖 使用方法："
echo "1. 添加文档：python knowledge_manager.py --add '文件路径' --title '标题'"
echo "2. 搜索测试：python knowledge_manager.py --search '关键词'"
echo "3. 查看列表：python knowledge_manager.py --list"
echo "4. 启动系统：python dragon_robot_session.py"
echo ""
echo "🎯 现在可以问机器人："
echo "  - '机器人怎么操作？'"
echo "  - '请假需要什么手续？'"
echo "  - '语音识别不准确怎么办？'"
echo ""
