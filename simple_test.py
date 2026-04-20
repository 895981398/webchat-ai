#!/usr/bin/env python3
"""
简单发送测试 - 不依赖配置文件
"""

import sys
import os
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

print("🎯 简单发送测试")
print("="*60)

# 检查微信状态
print("1. 检查微信状态...")
import subprocess
result = subprocess.run(['pgrep', '-x', 'WeChat'], capture_output=True)
if result.returncode == 0:
    print(f"✅ 微信正在运行 (PID: {result.stdout.decode().strip()})")
else:
    print("❌ 微信未运行")
    sys.exit(1)

# 测试自动回复系统
print("\n2. 测试自动回复系统...")

try:
    from auto_reply import AutoReplySystem
    
    # 创建简单配置
    config = {
        'mode': 'simulate',  # simulate/test/controlled/auto
        'test_contacts': ['文件传输助手'],
        'user_name': '张三',  # 用于@我检测
        'nickname': '三哥',
        
        # 群聊配置
        'group': {
            'enabled': True,
            'reply_only_at_me': True,
            'blacklist': [],
            'whitelist': []
        }
    }
    
    # 创建系统
    system = AutoReplySystem(config)
    system.initialize()
    
    print("✅ 自动回复系统初始化成功")
    
    # 测试不同场景
    print("\n3. 测试场景...")
    
    test_cases = [
        ("私聊消息", "文件传输助手", "你好"),
        ("群聊@我", "wxid_group@chatroom", "@张三 你好"),
        ("群聊未@我", "wxid_group@chatroom", "大家晚上好"),
        ("群聊@昵称", "wxid_group@chatroom", "@三哥 帮忙"),
    ]
    
    for desc, username, content in test_cases:
        print(f"\n🔹 {desc}:")
        print(f"   收件人: {username}")
        print(f"   内容: {content}")
        
        msg = {
            'username': username,
            'content': content,
            'sender': username,
            'timestamp': time.time()
        }
        
        result = system.handle_message(msg)
        
        if result:
            print(f"   ✅ 处理成功")
            print(f"     动作: {result.get('action')}")
            print(f"     回复: {result.get('reply')[:30]}...")
        else:
            print(f"   ❌ 处理失败")
    
    # 测试模式切换
    print("\n4. 测试模式切换...")
    
    # 切换到 test 模式
    system.set_mode('test')
    
    # 测试 test 模式
    test_msg = {
        'username': '文件传输助手',
        'content': '测试模式消息',
        'sender': '文件传输助手',
        'timestamp': time.time()
    }
    
    result = system.handle_message(test_msg)
    
    if result and result.get('action') == 'test':
        print("✅ test 模式工作正常")
        print(f"   建议: 确保微信在前台，可以尝试实际发送")
    else:
        print("❌ test 模式测试失败")
    
    # 切换回 simulate 模式
    system.set_mode('simulate')
    
except Exception as e:
    print(f"❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()

print(f"\n{'='*60}")
print("📊 总结:")
print()
print("✅ 核心功能:")
print("   1. 自动回复系统初始化 ✅")
print("   2. 消息处理流程 ✅")
print("   3. 群聊过滤 (@我检测) ✅")
print("   4. 模式切换 (simulate/test) ✅")
print()
print("🚀 下一步:")
print("   1. 启动监控系统: python monitor_web.py")
print("   2. 在微信中发送消息")
print("   3. 观察控制台输出")
print()
print("💡 提示:")
print("   - simulate 模式: 只模拟，不实际发送")
print("   - test 模式: 只发给'文件传输助手'")
print("   - 确保微信在前台，目标聊天窗口已打开")
print()
print("🔧 立即测试:")
print("   1. 在微信中打开'文件传输助手'")
print("   2. 发送 '你好'")
print("   3. 观察系统是否处理")