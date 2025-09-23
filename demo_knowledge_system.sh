#!/bin/bash
# Dragon机器人知识库系统完整演示

echo "🎯 Dragon机器人语音控制系统 + 本地知识库"
echo "================================================"

echo ""
echo "📋 系统状态检查..."
echo "  ✅ Python环境: $(python3 --version)"
echo "  ✅ 工作目录: $(pwd)"

# 检查知识库
echo "  🧠 知识库状态:"
if [ -d "simple_knowledge_base" ]; then
    echo "    ✅ 知识库目录存在"
    doc_count=$(python3 simple_kb_manager.py --stats 2>/dev/null | grep "总文件数" | awk '{print $3}' || echo "0")
    echo "    📚 包含文档: $doc_count 个"
else
    echo "    ⚠️ 知识库未初始化"
fi

echo ""
echo "🛠️ 快速设置知识库..."

# 创建知识库演示
if [ ! -d "docs/examples" ]; then
    echo "📁 创建演示文档目录..."
    mkdir -p docs/examples
    
    # 创建机器人操作手册
    cat > docs/examples/机器人操作手册.txt << 'EOF'
Dragon机器人操作手册

一、基本控制命令
1. 机器人前进 - 控制机器人向前移动，默认距离1米
2. 机器人后退 - 控制机器人向后移动，注意后方障碍
3. 机器人左转 - 控制机器人向左转向90度
4. 机器人右转 - 控制机器人向右转向90度
5. 机器人停止 - 立即停止所有机器人运动

二、关节控制命令
1. 抬起左手 - 左臂向上抬起到90度位置
2. 抬起右手 - 右臂向上抬起到90度位置
3. 放下左手 - 左臂放下到自然垂直位置
4. 放下右手 - 右臂放下到自然垂直位置

三、安全注意事项
1. 操作前请确保周围环境安全，无人员和障碍物
2. 机器人运动时请保持至少2米安全距离
3. 遇到紧急情况立即使用"机器人停止"命令
4. 定期检查机器人关节和传感器状态
5. 低电量时会自动停止，请及时充电

四、语音指令技巧
1. 说话清晰，语速适中
2. 使用标准普通话发音
3. 避免在嘈杂环境中使用
4. 每个指令间留有适当间隔
EOF

    # 创建常见问题文档
    cat > docs/examples/FAQ常见问题.md << 'EOF'
# Dragon机器人系统常见问题解答

## 语音识别问题

### Q: 语音识别不准确怎么办？
A: 请检查以下几点：
- 确保麦克风正常工作且音量适中
- 在安静环境中使用，避免背景噪音
- 说话清晰，使用标准普通话
- 保持与麦克风适当距离（30-50厘米）

### Q: 为什么没有语音回复？
A: 可能的原因和解决方案：
- 检查音频输出设备是否正常
- 确认网络连接稳定
- 验证豆包API密钥配置正确
- 重启系统重新初始化音频

### Q: 语音识别延迟很高？
A: 优化建议：
- 检查网络连接速度
- 确保系统资源充足
- 关闭不必要的后台程序
- 使用有线网络连接

## 机器人控制问题

### Q: 机器人不响应控制命令？
A: 排查步骤：
- 确认ROS系统正常运行
- 检查机器人硬件连接状态
- 验证控制指令格式正确
- 查看系统日志错误信息

### Q: 机器人动作不精确？
A: 调整方法：
- 校准机器人关节参数
- 检查机械部件磨损情况
- 更新控制算法参数
- 进行系统重新标定

### Q: 支持哪些具体的控制命令？
A: 当前支持的语音指令：
- 移动控制：前进、后退、左转、右转、停止
- 关节控制：抬左手、抬右手、放下左手、放下右手
- 安全控制：紧急停止、回到初始位置

## 系统配置问题

### Q: 如何配置豆包API？
A: 配置步骤：
1. 获取豆包API密钥
2. 编辑.env文件添加密钥
3. 设置正确的API端点URL
4. 测试连接是否正常

### Q: 知识库如何添加文档？
A: 添加方法：
```bash
# 添加单个文档
python3 simple_kb_manager.py --add "文档路径" --title "标题"

# 批量添加目录
python3 simple_kb_manager.py --add-dir "目录路径"
```

### Q: 知识库搜索不到内容？
A: 检查项目：
- 确认文档已正确添加
- 检查搜索关键词是否准确
- 验证文档内容编码格式
- 重建知识库索引
EOF

    # 创建技术规范文档
    cat > docs/examples/技术规范.txt << 'EOF'
Dragon机器人技术规范文档

一、硬件规格
1. 处理器：ARM Cortex-A78 八核心 2.4GHz
2. 内存：8GB LPDDR5
3. 存储：256GB eUFS 3.1
4. 传感器：
   - 激光雷达：360度扫描，测距精度±2cm
   - 摄像头：4K分辨率，支持夜视
   - IMU：9轴惯性测量单元
   - 超声波：16个，检测范围0.02-4m

二、软件架构
1. 操作系统：Ubuntu 20.04 LTS
2. 机器人框架：ROS2 Galactic
3. 语音引擎：豆包实时语音API
4. 控制算法：PID + 自适应控制
5. 导航系统：SLAM + 路径规划

三、通信协议
1. WiFi：802.11ac，双频段
2. 蓝牙：5.2，低功耗
3. 串口：RS485，波特率115200
4. 网络：支持5G/4G模块扩展

四、性能指标
1. 语音识别准确率：>95%
2. 响应延迟：<500ms
3. 定位精度：±5cm
4. 续航时间：8-10小时
5. 负载能力：最大5kg

五、安全特性
1. 碰撞检测：全方位传感器保护
2. 紧急停止：硬件级安全开关
3. 防跌落：边缘检测算法
4. 过热保护：自动降频和报警
5. 权限管理：多级用户访问控制
EOF

    echo "📝 演示文档创建完成"
fi

# 添加文档到知识库
echo "📚 添加文档到知识库..."
python3 simple_kb_manager.py --add "docs/examples/机器人操作手册.txt" --title "机器人操作手册" --category "操作指南" 2>/dev/null
python3 simple_kb_manager.py --add "docs/examples/FAQ常见问题.md" --title "常见问题解答" --category "技术支持" 2>/dev/null  
python3 simple_kb_manager.py --add "docs/examples/技术规范.txt" --title "技术规范文档" --category "技术文档" 2>/dev/null

echo ""
echo "🔍 知识库测试..."

# 测试搜索功能
echo "测试搜索 '机器人控制':"
python3 simple_kb_manager.py --search "机器人控制" 2>/dev/null | grep -A 5 "📄 结果" | head -10

echo ""
echo "测试搜索 '语音识别问题':"
python3 simple_kb_manager.py --search "语音识别" 2>/dev/null | grep -A 5 "📄 结果" | head -10

echo ""
echo "📊 知识库统计信息:"
python3 simple_kb_manager.py --stats 2>/dev/null | grep -E "(总文件数|总片段数|文件类型|分类分布)"

echo ""
echo "🎯 系统演示场景:"
echo ""
echo "1️⃣ 机器人控制演示:"
echo "   用户说: '机器人前进'"
echo "   系统: ✅ 执行前进动作 + 🧠 无需知识库"
echo ""
echo "2️⃣ 知识库问答演示:"
echo "   用户说: '机器人怎么控制？'"
echo "   系统: 🧠 搜索操作手册 → 📚 返回控制方法"
echo ""
echo "3️⃣ 故障排除演示:"
echo "   用户说: '语音识别不准确怎么办？'"
echo "   系统: 🧠 搜索FAQ文档 → 🔧 提供解决方案"
echo ""
echo "4️⃣ 技术咨询演示:"
echo "   用户说: '机器人的技术规格是什么？'"
echo "   系统: 🧠 搜索技术文档 → 📋 详细技术参数"

echo ""
echo "🚀 启动系统:"
echo "   python3 dragon_robot_session.py"
echo ""
echo "💡 知识库管理:"
echo "   python3 simple_kb_manager.py --help"
echo ""
echo "✅ 演示设置完成！现在可以启动系统进行测试。"
