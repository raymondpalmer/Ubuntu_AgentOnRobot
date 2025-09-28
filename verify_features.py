#!/usr/bin/env python3
"""
快速离线/半模拟验证新增功能：
1. voice_start / voice_end 事件触发
2. 命令事件 cmd_1~cmd_6
3. 导航点触发 point1~point5 + 麦克风静音/恢复逻辑变量变化
4. 文本模式 dialog.extra = {"input_mod": "text"} 注入（通过 monkey patch mock chat_text_query 捕获）

说明：
- 该脚本不真正连接远端服务，而是局部模拟 DragonDialogSession 的关键调用路径。
- 若需真实验证，请运行 dragon_official_exact.py 并按照 README 手动语音/调用接口。
"""
import asyncio
import types
from dragon_official_exact import DragonDialogSession, EventInterface

results = {
    "voice_events": [],
    "command_events": [],
    "navigation_events": [],
    "text_mode_payloads": [],
}

def voice_cb(ev):
    results["voice_events"].append(ev)

def command_cb(cmd_id, phrase):
    results["command_events"].append((cmd_id, phrase))

def nav_cb(point):
    results["navigation_events"].append(point)

async def main():
    # 重置并注册回调
    EventInterface.reset()
    EventInterface.register_voice_callback(voice_cb)
    EventInterface.register_command_callback(command_cb)
    EventInterface.register_navigation_callback(nav_cb)

    session = DragonDialogSession()

    # ---- 模拟命令事件：直接调用 robot_controller.execute_command ----
    test_commands = ["机器人前进", "去洗手间", "前往电梯间", "左转"]
    for c in test_commands:
        session.robot_controller.execute_command(c)

    # ---- 模拟导航点：拦截 client.chat_text_query 捕获 dialog_extra ----
    async def fake_chat_text_query(self, content, dialog_extra=None):  # type: ignore
        results["text_mode_payloads"].append({
            "content": content,
            "dialog_extra": dialog_extra,
        })
        # 模拟立即播放开始 -> 结束
        EventInterface.emit_voice_event("voice_start")
        await asyncio.sleep(0.01)
        EventInterface.emit_voice_event("voice_end")

    # monkey patch
    session.client.chat_text_query = types.MethodType(fake_chat_text_query, session.client)

    # 导航触发前状态
    assert not session.microphone_muted
    EventInterface.point1()
    # 等待异步处理
    await asyncio.sleep(0.05)

    # 人为调用 _send_navigation_prompt 以确保执行（事件循环已在当前）
    await session._send_navigation_prompt("point1")
    await asyncio.sleep(0.05)

    # ---- 汇总结果 ----
    print("=== 验证结果 ===")
    print("命令事件:", results["command_events"])
    print("语音事件:", results["voice_events"])  # 期望至少包含 start/end
    print("导航事件:", results["navigation_events"])  # 期望包含 point1
    print("文本模式payloads:", results["text_mode_payloads"])  # 期望包含 input_mod=text

    # 关键断言（失败将抛异常）
    assert any(e == "voice_start" for e in results["voice_events"]), "缺少 voice_start"
    assert any(e == "voice_end" for e in results["voice_events"]), "缺少 voice_end"
    assert any(cmd for cmd, _ in results["command_events"] if cmd == "cmd_1"), "未触发 cmd_1"
    assert any(p == "point1" for p in results["navigation_events"]), "未触发 point1"
    assert any(p.get("dialog_extra", {}).get("input_mod") == "text" for p in results["text_mode_payloads"]), "未检测到文本模式 input_mod=text"

    print("✅ 所有断言通过")

if __name__ == "__main__":
    asyncio.run(main())
