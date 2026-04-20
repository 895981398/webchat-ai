#!/usr/bin/env python3
"""
实际发送测试 - 测试能否发送消息到微信
"""

import sys
import os
import time
import unittest
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.dirname(__file__))

if __name__ != "__main__":
    raise unittest.SkipTest("script-style test; run directly via python test_actual_send.py")

print("🎯 实际发送测试")
print("="*60)
print("时间:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
print()

# 检查微信状态
print("1. 检查微信状态...")
import subprocess
result = subprocess.run(['pgrep', '-x', 'WeChat'], capture_output=True)
if result.returncode == 0:
    print(f"✅ 微信正在运行 (PID: {result.stdout.decode().strip()})")
else:
    print("❌ 微信未运行")
    sys.exit(1)

# 导入模块
print("\n2. 导入发送模块...")
try:
    from auto_reply.core.sender import WeChatSender
    print("✅ WeChatSender 导入成功")
except Exception as e:
    print(f"❌ WeChatSender 导入失败: {e}")
    sys.exit(1)

# 测试不同模式
modes = ['simulate', 'test', 'controlled', 'auto']

for mode in modes:
    print(f"\n{'='*60}")
    print(f"测试模式: {mode}")
    print(f"{'='*60}")
    
    # 创建配置
    config = {
        'mode': mode,
        'test_contacts': ['文件传输助手'],
        'whitelist': ['文件传输助手'],
        'blacklist': []
    }
    
    try:
        # 创建发送器
        sender = WeChatSender(config)
        
        # 获取发送器状态
        stats = sender.get_stats()
        print(f"发送器状态:")
        print(f"  当前模式: {stats['current_mode']}")
        print(f"  可用方法: {stats['send_methods']}")
        
        # 测试发送消息
        test_contact = '文件传输助手'
        test_message = f"测试消息 - {mode}模式 - {datetime.now().strftime('%H:%M:%S')}"
        
        print(f"\n准备发送:")
        print(f"  收件人: {test_contact}")
        print(f"  内容: {test_message}")
        
        # 实际发送
        success = sender.send_message(test_contact, test_message, mode=mode)
        
        if success:
            print(f"✅ 发送成功!")
        else:
            print(f"❌ 发送失败")
            
        # 等待一下
        time.sleep(2)
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

print(f"\n{'='*60}")
print("🎯 测试完成总结")
print(f"{'='*60}")
print("\n🔧 当前推荐配置:")
print('''
{
  "mode": "test",  # 测试模式，只发给测试联系人
  "test_contacts": ["文件传输助手"],
  "whitelist": ["文件传输助手"],
  "blacklist": [],
  
  "group": {
    "enabled": true,
    "reply_only_at_me": true,
    "blacklist": [],
    "whitelist": []
  }
}
''')

print("\n🚀 下一步:")
print("1. 编辑 auto_reply_config.json 设置模式为 'test'")
print("2. 启动监控系统: python monitor_web.py")
print("3. 在微信中给'文件传输助手'发送消息")
print("4. 观察自动回复是否工作")
print("\n💡 提示: 在 test 模式下，只会回复给'文件传输助手'，不会影响其他联系人")