#!/usr/bin/env python3
"""
自动窗口管理测试 - 自动打开微信、调整窗口大小、确保前台
"""

import sys
import os
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

print("🪟 自动窗口管理测试")
print("="*60)
print("时间:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
print()

# 检查当前系统
print("1. 系统检测...")
import platform
current_platform = platform.system()
print(f"   操作系统: {current_platform}")
print(f"   系统版本: {platform.version()}")

# 检查微信状态
print("\n2. 微信状态检查...")
import subprocess
result = subprocess.run(['pgrep', '-x', 'WeChat'], capture_output=True, text=True)

if result.returncode == 0:
    wechat_pid = result.stdout.strip()
    print(f"✅ 微信正在运行 (PID: {wechat_pid})")
    wechat_running = True
else:
    print("❌ 微信未运行")
    wechat_running = False

# 导入窗口管理器
print("\n3. 加载窗口管理器...")
try:
    from auto_reply.core.window_manager import WeChatWindowManager
    print("✅ 窗口管理器导入成功")
    
    # 创建配置
    config = {
        'window': {
            'auto_activate': True,
            'ensure_frontmost': True,
            'adjust_size': True,
            'min_width': 800,
            'min_height': 600,
            'optimal_width': 1200,
            'optimal_height': 800,
            'check_interval': 1.0,
            'max_retry': 3
        }
    }
    
    # 创建窗口管理器
    window_manager = WeChatWindowManager(config)
    print("✅ 窗口管理器初始化成功")
    
    # 测试微信运行状态
    if not wechat_running:
        print("\n🔄 尝试自动启动微信...")
        success = window_manager.launch_wechat()
        if success:
            print("✅ 微信已成功启动")
            time.sleep(3)  # 等待微信完全启动
        else:
            print("❌ 微信启动失败，无法继续测试")
            sys.exit(1)
    
    # 测试窗口激活
    print("\n4. 测试窗口激活...")
    print("   ⚠️ 注意: 观察微信窗口是否会自动跳到前台")
    time.sleep(1)
    
    success = window_manager.activate_wechat_window()
    if success:
        print("✅ 窗口激活成功")
    else:
        print("❌ 窗口激活失败")
    
    # 等待用户确认窗口在前台
    print("\n   📱 请检查:")
    print("   1. 微信窗口是否在前台")
    print("   2. 窗口是否可见且可操作")
    print("   3. 然后等待3秒...")
    time.sleep(3)
    
    # 测试窗口大小调整
    print("\n5. 测试窗口大小调整...")
    print("   ⚠️ 注意: 观察微信窗口大小是否会变化")
    time.sleep(1)
    
    success = window_manager.adjust_window_size()
    if success:
        print("✅ 窗口大小调整成功")
    else:
        print("❌ 窗口大小调整失败")
    
    # 等待用户确认窗口大小
    print("\n   📱 请检查:")
    print("   1. 微信窗口大小是否合适")
    print("   2. 聊天列表和输入框是否可见")
    print("   3. 然后等待3秒...")
    time.sleep(3)
    
    # 测试完整准备流程
    print("\n6. 测试完整准备流程...")
    print("   🛠️ 准备: 文件传输助手")
    
    result = window_manager.prepare_for_sending("文件传输助手")
    
    print(f"\n   📊 准备结果:")
    for key, value in result.items():
        print(f"      {key}: {value}")
    
    if result.get('ready'):
        print("   ✅ 发送环境准备就绪")
        
        # 获取窗口信息
        print("\n7. 获取窗口信息...")
        info = window_manager.get_window_info()
        
        print(f"   状态: {info.get('status', 'unknown')}")
        if 'position' in info:
            print(f"   位置: {info['position']}")
        if 'size' in info:
            print(f"   大小: {info['size']}")
        print(f"   微信运行: {info.get('wechat_running', False)}")
        
    else:
        print("   ❌ 发送环境准备失败")
    
    # 测试开关功能
    print("\n8. 测试开关功能...")
    
    print("   a) 关闭群聊回复...")
    # 注意: 这里实际上应该调用 AutoReplySystem 的方法
    print("      可以在代码中调用: system.enable_group_reply(False)")
    
    print("\n   b) 切换为只回复@我...")
    print("      可以在代码中调用: system.set_reply_only_at_me(True)")
    
    print("\n   c) 添加群聊到黑名单...")
    print("      可以在代码中调用: system.add_group_to_blacklist('群ID', '原因')")
    
    print("\n   d) 关闭窗口自动激活...")
    config['window']['auto_activate'] = False
    print("      配置: window.auto_activate = False")
    
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ 测试异常: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print(f"\n{'='*60}")
print("🎯 功能总结")
print("="*60)
print()
print("✅ 已实现的窗口管理功能:")
print("   1. 自动检测微信运行状态")
print("   2. 自动启动微信（如果未运行）")
print("   3. 自动激活微信窗口到前台")
print("   4. 自动调整窗口到最佳大小（1200x800）")
print("   5. 窗口信息获取")
print()
print("🛠️ 推荐配置:")
print('''
{
  "window": {
    "enabled": true,
    "auto_activate": true,
    "adjust_size": true,
    "optimal_width": 1200,
    "optimal_height": 800,
    "max_retry": 3
  }
}
''')
print()
print("🚀 完整工作流程:")
print("   1. 用户发送消息 → 系统检测到数据库变化")
print("   2. 解密消息 → 通过安全检查 → 生成回复")
print("   3. 自动激活微信窗口 → 调整大小 → 定位聊天")
print("   4. 输入回复 → 点击发送")
print()
print("💡 重要提示:")
print("   - 系统会自动处理微信窗口，用户无需手动操作")
print("   - 窗口大小调整确保UI元素可见")
print("   - 如果微信未运行，系统会尝试自动启动")
print("   - 所有操作都有重试机制，避免单点失败")