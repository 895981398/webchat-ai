#!/usr/bin/env python3
"""
快速检查现有系统状态
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(__file__))

print("🔍 快速系统状态检查")
print("="*50)

# 1. 检查 auto_reply 模块
print("1. auto_reply 模块检查:")
try:
    from auto_reply import AutoReplySystem
    
    # 测试配置
    test_config = {
        'mode': 'simulate',
        'test_contacts': ['文件传输助手']
    }
    
    # 创建实例
    print("   创建 AutoReplySystem 实例...")
    system = AutoReplySystem(test_config)
    
    # 初始化
    print("   初始化系统...")
    system.initialize()
    
    print(f"   ✅ 系统初始化成功")
    print(f"     当前模式: {system.mode}")
    
    # 测试消息处理
    test_msg = {
        'username': '文件传输助手',
        'content': '测试消息',
        'sender': '文件传输助手',
        'timestamp': 1234567890,
        'type': 1
    }
    
    print("   测试消息处理...")
    result = system.handle_message(test_msg)
    
    if result:
        print(f"   ✅ 消息处理成功")
        print(f"     动作: {result.get('action')}")
        print(f"     回复: {result.get('reply')}")
    else:
        print(f"   ⚠️ 消息无回复（可能安全策略）")
        
except Exception as e:
    print(f"   ❌ auto_reply 模块检查失败: {e}")
    import traceback
    traceback.print_exc()

print("\n2. 检查现有 sender 模块:")
try:
    from auto_reply.core.sender import WeChatSender
    
    # 创建实例
    sender_config = {
        'mode': 'simulate'
    }
    
    sender = WeChatSender(sender_config)
    
    print(f"   ✅ 发送器初始化成功")
    print(f"     当前模式: {sender.mode}")
    
    # 获取可用方法
    stats = sender.get_stats()
    print(f"     可用发送方法: {stats.get('send_methods', {})}")
    
    if 'airtest_stats' in stats:
        print(f"     Airtest 状态: {stats['airtest_stats']}")
    else:
        print(f"     Airtest 状态: 未启用")
        
except Exception as e:
    print(f"   ❌ 发送器检查失败: {e}")

print("\n3. 检查监控系统:")
try:
    import monitor_web
    
    print(f"   ✅ monitor_web.py 导入成功")
    
    # 检查全局变量
    if hasattr(monitor_web, 'AUTO_REPLY_ENABLED'):
        print(f"     AUTO_REPLY_ENABLED: {monitor_web.AUTO_REPLY_ENABLED}")
    else:
        print(f"     AUTO_REPLY_ENABLED: 未找到")
        
except Exception as e:
    print(f"   ❌ 监控系统检查失败: {e}")

print("\n4. 硬件检查:")
try:
    import pyautogui
    
    screen_width, screen_height = pyautogui.size()
    print(f"   ✅ 屏幕尺寸: {screen_width} x {screen_height}")
    
    # 检查微信是否运行
    import subprocess
    result = subprocess.run(['pgrep', '-x', 'WeChat'], capture_output=True)
    wechat_running = result.returncode == 0
    print(f"   💬 微信运行状态: {'✅ 运行中' if wechat_running else '❌ 未运行'}")
    
except Exception as e:
    print(f"   ❌ 硬件检查失败: {e}")

print("\n" + "="*50)
print("📋 总结:")
print("  如果看到 '✅' 表示模块正常工作")
print("  如果看到 '⚠️' 表示有警告但不影响基本功能")
print("  如果看到 '❌' 表示模块有问题需要修复")
print("\n🎯 下一步建议:")
print("  1. 先运行现有系统: python monitor_web.py")
print("  2. 在 Web UI (http://localhost:5678) 查看实时消息")
print("  3. 测试自动回复: 发送消息到 '文件传输助手'")
print("  4. 观察控制台输出，确认功能正常")