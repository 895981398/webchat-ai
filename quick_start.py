#!/usr/bin/env python3
"""
快速启动测试 - 验证所有功能是否工作
"""

import os
import sys
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

print("🎯 快速启动测试")
print("="*60)
print()

# 1. 检查配置文件
print("1. 检查配置文件...")
config_file = "auto_reply_config.json"
if os.path.exists(config_file):
    print(f"✅ 配置文件存在: {config_file}")
    
    try:
        import json
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 检查模式

        if 'auto_reply' in config:
            mode = config['auto_reply'].get('mode', 'simulate')
            print(f"✅ 当前模式: {mode}")
        else:
            print("⚠️  配置格式不标准")
            
    except Exception as e:
        print(f"❌ 配置文件错误: {e}")
else:
    print("⚠️  配置文件不存在，将使用默认配置")

# 2. 检查 Python 环境
print("\n2. 检查 Python 环境...")
print(f"   Python版本: {sys.version.split()[0]}")
print(f"   工作目录: {os.getcwd()}")

# 3. 检查依赖
print("\n3. 检查依赖库...")

dependencies = ['sqlite3', 'hmac', 'hashlib', 'json', 'os', 'sys', 'time']
available = []

for dep in dependencies:
    try:
        __import__(dep)
        available.append((dep, "✅"))
    except:
        available.append((dep, "❌"))

for dep, status in available:
    print(f"   {dep}: {status}")

# 4. 检查微信状态
print("\n4. 检查微信状态...")
import subprocess

try:
    result = subprocess.run(['pgrep', '-x', 'WeChat'], capture_output=True, text=True)
    if result.returncode == 0:
        print(f"✅ 微信正在运行 (PID: {result.stdout.strip()})")
    else:
        print("⚠️  微信未运行")
        print("   提示: 如果未运行，启动脚本会自动打开微信")
except:
    print("❌ 无法检查微信状态")

# 5. 测试自动回复系统
print("\n5. 测试自动回复系统...")
try:
    from auto_reply import AutoReplySystem
    
    # 创建简单配置

    config = {
        'mode': 'simulate',
        'test_contacts': ['文件传输助手'],
        'user_name': '测试用户',
        'nickname': '测试昵称',
        'group': {
            'enabled': True,
            'reply_only_at_me': True
        }
    }
    
    system = AutoReplySystem(config)
    system.initialize()
    
    print("✅ 自动回复系统初始化成功")
    
    # 测试消息处理

    test_msg = {
        'username': '文件传输助手',
        'content': '测试消息',
        'sender': '文件传输助手',
        'timestamp': time.time()
    }
    
    result = system.handle_message(test_msg)
    
    if result:
        print(f"✅ 消息处理成功")
        print(f"   动作: {result.get('action')}")
        print(f"   回复: {result.get('reply', '')[:30]}...")
    else:
        print("❌ 消息处理失败")
    
except Exception as e:
    print(f"❌ 自动回复系统测试失败: {e}")

# 6. 检查脚本
print("\n6. 检查启动脚本...")
scripts = ['start_bot.sh', 'stop_bot.sh', 'run_bot.py']
for script in scripts:
    if os.path.exists(script):
        if os.access(script, os.X_OK):
            print(f"✅ {script}: 可执行")
        else:
            print(f"⚠️  {script}: 不可执行")
    else:
        print(f"❌ {script}: 不存在")

# 总结
print(f"\n{'='*60}")
print("📋 启动准备完成")
print("="*60)
print()
print("🚀 你现在可以:")
print()
print("  1. 使用脚本启动:")
print("     ./start_bot.sh")
print("     或者")
print("     python3 run_bot.py")
print()
print("  2. 手动启动:")
print("     python3 monitor_web.py")
print()
print("  3. 停止机器人:")
print("     ./stop_bot.sh")
print()
print("📱 访问Web界面:")
print("    http://localhost:5678")
print()
print("🔧 重要配置:")
print("    1. 在微信中打开'文件传输助手'聊天窗口")
print("    2. 确保微信在前台")
print("    3. 发送消息测试自动回复")
print()
print("💡 提示:")
print("    - 第一次运行可能需要授权")
print("    - 系统会自动激活微信窗口")
print("    - 日志保存在 logs/ 目录")
print()
print("🎯 立即启动:")
print("    在终端运行: ./start_bot.sh")
print("    然后按 Ctrl+C 停止")

# 检查端口占用

print(f"\n{'='*60}")
print("🔍 端口 5678 状态:")
try:
    result = subprocess.run(['lsof', '-ti:5678'], capture_output=True, text=True)
    if result.stdout.strip():
        print(f"❌ 端口被占用")
        print(f"   PID: {result.stdout.strip()}")
        print("   运行 ./stop_bot.sh 清理")
    else:
        print("✅ 端口可用")
except:
    print("⚠️  无法检查端口状态")