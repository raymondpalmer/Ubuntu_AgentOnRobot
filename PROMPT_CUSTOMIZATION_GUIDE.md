# Dragon机器人Prompt自定义指南

## 概述
Dragon机器人系统现已支持完全自定义的prompt配置，您可以轻松调整系统的行为、语言风格和不同场景的响应方式。

## 📁 相关文件
- `dragon_prompts_config.py` - 主要的prompt配置文件
- `prompt_manager.py` - prompt管理工具
- `dragon_robot_session.py` - 集成了prompt配置的主系统

## 🎯 核心功能

### 1. 系统角色配置
定义机器人的基本人格和行为准则：
- `default` - 默认的专业助手角色
- `friendly` - 友好热情的伙伴角色
- `professional` - 专业技术导向角色
- `technical` - 技术专家角色

### 2. 说话风格配置
控制机器人的语言风格：
- `natural` - 自然友好的语调
- `warm` - 温暖亲切的语调
- `professional` - 专业稳重的语调
- `energetic` - 充满活力的语调
- `calm` - 平和稳定的语调

### 3. 应用场景配置
针对不同使用环境的专门配置：
- `industrial` - 工业生产环境
- `home` - 家庭服务环境
- `education` - 教育培训环境

## 🛠️ 使用方法

### 基本查看和测试
```bash
# 查看当前配置
python3 prompt_manager.py show

# 测试特定角色
python3 prompt_manager.py test friendly

# 验证配置文件
python3 prompt_manager.py validate
```

### 编辑配置
```bash
# 打开配置文件编辑
python3 prompt_manager.py edit

# 备份当前配置
python3 prompt_manager.py backup

# 恢复配置
python3 prompt_manager.py restore <backup_file>
```

## ⚙️ 自定义配置

### 1. 修改现有角色
打开 `dragon_prompts_config.py`，找到对应的角色定义，直接修改内容：

```python
self.system_roles = {
    "default": """你的自定义系统角色描述...""",
    # 其他角色...
}
```

### 2. 添加新角色
在 `__init__` 方法中添加新的角色：

```python
self.system_roles["my_custom_role"] = """
你是我的自定义机器人助手，特点：
- 特点1
- 特点2
- 特点3
"""
```

### 3. 创建新场景
在 `scenario_prompts` 中添加新场景：

```python
self.scenario_prompts["retail"] = {
    "system_role": """你是零售店的服务机器人...""",
    "greeting": "欢迎光临！我是您的购物助手。"
}
```

### 4. 自定义说话风格
在 `speaking_styles` 中添加新风格：

```python
self.speaking_styles["humorous"] = "幽默风趣的语调，适当使用俏皮话和比喻。"
```

## 🔧 高级配置

### 动态配置切换
在程序运行时动态更新配置：

```python
from dragon_robot_session import DragonDialogSession

session = DragonDialogSession()

# 更新配置
session.update_prompts_config()

# 查看当前配置信息
print(session.get_current_prompts_info())
```

### 程序化配置
直接在代码中修改配置：

```python
from dragon_prompts_config import DragonRobotPrompts

prompts = DragonRobotPrompts()

# 添加自定义角色
prompts.add_custom_role("customer_service", "你是专业的客服助手...")

# 自定义现有角色
prompts.customize_prompt("friendly", "你的新友好角色定义...")
```

## 📝 配置模板

### 工业场景模板
```python
"industrial_safety": {
    "system_role": '''你是工业安全监督机器人：
    - 始终优先考虑操作安全
    - 严格遵循安全操作规程
    - 及时提醒潜在安全风险
    - 使用标准工业术语''',
    "greeting": "安全检查完毕，工业机器人系统就绪。"
}
```

### 教育场景模板
```python
"kids_education": {
    "system_role": '''你是儿童教育机器人：
    - 使用简单易懂的语言
    - 保持耐心和鼓励
    - 适时提供正面反馈
    - 让学习变得有趣''',
    "greeting": "小朋友好！我是你的学习伙伴，今天想学什么呢？"
}
```

### 家庭场景模板
```python
"elderly_care": {
    "system_role": '''你是老年人关怀机器人：
    - 语速适中，语调温和
    - 重复重要信息
    - 提供日常生活帮助
    - 关注健康和安全''',
    "greeting": "您好！我是您的生活助手，有什么需要帮助的吗？"
}
```

## 📋 最佳实践

### 1. 角色定义原则
- **明确性**：清楚定义机器人的身份和职责
- **一致性**：保持角色特点在所有对话中的一致性
- **适用性**：确保角色适合实际使用场景

### 2. 语言风格建议
- **简洁性**：适合语音播放，避免过长句子
- **自然性**：使用自然的对话语言
- **专业性**：根据场景使用适当的专业术语

### 3. 场景配置要点
- **场景特异性**：针对具体场景的特殊需求
- **安全考虑**：特别是工业场景的安全要求
- **用户友好**：考虑目标用户群体的特点

## 🚀 测试和验证

### 1. 配置验证
每次修改后都要验证配置：
```bash
python3 prompt_manager.py validate
```

### 2. 功能测试
测试不同角色的表现：
```bash
python3 prompt_manager.py test <role_name>
```

### 3. 集成测试
确保修改后的配置在主系统中正常工作：
```bash
python3 -c "from dragon_robot_session import DragonDialogSession; print('✅ 配置加载成功')"
```

## 🔄 版本管理

### 备份配置
```bash
python3 prompt_manager.py backup
```

### 版本控制
建议将配置文件纳入Git版本控制：
```bash
git add dragon_prompts_config.py
git commit -m "更新prompt配置"
```

## 💡 使用建议

1. **开始简单**：先修改现有角色，熟悉系统后再创建新角色
2. **小步测试**：每次修改后都要验证和测试
3. **备份重要**：修改前先备份当前配置
4. **文档记录**：记录自定义配置的用途和效果
5. **用户反馈**：根据实际使用效果调整配置

## ❓ 常见问题

**Q: 修改配置后没有生效？**
A: 重启系统或使用 `update_prompts_config()` 方法重新加载配置。

**Q: 配置文件损坏了怎么办？**
A: 使用 `restore` 命令恢复备份，或从Git历史中恢复。

**Q: 如何为不同客户创建不同配置？**
A: 创建不同的配置文件，使用 `update_prompts_config(config_path)` 加载。

**Q: 配置太多了，如何管理？**
A: 使用有意义的命名，添加注释，定期清理不用的配置。

---

通过这个prompt自定义系统，您可以让Dragon机器人适应各种不同的使用场景和用户需求，打造真正个性化的机器人助手！
