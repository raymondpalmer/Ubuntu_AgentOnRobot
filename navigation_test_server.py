#!/usr/bin/env python3
"""
导航点测试服务器
在Dragon系统运行时提供HTTP接口来触发导航点

使用方法：
1. 将此代码集成到Dragon系统中，启动HTTP服务器
2. 通过HTTP GET请求触发导航点：
   curl http://localhost:8080/point1
   curl http://localhost:8080/point2
   等等...
"""

import asyncio
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import time
import urllib.parse

class NavigationTestHandler(BaseHTTPRequestHandler):
    """处理导航测试请求的HTTP处理器"""
    
    def __init__(self, dragon_session, *args, **kwargs):
        self.dragon_session = dragon_session
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """处理GET请求"""
        try:
            # 解析URL路径
            path = self.path.strip('/')
            
            if path == '':
                # 根路径，显示可用的导航点
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                
                html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Dragon导航点测试</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .nav-button { 
            display: inline-block; 
            padding: 10px 20px; 
            margin: 10px; 
            background: #007bff; 
            color: white; 
            text-decoration: none; 
            border-radius: 5px; 
        }
        .nav-button:hover { background: #0056b3; }
    </style>
</head>
<body>
    <h1>🤖 Dragon导航点测试</h1>
    <p>点击按钮触发对应的导航点：</p>
    
    <a href="/point1" class="nav-button">Point 1 - 欢迎词和观影点引导</a><br>
    <a href="/point2" class="nav-button">Point 2 - 真实之境沙盘介绍</a><br>
    <a href="/point3" class="nav-button">Point 3 - 数字人展区介绍</a><br>
    <a href="/point4" class="nav-button">Point 4 - 全模态大模型基座介绍</a><br>
    <a href="/point5" class="nav-button">Point 5 - 智能家居展厅介绍</a><br>
    
    <h2>命令行测试</h2>
    <pre>
curl http://localhost:8080/point1
curl http://localhost:8080/point2
curl http://localhost:8080/point3
curl http://localhost:8080/point4
curl http://localhost:8080/point5
    </pre>
</body>
</html>
                """
                self.wfile.write(html.encode('utf-8'))
                return
            
            elif path == 'status':
                # 返回当前 Dragon 会话关键状态
                st = {}
                sess = self.dragon_session
                if sess:
                    attrs = [
                        'dialog_mode','microphone_muted','mic_muted_due_to_navigation','is_voice_playback_active',
                        'is_user_querying','pending_navigation_point','is_recording','is_running'
                    ]
                    for a in attrs:
                        st[a] = getattr(sess,a,None)
                    # 导航队列长度
                    q_len = None
                    try:
                        if hasattr(sess,'navigation_queue'):
                            q_len = sess.navigation_queue.qsize()
                    except Exception:
                        pass
                    st['navigation_queue_len'] = q_len
                    # 最近导航发送与最近音频包时间差
                    import time
                    now = time.time()
                    st['last_navigation_send_age'] = round(now - getattr(sess,'last_navigation_send_time',0.0),2)
                    st['last_audio_packet_age'] = round(now - getattr(sess,'last_audio_packet_time',0.0),2)
                self.send_response(200)
                self.send_header('Content-type','application/json; charset=utf-8')
                self.end_headers()
                import json
                self.wfile.write(json.dumps(st,ensure_ascii=False,indent=2).encode('utf-8'))
                return
            elif path in ['point1', 'point2', 'point3', 'point4', 'point5','ping']:
                # 触发导航点
                if path == 'ping':
                    # 会话活跃探测：发送一个空文本TTS或轻量请求
                    if self.dragon_session and hasattr(self.dragon_session,'client'):
                        try:
                            # 只做一个轻量标记，不触发导航模式
                            asyncio.run_coroutine_threadsafe(
                                self.dragon_session.client.chat_text_query("."),
                                self.dragon_session.loop
                            )
                            self.send_response(200)
                            self.send_header('Content-type','text/plain; charset=utf-8')
                            self.end_headers()
                            self.wfile.write("✅ ping 已发送 (.)".encode('utf-8'))
                        except Exception as e:
                            self.send_response(500)
                            self.send_header('Content-type','text/plain; charset=utf-8')
                            self.end_headers()
                            self.wfile.write(f"❌ ping 失败: {e}".encode('utf-8'))
                    else:
                        self.send_response(500)
                        self.send_header('Content-type','text/plain; charset=utf-8')
                        self.end_headers()
                        self.wfile.write("❌ 会话不可用，无法ping".encode('utf-8'))
                    return
                print(f"🌐 HTTP请求触发导航点: {path}")
                if self.dragon_session:
                    self.dragon_session.trigger_navigation_point(path)
                    self.send_response(200)
                    self.send_header('Content-type', 'text/plain; charset=utf-8')
                    self.end_headers()
                    self.wfile.write(f"✅ 导航点 {path} 已触发".encode('utf-8'))
                else:
                    self.send_response(500)
                    self.send_header('Content-type', 'text/plain; charset=utf-8')
                    self.end_headers()
                    self.wfile.write("❌ Dragon系统未连接".encode('utf-8'))
            
            else:
                # 无效路径
                self.send_response(404)
                self.send_header('Content-type', 'text/plain; charset=utf-8')
                self.end_headers()
                self.wfile.write("❌ 无效的导航点".encode('utf-8'))
                
        except Exception as e:
            print(f"❌ HTTP处理错误: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write(f"❌ 服务器错误: {str(e)}".encode('utf-8'))
    
    def log_message(self, format, *args):
        """自定义日志格式"""
        print(f"🌐 HTTP: {format % args}")


class NavigationTestServer:
    """导航测试服务器"""
    
    def __init__(self, dragon_session, port=8080):
        self.dragon_session = dragon_session
        self.port = port
        self.server = None
        self.server_thread = None
        self.running = False
    
    def start(self):
        """启动HTTP服务器"""
        try:
            # 创建处理器工厂函数
            def handler_factory(*args, **kwargs):
                return NavigationTestHandler(self.dragon_session, *args, **kwargs)
            
            # 创建HTTP服务器
            self.server = HTTPServer(('localhost', self.port), handler_factory)
            
            # 在单独线程中运行服务器
            self.server_thread = threading.Thread(target=self._run_server)
            self.server_thread.daemon = True
            self.running = True
            self.server_thread.start()
            
            print(f"🌐 导航测试服务器已启动: http://localhost:{self.port}")
            print(f"🎯 可以通过浏览器或curl命令触发导航点")
            print(f"   例如: curl http://localhost:{self.port}/point1")
            
        except Exception as e:
            print(f"❌ 导航测试服务器启动失败: {e}")
    
    def _run_server(self):
        """运行HTTP服务器"""
        try:
            while self.running:
                self.server.handle_request()
        except Exception as e:
            print(f"❌ 导航测试服务器运行错误: {e}")
    
    def stop(self):
        """停止HTTP服务器"""
        self.running = False
        if self.server:
            self.server.shutdown()
            print("🌐 导航测试服务器已停止")


def create_simple_test_client():
    """创建简单的测试客户端"""
    import requests
    
    base_url = "http://localhost:8080"
    
    print("🎯 Dragon导航点测试客户端")
    print("=" * 50)
    
    while True:
        try:
            print("\n📋 可用的导航点:")
            print("   1 - point1: 欢迎词和观影点引导")
            print("   2 - point2: 真实之境沙盘介绍")
            print("   3 - point3: 数字人展区介绍")
            print("   4 - point4: 全模态大模型基座介绍")
            print("   5 - point5: 智能家居展厅介绍")
            print("   0 - 退出")
            
            choice = input("\n请选择要测试的导航点 (1-5, 0退出): ").strip()
            
            if choice == "0":
                print("👋 退出测试")
                break
            elif choice in ["1", "2", "3", "4", "5"]:
                point = f"point{choice}"
                print(f"🎯 触发 {point}...")
                
                try:
                    response = requests.get(f"{base_url}/{point}", timeout=5)
                    if response.status_code == 200:
                        print(f"✅ {response.text}")
                    else:
                        print(f"❌ 错误 {response.status_code}: {response.text}")
                except requests.exceptions.ConnectionError:
                    print(f"❌ 无法连接到导航测试服务器 ({base_url})")
                    print("请确保Dragon系统正在运行且启用了导航测试服务器")
                except Exception as e:
                    print(f"❌ 请求失败: {e}")
                    
            else:
                print("❌ 无效选择，请输入 1-5 或 0")
                
        except KeyboardInterrupt:
            print("\n👋 用户中断，退出测试")
            break

if __name__ == "__main__":
    # 如果直接运行此脚本，启动测试客户端
    print("🔗 尝试连接到Dragon导航测试服务器...")
    create_simple_test_client()