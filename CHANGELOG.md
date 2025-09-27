# 更新日志 CHANGELOG

## 2025-09-28
### 新增
- 导航点文本触发 (point1~point5)：自动麦克风静音 -> 发送文本 -> TTS 播报 -> voice_end 恢复。
- 文本输入模式支持：发送时添加 dialog.extra.input_mod = "text"。
- 事件接口 EventInterface：统一 voice / command / navigation 回调注册与触发。
- 语音播放生命周期事件：voice_start / voice_end。

### 优化
- Prompt 配置精简：保留结构删除冗长内容，保持兼容。
- 机器人命令事件化：输出 cmd_1~cmd_6 便于上层消费。

### 说明
- 新增逻辑集中在 dragon_official_exact.py 与 realtime_dialog_client.chat_text_query。
- 旧脚本不依赖导航点事件时无需修改即可继续运行。

## 2025-09-10
- v2.0.0 知识库集成：加入本地文档检索与上下文增强。

## 早期版本
- v1.x 基础：语音识别、机器人控制、TTS、连续对话。
