#!/usr/bin/env python3
"""
微信实时消息监听器 - Web UI (SSE推送 + mtime检测) - 修复版
带自动回复系统，设置为test模式
"""

import sys
import os

# 修复文件路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 先读取原文件内容
with open('monitor_web.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 找到并替换自动回复系统配置
old_config = '''        auto_reply_system = AutoReplySystem({
            "mode": "simulate",
            "test_contacts": ["文件传输助手"],
            "whitelist": [],
            "blacklist": []
        })'''

new_config = '''        auto_reply_system = AutoReplySystem({
            "mode": "test",
            "test_contacts": ["王者"],
            "whitelist": [],
            "blacklist": ["文件传输助手"]
        })'''

if old_config in content:
    new_content = content.replace(old_config, new_config)
    
    # 保存修复版本
    with open('monitor_web_fixed.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ 配置修复完成!")
    print("文件已保存为: monitor_web_fixed.py")
    print("\n新的配置:")
    print("- 模式: test (真实发送)")
    print("- 测试联系人: 王者")
    print("- 黑名单: 文件传输助手 (避免给自己回复)")
    print("\n运行命令: python3 monitor_web_fixed.py")
else:
    print("❌ 未找到原始配置")
    print("请手动修改配置: 将 'simulate' 改为 'test'，并将测试联系人改为 '王者'")