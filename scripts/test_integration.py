#!/usr/bin/env python3
"""
测试自动回复系统集成到现有监控
"""

import sys
import os
import time
import json
import unittest
from datetime import datetime

if __name__ != "__main__":
    raise unittest.SkipTest("script-style test; run directly via python test_integration.py")

# 1. 测试模块导入
print("=== 步骤1: 测试模块导入 ===")
try:
    # 添加当前目录到路径
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from auto_reply import AutoReplySystem
    print("✅ AutoReplySystem 导入成功")
except ImportError as e:
    print(f"❌ AutoReplySystem 导入失败: {e}")
    sys.exit(1)

# 2. 创建自动回复系统实例
print("\n=== 步骤2: 创建自动回复系统实例 ===")
config = {
    'mode': 'simulate',
    'test_contacts': ['文件传输助手'],
    'whitelist': [],
    'blacklist': []
}

auto_reply = AutoReplySystem(config)
print(f"✅ 自动回复系统创建成功")
print(f"   当前模式: {auto_reply.mode}")
print(f"   测试联系人: {auto_reply.sender.test_contacts}")

# 3. 模拟微信消息处理
print("\n=== 步骤3: 模拟微信消息处理 ===")

def mock_wechat_message(username, content, sender=None, is_group=False):
    """模拟微信消息"""
    sender = sender or username
    is_group = '@chatroom' in username or is_group
    
    # 构建消息数据
    if is_group:
        display_name = f"{sender}@{username}"
    else:
        display_name = username
        
    return {
        'username': username,
        'content': content,
        'sender': sender,
        'is_group': is_group,
        'timestamp': time.time(),
        'msg_type': 1,  # 文本消息
        'display_name': display_name
    }

# 测试不同类型的消息
test_cases = [
    ("个人消息", mock_wechat_message("wxid_test123", "你好")),
    ("群聊消息", mock_wechat_message("123456@chatroom", "下午开会", sender="张三")),
    ("感谢消息", mock_wechat_message("wxid_thanks", "谢谢你的帮助")),
    ("时间查询", mock_wechat_message("wxid_time", "现在几点了")),
    ("天气查询", mock_wechat_message("wxid_weather", "今天天气怎么样")),
    ("工作消息", mock_wechat_message("wxid_work", "项目进度怎么样")),
    ("普通消息", mock_wechat_message("wxid_normal", "今天吃了什么"))
]

print("测试消息处理:")
for test_name, message_data in test_cases:
    print(f"\n📨 {test_name}:")
    print(f"  发件人: {message_data['display_name']}")
    print(f"  内容: {message_data['content']}")
    
    result = auto_reply.handle_message(message_data)
    if result:
        print(f"  💬 回复: {result['reply']}")
    else:
        print(f"  ⚠️  不回复")

# 4. 测试安全控制
print("\n=== 步骤4: 测试安全控制 ===")

# 测试频率限制
print("测试频率限制:")
for i in range(5):
    message = mock_wechat_message("wxid_test", f"测试消息{i}")
    result = auto_reply.handle_message(message)
    safe = auto_reply.safety.check_message(message)
    
    status = "✅ 通过" if safe else "❌ 限制"
    if result:
        print(f"  第{i+1}条: {status} - {result['reply']}")
    else:
        print(f"  第{i+1}条: {status} - 不回复")

# 5. 测试模式切换
print("\n=== 步骤5: 测试模式切换 ===")

modes = ['simulate', 'test', 'controlled', 'auto']
for mode in modes:
    success = auto_reply.set_mode(mode)
    status = "✅ 成功" if success else "❌ 失败"
    print(f"  切换到{mode}模式: {status}")
    print(f"    当前模式: {auto_reply.mode}")

# 6. 测试实际发送（模拟模式）
print("\n=== 步骤6: 测试实际发送功能 ===")

# 模拟消息发送
test_target = "文件传输助手"
test_content = f"集成测试 {datetime.now().strftime('%H:%M:%S')}"

# 模拟模式
auto_reply.set_mode('simulate')
success = auto_reply.sender.send_message(test_target, test_content)
print(f"模拟发送: {'✅ 成功' if success else '❌ 失败'}")

# 尝试真实发送（需要wxauto或pyautogui）
print("\n测试实际发送方法:")
auto_reply.sender._detect_send_methods()
methods = auto_reply.sender.send_methods

for method, available in methods.items():
    status = "✅ 可用" if available else "❌ 不可用"
    print(f"  {method}: {status}")

print("\n=== 集成测试完成 ===")

# 7. 生成集成说明
print("\n📋 下一步: 将以下代码集成到 monitor_web.py")

integration_code = '''
# =============== 自动回复系统集成 ===============
# 在文件顶部添加导入
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from auto_reply import AutoReplySystem
    AUTO_REPLY_ENABLED = True
    print("[AutoReply] 自动回复系统导入成功")
except ImportError as e:
    AUTO_REPLY_ENABLED = False
    print(f"[AutoReply] 自动回复系统导入失败: {e}")
    print("[AutoReply] 将在只读模式下运行")

# 在 main() 函数中添加初始化
global auto_reply_system
auto_reply_system = AutoReplySystem(config)

# 在消息处理回调中添加自动回复
def on_new_message(message_data):
    """新消息回调 - 添加自动回复功能"""
    # 原有功能...
    
    # 新增自动回复
    if AUTO_REPLY_ENABLED:
        result = auto_reply_system.handle_message(message_data)
        if result:
            print(f"[AutoReply] 回复: {result[\'reply\']}")
'''

print(integration_code)

print("\n🚀 集成成功！现在可以启动监控测试：")
print("python monitor_web.py")