#!/usr/bin/env python3
"""
导航点测试客户端 - 简单命令行工具

用于测试Dragon系统的HTTP导航接口
"""

import requests
import time
import sys

def test_navigation_points():
    """测试所有导航点"""
    base_url = "http://localhost:8080"
    
    points = {
        "point1": "欢迎词和观影点引导",
        "point2": "真实之境沙盘介绍", 
        "point3": "数字人展区介绍",
        "point4": "全模态大模型基座介绍",
        "point5": "智能家居展厅介绍"
    }
    
    print("🎯 Dragon导航点测试工具")
    print("=" * 50)
    
    # 测试服务器连接
    try:
        response = requests.get(f"{base_url}/", timeout=2)
        print("✅ 导航测试服务器连接成功")
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到导航测试服务器")
        print("请确保Dragon系统正在运行并启用了导航测试服务器")
        return False
    except Exception as e:
        print(f"❌ 连接错误: {e}")
        return False
    
    if len(sys.argv) > 1:
        # 测试指定的点
        point = sys.argv[1]
        if point in points:
            print(f"\n🎯 测试单个导航点: {point}")
            test_single_point(base_url, point, points[point])
        else:
            print(f"❌ 无效的导航点: {point}")
            print(f"可用的导航点: {list(points.keys())}")
    else:
        # 交互式测试所有点
        while True:
            print(f"\n📋 可用的导航点:")
            for i, (point, desc) in enumerate(points.items(), 1):
                print(f"   {i} - {point}: {desc}")
            print("   0 - 退出")
            
            try:
                choice = input("\n请选择要测试的导航点 (1-5, 0退出): ").strip()
                
                if choice == "0":
                    print("👋 退出测试")
                    break
                elif choice in ["1", "2", "3", "4", "5"]:
                    point = f"point{choice}"
                    desc = points[point]
                    test_single_point(base_url, point, desc)
                else:
                    print("❌ 无效选择，请输入 1-5 或 0")
                    
            except KeyboardInterrupt:
                print("\n👋 用户中断，退出测试")
                break
    
    return True

def test_single_point(base_url, point, description):
    """测试单个导航点"""
    print(f"\n🎯 触发导航点: {point} - {description}")
    print("⏳ 发送HTTP请求...")
    
    try:
        response = requests.get(f"{base_url}/{point}", timeout=10)
        if response.status_code == 200:
            print(f"✅ 请求成功: {response.text}")
            print("🔊 请注意听Dragon系统的语音回复...")
            time.sleep(2)  # 给一点时间让用户听到响应
        else:
            print(f"❌ 请求失败 {response.status_code}: {response.text}")
    except requests.exceptions.Timeout:
        print("⏰ 请求超时，但导航事件可能已触发")
    except Exception as e:
        print(f"❌ 请求异常: {e}")

if __name__ == "__main__":
    test_navigation_points()