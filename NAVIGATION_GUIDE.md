# 导航点使用指南

## 🎯 概述
Dragon 机器人系统提供了 5 个预设导航点，用于中国电信人工智能展示中心的自动导览。每个导航点会触发特定的语音播报内容，播报结束后系统会自动重启以确保状态清洁。

## 📍 可用导航点

### Point 1 - 欢迎词和观影点引导
**触发方式：** `curl http://localhost:8080/point1`
**播报内容：** 欢迎各位领导，各位来宾莅临中国电信人工智能展示中心...

### Point 2 - 真实之境沙盘介绍  
**触发方式：** `curl http://localhost:8080/point2`
**播报内容：** 这边为真实之境，通过观看沙盘的短片...

### Point 3 - 数字人展区介绍
**触发方式：** `curl http://localhost:8080/point3`
**播报内容：** 各位领导下面请移步至我们的数字人展区...

### Point 4 - 全模态大模型基座介绍
**触发方式：** `curl http://localhost:8080/point4`
**播报内容：** 请各位领导向后转身。这边展示的是中国电信全自研的全模态...

### Point 5 - 智能家居展厅介绍
**触发方式：** `curl http://localhost:8080/point5`
**播报内容：** 请各位领导移步至我们的智能家居展厅...

## 🚀 快速开始

### 1. 启动系统
```bash
cd /path/to/AgentOnRobot-main
python3 dragon_official_exact.py
```

### 2. 等待系统就绪
看到以下提示表示系统已准备完毕：
```
🎤 基于中国电信星辰大模型驱动的机器人智能助理已准备就绪！
🌐 导航测试: ✅ 已启动 http://localhost:8080
```

### 3. 触发导航点
在另一个终端或通过网络请求：
```bash
# 触发 Point 1
curl http://localhost:8080/point1

# 触发其他导航点
curl http://localhost:8080/point2
curl http://localhost:8080/point3
curl http://localhost:8080/point4
curl http://localhost:8080/point5
```

## 🔄 系统行为流程

1. **接收请求** - HTTP 请求到达导航服务器
2. **进入导航模式** - 自动静音麦克风，切换到导航模式
3. **发送文本** - 将预设文本发送到 AI 模型
4. **语音播报** - AI 模型生成语音并播放
5. **静默检测** - 播放线程检测音频静默 ≥1 秒
6. **自动重启** - 检测到播报结束，1 秒后硬重启整个系统
7. **静音窗口** - 重启后前 8 秒完全静音，避免开场白
8. **恢复就绪** - 8 秒后系统恢复正常，可接受新的语音或导航请求

## 📊 状态监控

### 查看系统状态
```bash
curl http://localhost:8080/status
```
返回 JSON 格式的系统状态，包括：
- `dialog_mode`: 当前对话模式 (normal/navigation)
- `microphone_muted`: 麦克风是否静音
- `is_voice_playback_active`: 是否正在播放语音
- `navigation_queue_len`: 导航队列长度
- `last_navigation_send_age`: 最近导航发送时间
- `last_audio_packet_age`: 最近音频包时间

### 测试连接
```bash
curl http://localhost:8080/ping
```
发送轻量级探测请求，确认系统响应正常。

## ⚠️ 注意事项

### 系统重启行为
- **每次导航后都会重启**：这是设计行为，确保状态完全清洁
- **重启耗时约 3-5 秒**：包含进程重启 + 模型连接 + 音频初始化
- **8 秒静音期**：重启后不会立即播放开场白，给系统充分初始化时间

### 使用建议
1. **连续导航**：如需连续触发多个导航点，请在每次重启完成后再发送下一个请求
2. **状态确认**：可通过 `/status` 接口确认系统已恢复到 normal 模式
3. **网络延迟**：在网络环境较差时，适当增加请求间隔

### 故障排查
- **无响应**：检查系统是否正在重启中，等待重启完成
- **静音过长**：确认是否处于 8 秒静音窗口内
- **连接失败**：确认 8080 端口未被占用，系统正常启动

## 🛠️ 高级配置

### 环境变量
- `DRAGON_INITIAL_SPEAKER_MUTE_SEC`: 重启后静音秒数（默认 8）
- `DRAGON_NAV_AUDIO_FALLBACK_SEC`: 音频回退超时（默认 6）
- `DRAGON_DEBUG_AUDIO=1`: 启用音频调试日志

### 自定义导航文本
导航文本在 `dragon_official_exact.py` 的 `navigation_prompts` 字典中定义，可根据需要修改。

## 🔗 集成示例

### Python 集成
```python
import requests
import time

def trigger_navigation_tour():
    base_url = "http://localhost:8080"
    points = ["point1", "point2", "point3", "point4", "point5"]
    
    for point in points:
        print(f"正在播放 {point}...")
        response = requests.get(f"{base_url}/{point}")
        print(f"响应: {response.text}")
        
        # 等待播报完成和系统重启
        time.sleep(15)  # 根据实际播报时长调整
        
        # 检查系统是否就绪
        while True:
            try:
                status = requests.get(f"{base_url}/status").json()
                if status.get("dialog_mode") == "normal":
                    break
            except:
                pass
            time.sleep(1)

if __name__ == "__main__":
    trigger_navigation_tour()
```

### Shell 脚本集成
```bash
#!/bin/bash
# navigation_tour.sh

POINTS=("point1" "point2" "point3" "point4" "point5")
BASE_URL="http://localhost:8080"

for point in "${POINTS[@]}"; do
    echo "触发 $point..."
    curl "$BASE_URL/$point"
    
    echo "等待播报完成和重启..."
    sleep 15
    
    # 等待系统恢复
    while true; do
        if curl -s "$BASE_URL/status" | grep -q '"dialog_mode": "normal"'; then
            echo "系统已恢复，准备下一个导航点"
            break
        fi
        sleep 1
    done
done

echo "导航巡演完成！"
```

## 📞 支持

如遇问题，请检查：
1. 系统日志输出
2. HTTP 接口返回状态
3. 网络连接状况
4. 音频设备配置

更多技术细节请参考项目 README.md 和源码注释。