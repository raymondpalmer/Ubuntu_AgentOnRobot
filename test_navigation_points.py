#!/usr/bin/env python3
"""
导航点测试脚本（升级版）
================================
核心问题回避：直接 import dragon_official_exact 会生成新的 EventInterface 回调集合，
与已经运行中的 Dragon 进程（语音会话）隔离 => 导致触发 pointX 实际没人接收到。

本改造：
1. 默认采用 HTTP 触发模式（依赖运行中的 dragon_official_exact 已启动并内置 navigation_test_server）
2. 保留旧的本地 import 触发作为 --local 回退（仅在同一进程内调试时使用）
3. 增加 --point 指定单个点测试；--interval 自定义间隔；--fast 跳过确认
4. 自动检测 HTTP 服务是否可用；失败再提示是否回退本地模式

使用示例：
    python3 test_navigation_points.py --http --point point1
    python3 test_navigation_points.py --http            # 顺序播放全部
    python3 test_navigation_points.py --local --single  # 回到旧的交互模式（不推荐常规使用）
"""

import time
import sys
import os
import argparse
from typing import List

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("⚠️ 未安装 requests，HTTP 模式不可用（pip install requests）")

# 添加当前目录到路径，以便导入EventInterface
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

HTTP_BASE = "http://localhost:8080"

NAV_POINTS = [
    ("point1", "欢迎词和观影点引导"),
    ("point2", "真实之境沙盘介绍"),
    ("point3", "数字人展区介绍"),
    ("point4", "全模态大模型基座介绍"),
    ("point5", "智能家居展厅介绍"),
]

def trigger_via_http(point: str, timeout: float = 6.0) -> bool:
    if not REQUESTS_AVAILABLE:
        print("❌ requests 不可用，无法HTTP触发")
        return False
    try:
        url = f"{HTTP_BASE}/{point}"
        r = requests.get(url, timeout=timeout)
        if r.status_code == 200:
            print(f"✅ HTTP触发成功: {r.text}")
            return True
        else:
            print(f"❌ HTTP触发失败: {r.status_code} {r.text}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ 无法连接到 {HTTP_BASE}，Dragon 主程序可能未启动或未启用导航服务器")
        return False
    except requests.exceptions.Timeout:
        print("⏰ HTTP请求超时（可能仍然已被接收，注意观察主程序日志）")
        return True
    except Exception as e:
        print(f"❌ HTTP异常: {e}")
        return False

def check_http_server() -> bool:
    if not REQUESTS_AVAILABLE:
        return False
    try:
        requests.get(HTTP_BASE + "/", timeout=1.5)
        return True
    except Exception:
        return False

def test_navigation_points(http: bool, interval: int, fast: bool):
    """测试所有导航点（支持HTTP / 本地两种模式）"""
    
    # 选择模式
    local_mode = not http
    if http:
        if check_http_server():
            print(f"🌐 HTTP模式：将通过 {HTTP_BASE}/pointX 触发")
        else:
            print("⚠️ 未检测到HTTP服务器，尝试回退本地模式 (import EventInterface)")
            local_mode = True

    if local_mode:
        try:
            from dragon_official_exact import EventInterface
            print("✅ 本地模式：EventInterface导入成功 (注意：需要与语音会话同进程才有效)")
        except ImportError as e:
            print(f"❌ 本地模式失败：无法导入 EventInterface: {e}")
            print("👉 请启动 dragon_official_exact.py 并使用 --http 模式")
            return
    
    print("🎯 导航点测试脚本启动")
    print("📋 测试计划:")
    print("   - point1: 欢迎词和观影点引导")
    print("   - point2: 真实之境沙盘介绍") 
    print("   - point3: 数字人展区介绍")
    print("   - point4: 全模态大模型基座介绍")
    print("   - point5: 智能家居展厅介绍")
    print("=" * 50)
    
    # 等待用户确认Dragon系统已启动
    input("🔔 请确保Dragon系统已经启动并正常运行，然后按Enter开始测试...")
    
    # 测试所有导航点
    for i, (point, description) in enumerate(NAV_POINTS, 1):
        print(f"\n🎯 [{i}/5] 触发 {point}: {description}")
        print(f"⏰ 时间: {time.strftime('%H:%M:%S')}")
        
        try:
            ok = False
            if http and not local_mode:
                ok = trigger_via_http(point)
            else:
                # 本地模式调用（不推荐除非确认同进程）
                from dragon_official_exact import EventInterface
                getattr(EventInterface, point)()
                ok = True
            if ok:
                print(f"✅ {point} 触发成功")
            else:
                print(f"❌ {point} 触发失败（模式={'HTTP' if http else 'LOCAL'}）")
            
            # 如果不是最后一个点，等待30秒
            if i < len(NAV_POINTS):
                if fast:
                    time.sleep(1)
                else:
                    print(f"⏳ 等待{interval}秒后继续下一个导航点...")
                    remain = interval
                    step = 5 if interval >= 10 else 1
                    while remain > 0:
                        print(f"   剩余 {remain} 秒...")
                        sleep_t = step if remain >= step else remain
                        time.sleep(sleep_t)
                        remain -= sleep_t
            else:
                print("🎉 所有导航点测试完成！")
                
        except Exception as e:
            print(f"❌ {point} 触发失败: {e}")
            continue

def test_single_point():
    """测试单个导航点（交互模式）"""
    
    try:
        from dragon_official_exact import EventInterface
        print("✅ EventInterface导入成功")
        print(f"📊 当前注册的导航回调数量: {len(EventInterface._navigation_callbacks)}")
    except ImportError as e:
        print(f"❌ 无法导入EventInterface: {e}")
        return
    
    print("🎯 单点测试模式")
    print("📋 可用的导航点:")
    print("   1 - point1: 欢迎词和观影点引导")
    print("   2 - point2: 真实之境沙盘介绍")
    print("   3 - point3: 数字人展区介绍") 
    print("   4 - point4: 全模态大模型基座介绍")
    print("   5 - point5: 智能家居展厅介绍")
    print("   0 - 退出")
    
    while True:
        try:
            choice = input("\n请选择要测试的导航点 (1-5, 0退出): ").strip()
            
            if choice == "0":
                print("👋 退出测试")
                break
            elif choice == "1":
                print("🎯 触发 point1...")
                print(f"📊 触发前回调数量: {len(EventInterface._navigation_callbacks)}")
                EventInterface.point1()
                print("✅ point1 触发完成")
                print("⏳ 等待2秒观察效果...")
                time.sleep(2)
            elif choice == "2":
                print("🎯 触发 point2...")
                EventInterface.point2()
                print("✅ point2 触发成功")
            elif choice == "3":
                print("🎯 触发 point3...")
                EventInterface.point3()
                print("✅ point3 触发成功")
            elif choice == "4":
                print("🎯 触发 point4...")
                EventInterface.point4()
                print("✅ point4 触发成功")
            elif choice == "5":
                print("🎯 触发 point5...")
                EventInterface.point5()
                print("✅ point5 触发成功")
            else:
                print("❌ 无效选择，请输入 1-5 或 0")
                
        except KeyboardInterrupt:
            print("\n👋 用户中断，退出测试")
            break
        except Exception as e:
            print(f"❌ 触发失败: {e}")

def parse_args():
    p = argparse.ArgumentParser(description="Dragon 导航点测试")
    p.add_argument("--http", action="store_true", help="使用HTTP方式触发 (推荐)")
    p.add_argument("--local", action="store_true", help="强制使用本地 EventInterface 触发")
    p.add_argument("--point", choices=[p for p, _ in NAV_POINTS], help="仅触发单个导航点")
    p.add_argument("--interval", type=int, default=30, help="自动模式导航点间隔秒 (默认30)")
    p.add_argument("--fast", action="store_true", help="快速模式：间隔缩短为1秒")
    p.add_argument("--single", action="store_true", help="进入旧的交互单点测试界面")
    return p.parse_args()

def main():
    args = parse_args()
    print("🤖 Dragon导航点测试工具 (增强版)")
    print("=" * 60)

    # 交互旧模式
    if args.single and not args.point:
        test_single_point()
        return

    # 单点触发直接执行
    if args.point:
        # 复用批量逻辑但只保留一个点
        global NAV_POINTS
        NAV_POINTS = [(p, d) for (p, d) in NAV_POINTS if p == args.point]
        test_navigation_points(http=args.http and not args.local, interval=args.interval, fast=args.fast)
        return

    # 默认：批量触发全部
    # 如果未显式指定模式，默认尝试HTTP
    prefer_http = args.http or (not args.local)
    test_navigation_points(http=prefer_http, interval=args.interval, fast=args.fast)

if __name__ == "__main__":
    main()