#!/usr/bin/env python3
"""
快速测试自动回复模块
"""

import sys
import os

# 测试导入
print("1. 测试导入auto_reply模块...")
try:
    sys.path.append('.')
    from auto_reply import AutoReplySystem
    print("✅ 导入成功")
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    exit(1)

# 测试创建实例
print("\n2. 测试创建AutoReplySystem实例...")
try:
    config = {
        'mode': 'simulate',
        'test_contacts': ['文件传输助手']
    }
    system = AutoReplySystem(config)
    print(f"✅ 创建成功")
    print(f"   模式: {system.mode}")
except Exception as e:
    print(f"❌ 创建失败: {e}")
    exit(1)

# 测试消息处理
print("\n3. 测试消息处理...")
test_messages = [
    {'username': 'wxid_test', 'content': '你好', 'sender': 'wxid_test'},
    {'username': '123@chatroom', 'content': '谢谢', 'sender': '张三'},
]

for msg in test_messages:
    result = system.handle_message(msg)
    if result:
        print(f"  ✅ 输入: '{msg['content']}' -> 回复: '{result.get('reply')}'")
    else:
        print(f"  ⚠️  输入: '{msg['content']}' -> 不回复")

print("\n🎉 基本测试通过！")
print("\n下一步:")
print("1. 启动监控: python monitor_web.py")
print("2. 发送微信消息测试")
print("3. 确保控制台显示 '[AutoReply] 生成回复: ...'")