# Dragon机器人音色配置使用指南

## 概述
Dragon机器人系统现已支持完全自定义的音色配置，您可以根据不同场景和用户需求选择最适合的声音效果。

## 📁 相关文件
- `voice_config.py` - 主要的音色配置文件
- `voice_manager.py` - 命令行音色管理工具
- `voice_demo.py` - 音色演示和测试脚本
- `dragon_robot_session.py` - 集成了音色配置的主系统

## 🎵 可用音色

### 👩 女声音色
| 音色ID | 名称 | 风格特点 | 推荐场景 |
|--------|------|----------|----------|
| `BV700_streaming` | 温柔自然女声 | 温柔、自然、适合日常对话 | 家庭、客服、教育 |
| `BV705_streaming` | 甜美清新女声 | 甜美、清新、年轻活力 | 教育、娱乐、儿童 |
| `BV701_streaming` | 专业播音女声 | 专业、正式、播音腔调 | 商务、新闻、正式场合 |

### 👨 男声音色
| 音色ID | 名称 | 风格特点 | 推荐场景 |
|--------|------|----------|----------|
| `BV406_streaming` | 沉稳磁性男声 | 沉稳、磁性、成熟稳重 | 工业、商务、技术 |
| `BV407_streaming` | 年轻活力男声 | 年轻、活力、朝气蓬勃 | 运动、娱乐、青年 |

### 🎭 特殊音色
| 音色ID | 名称 | 风格特点 | 推荐场景 |
|--------|------|----------|----------|
| `BV102_streaming` | 童声音色 | 童真、可爱、天真烂漫 | 儿童教育、童话、游戏 |
| `BV002_streaming` | 老年音色 | 慈祥、温和、长者风范 | 老年关怀、传统文化、故事讲述 |

## 🛠️ 使用方法

### 命令行管理
```bash
# 查看当前音色配置
python3 voice_manager.py show

# 列出所有可用音色
python3 voice_manager.py list

# 切换到指定音色
python3 voice_manager.py set BV700_streaming

# 设置音色并调整参数
python3 voice_manager.py set BV406_streaming --speed 1.2 --volume 1.1 --pitch 0.9

# 查看场景推荐
python3 voice_manager.py scenarios

# 测试音色效果
python3 voice_manager.py test BV705_streaming

# 备份当前配置
python3 voice_manager.py backup

# 恢复配置
python3 voice_manager.py restore voice_config_backup_20250915_143022.json
```

### 代码中使用
```python
from voice_config import VoiceConfig

# 创建音色配置实例
voice_config = VoiceConfig()

# 切换音色
voice_config.set_voice("BV705_streaming")

# 调整音色参数
voice_config.set_voice("BV406_streaming", speed=1.2, volume=1.1, pitch=0.9)

# 获取场景推荐音色
recommended = voice_config.get_recommended_voice("industrial")

# 获取TTS配置
tts_config = voice_config.get_config_for_tts()
```

### 主系统集成
```python
from dragon_robot_session import DragonDialogSession

# 创建会话实例
session = DragonDialogSession()

# 切换音色
session.update_voice_config("BV705_streaming")

# 设置场景音色
session.set_scenario_voice("industrial")

# 查看当前音色信息
print(session.get_current_voice_info())
```

## ⚙️ 音色参数

### 可调节参数
- **语速 (speed_ratio)**: 0.5-2.0，默认1.0
  - 0.5-0.8: 慢速，适合老年用户或重要信息
  - 0.9-1.1: 正常速度，日常对话
  - 1.2-2.0: 快速，活力充沛

- **音量 (volume_ratio)**: 0.5-2.0，默认1.0
  - 0.5-0.8: 轻柔，适合安静环境
  - 0.9-1.1: 正常音量
  - 1.2-2.0: 响亮，适合嘈杂环境

- **音调 (pitch_ratio)**: 0.5-2.0，默认1.0
  - 0.5-0.8: 低音调，更加沉稳
  - 0.9-1.1: 正常音调
  - 1.2-2.0: 高音调，更加活泼

### 参数组合建议
```python
# 工业场景：沉稳可靠
voice_config.set_voice("BV406_streaming", speed=0.9, volume=1.2, pitch=0.8)

# 家庭场景：温柔亲切
voice_config.set_voice("BV700_streaming", speed=1.0, volume=1.0, pitch=1.0)

# 教育场景：活泼清晰
voice_config.set_voice("BV705_streaming", speed=1.1, volume=1.1, pitch=1.1)

# 商务场景：专业正式
voice_config.set_voice("BV701_streaming", speed=0.95, volume=1.0, pitch=0.95)
```

## 🎬 场景适配

### 自动场景切换
系统支持根据使用场景自动推荐合适的音色：

```python
# 场景音色映射
scenario_voices = {
    "default": "BV700_streaming",      # 默认 - 温柔女声
    "industrial": "BV406_streaming",   # 工业 - 沉稳男声
    "home": "BV700_streaming",         # 家庭 - 温柔女声
    "education": "BV705_streaming",    # 教育 - 甜美女声
    "business": "BV701_streaming",     # 商务 - 专业女声
    "child": "BV102_streaming",        # 儿童 - 童声
    "senior": "BV002_streaming"        # 老年 - 老年音色
}
```

### 场景切换示例
```bash
# 切换到工业场景音色
python3 voice_manager.py set $(python3 -c "from voice_config import voice_config; print(voice_config.get_recommended_voice('industrial'))")

# 或者在代码中
session.set_scenario_voice("industrial")
```

## 🧪 测试和演示

### 运行演示脚本
```bash
# 完整演示
python3 voice_demo.py

# 交互式演示
python3 voice_demo.py interactive
```

### 测试音色效果
```bash
# 测试单个音色
python3 voice_manager.py test BV700_streaming

# 测试所有女声音色
for voice in BV700_streaming BV705_streaming BV701_streaming; do
    echo "测试音色: $voice"
    python3 voice_manager.py test $voice
done
```

## 📋 配置管理

### 备份和恢复
```bash
# 创建备份
python3 voice_manager.py backup

# 查看备份文件
ls voice_config_backup_*.json

# 恢复特定备份
python3 voice_manager.py restore voice_config_backup_20250915_143022.json
```

### 配置文件结构
```json
{
  "speaker": "BV700_streaming",
  "audio_config": {
    "channel": 1,
    "format": "pcm",
    "sample_rate": 24000
  },
  "voice_params": {
    "speed_ratio": 1.0,
    "volume_ratio": 1.0,
    "pitch_ratio": 1.0
  }
}
```

## 🔧 高级自定义

### 添加新音色
在 `voice_config.py` 中添加新的音色定义：

```python
self.available_voices["NEW_VOICE_ID"] = {
    "name": "新音色名称",
    "gender": "female",  # 或 "male", "child", "senior"
    "style": "音色风格描述",
    "recommended_scenes": ["适用场景1", "适用场景2"]
}
```

### 自定义场景配置
```python
# 添加新场景
voice_config.scenario_voices["custom_scenario"] = "BV700_streaming"

# 创建场景专用配置
custom_config = voice_config.create_scenario_config(
    "custom_scenario", 
    {"speed": 1.3, "volume": 1.2, "pitch": 1.1}
)
```

### 程序化控制
```python
# 动态音色切换
def switch_voice_by_time():
    import datetime
    hour = datetime.datetime.now().hour
    
    if 6 <= hour < 12:
        return "BV705_streaming"  # 早晨 - 甜美女声
    elif 12 <= hour < 18:
        return "BV701_streaming"  # 下午 - 专业女声
    else:
        return "BV700_streaming"  # 晚上 - 温柔女声

# 根据用户偏好切换
def switch_voice_by_user(user_age, user_gender):
    if user_age < 12:
        return "BV102_streaming"  # 儿童用户
    elif user_age > 60:
        return "BV002_streaming"  # 老年用户
    elif user_gender == "male":
        return "BV406_streaming"  # 男性用户偏好
    else:
        return "BV700_streaming"  # 默认女声
```

## 📊 性能优化

### 音色缓存
系统会缓存音色配置，避免重复加载：

```python
# 预加载常用音色
common_voices = ["BV700_streaming", "BV406_streaming", "BV705_streaming"]
for voice_id in common_voices:
    voice_config.get_voice_info(voice_id)
```

### 批量配置
```python
# 批量设置多个参数
voice_settings = {
    "voice_id": "BV700_streaming",
    "speed": 1.1,
    "volume": 1.0,
    "pitch": 1.0
}

voice_config.set_voice(**voice_settings)
```

## ❓ 常见问题

**Q: 音色切换后没有生效？**
A: 确保调用了 `_apply_voice_config()` 方法，或者重启系统。

**Q: 如何恢复默认音色？**
A: 使用 `voice_config.reset_to_default()` 或设置为 `BV700_streaming`。

**Q: 支持自定义音色吗？**
A: 目前支持豆包API提供的预设音色，如需自定义需要联系服务提供商。

**Q: 音色参数调整范围是多少？**
A: 语速、音量、音调的调整范围都是 0.5-2.0，建议在 0.8-1.5 范围内调整。

**Q: 如何为不同用户设置不同音色？**
A: 可以根据用户ID创建个人配置文件，在用户登录时加载对应配置。

## 💡 最佳实践

1. **场景适配**: 根据使用环境选择合适的音色
2. **参数微调**: 根据实际效果微调语速、音量、音调
3. **用户偏好**: 考虑目标用户群体的特点
4. **一致性**: 在同一场景下保持音色的一致性
5. **测试验证**: 在实际环境中测试音色效果

---

通过这个音色配置系统，您可以让Dragon机器人在不同场景下使用最适合的声音，提供更好的用户体验！