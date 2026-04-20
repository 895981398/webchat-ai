#!/usr/bin/env python3
"""
群聊功能测试 - 只回复@我的消息，可以关闭群聊
"""

import sys
import os
import unittest
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.dirname(__file__))

if __name__ != "__main__":
    raise unittest.SkipTest("script-style test; run directly via python test_group_chat_feature.py")

print("🎯 群聊功能测试")
print("="*60)
print("时间:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
print()

# 1. 导入增强版自动回复系统
print("1. 导入增强版自动回复系统...")
try:
    from auto_reply import AutoReplySystem
    print("✅ AutoReplySystem 导入成功")
    
    # 导入增强安全控制器
    from auto_reply.core.safety_controller_enhanced import SafetyControllerEnhanced
    print("✅ SafetyControllerEnhanced 导入成功")
    
except Exception as e:
    print(f"❌ 导入失败: {e}")
    sys.exit(1)

# 2. 创建配置
print("\n2. 创建测试配置...")
config = {
    'mode': 'simulate',
    'user_name': '张三',  # 用户名，用于检测@我
    'nickname': '三哥',  # 昵称
    'test_contacts': ['文件传输助手'],
    'whitelist': [],
    'blacklist': [],
    
    # 群聊配置
    'group': {
        'enabled': True,           # 群聊总开关
        'reply_only_at_me': True,  # 只回复@我的消息
        'blacklist': ['wxid_spam@chatroom'],  # 垃圾群聊
        'whitelist': ['wxid_important@chatroom'],  # 重要群聊
        'default_reply': False
    }
}

print("✅ 配置创建完成")
print(f"   用户名: {config['user_name']}")
print(f"   昵称: {config['nickname']}")
print(f"   群聊模式: {'只回复@我' if config['group']['reply_only_at_me'] else '回复所有'}")

# 3. 创建自动回复系统
print("\n3. 初始化自动回复系统...")
try:
    system = AutoReplySystem(config)
    system.initialize()
    print("✅ 自动回复系统初始化成功")
    
    # 获取群聊统计
    group_stats = system.get_group_stats()
    print(f"   群聊状态:")
    print(f"     启用: {group_stats['enabled']}")
    print(f"     只回复@我: {group_stats['reply_only_at_me']}")
    print(f"     黑名单群聊: {group_stats['blacklist_count']} 个")
    print(f"     白名单群聊: {group_stats['whitelist_count']} 个")
    
except Exception as e:
    print(f"❌ 初始化失败: {e}")
    sys.exit(1)

# 4. 测试不同场景
print("\n4. 测试不同场景...")
test_cases = [
    # (描述, 用户名, 内容, 期望结果)
    ("私聊消息", "wxid_friend", "你好", "✅ 通过"),
    ("群聊@我", "wxid_group@chatroom", "@张三 你好", "✅ 通过"),
    ("群聊@我昵称", "wxid_group@chatroom", "@三哥 帮忙", "✅ 通过"),
    ("群聊未@我", "wxid_group@chatroom", "大家晚上好", "❌ 拒绝"),
    ("群聊@所有人", "wxid_group@chatroom", "@所有人 开会", "❌ 拒绝"),
    ("黑名单群聊", "wxid_spam@chatroom", "@张三 看广告", "❌ 拒绝"),
    ("白名单群聊", "wxid_important@chatroom", "大家好", "✅ 通过"),
]

print("\n📋 测试结果:")
print("-" * 80)

for desc, username, content, expected in test_cases:
    print(f"\n🔹 场景: {desc}")
    print(f"   发件人: {username}")
    print(f"   内容: {content}")
    print(f"   期望: {expected}")
    
    # 创建消息数据
    message_data = {
        'username': username,
        'content': content,
        'sender': username,
        'timestamp': datetime.now().timestamp()
    }
    
    try:
        # 处理消息
        result = system.handle_message(message_data)
        
        if result is not None:
            print(f"   ✅ 实际: 通过 - 回复: {result.get('reply', '无')}")
            if result.get('is_group'):
                print(f"       [群聊消息]")
        else:
            print(f"   ❌ 实际: 拒绝 - 未通过安全检查")
            
    except Exception as e:
        print(f"   ⚠️ 实际: 错误 - {e}")

# 5. 测试群聊开关功能
print("\n5. 测试群聊开关功能...")

print("\na) 关闭群聊回复:")
system.enable_group_reply(False)
group_stats = system.get_group_stats()
print(f"   当前状态: {'✅ 启用' if group_stats['enabled'] else '❌ 关闭'}")

# 测试关闭状态下的群聊消息
test_msg = {
    'username': 'wxid_group@chatroom',
    'content': '@张三 测试关闭状态',
    'sender': 'wxid_group@chatroom',
    'timestamp': datetime.now().timestamp()
}

result = system.handle_message(test_msg)
if result is None:
    print("   ✅ 群聊消息被正确拒绝")
else:
    print(f"   ❌ 错误: 群聊消息被处理了")

print("\nb) 开启群聊回复:")
system.enable_group_reply(True)
group_stats = system.get_group_stats()
print(f"   当前状态: {'✅ 启用' if group_stats['enabled'] else '❌ 关闭'}")

print("\nc) 切换为回复所有群聊消息:")
system.set_reply_only_at_me(False)
group_stats = system.get_group_stats()
print(f"   当前模式: {'只回复@我' if group_stats['reply_only_at_me'] else '回复所有'}")

# 测试非@我的群聊消息
test_msg = {
    'username': 'wxid_group@chatroom',
    'content': '普通群聊消息',
    'sender': 'wxid_group@chatroom',
    'timestamp': datetime.now().timestamp()
}

result = system.handle_message(test_msg)
if result is not None:
    print("   ✅ 非@我的群聊消息被处理了")
else:
    print("   ❌ 错误: 非@我的群聊消息被拒绝")

print("\nd) 切换回只回复@我:")
system.set_reply_only_at_me(True)
group_stats = system.get_group_stats()
print(f"   当前模式: {'只回复@我' if group_stats['reply_only_at_me'] else '回复所有'}")

# 6. 测试群聊管理
print("\n6. 测试群聊管理功能...")

print("\na) 添加群聊到黑名单:")
success = system.add_group_to_blacklist('wxid_test@chatroom', '测试群聊')
if success:
    print("   ✅ 成功添加到黑名单")
    group_stats = system.get_group_stats()
    print(f"   当前黑名单: {group_stats['blacklist_count']} 个群")
else:
    print("   ❌ 添加到黑名单失败")

print("\nb) 添加群聊到白名单:")
success = system.add_group_to_whitelist('wxid_family@chatroom', '家庭群')
if success:
    print("   ✅ 成功添加到白名单")
    group_stats = system.get_group_stats()
    print(f"   当前白名单: {group_stats['whitelist_count']} 个群")
else:
    print("   ❌ 添加到白名单失败")

# 7. 总结
print("\n" + "="*60)
print("🎯 功能总结")
print("="*60)
print("✅ 已实现的功能:")
print("   1. 群聊消息识别 (@chatroom)")
print("   2. @我消息检测 (@用户名/@昵称)")
print("   3. 群聊总开关 (启用/禁用)")
print("   4. 只回复@我 模式")
print("   5. 群聊黑名单/白名单")
print("   6. 群聊消息默认不回复")
print()
print("🚀 使用方法:")
print("   1. 在 auto_reply_config.json 中设置群聊配置")
print("   2. 系统会自动识别@我的消息")
print("   3. 可以通过代码动态管理群聊")
print()
print("📋 配置示例:")
print('''{
  "group": {
    "enabled": true,
    "reply_only_at_me": true,
    "blacklist": ["wxid_spam@chatroom"],
    "whitelist": ["wxid_important@chatroom"]
  }
}''')
print()
print("🔧 代码管理:")
print("   system.enable_group_reply(False)  # 关闭群聊")
print("   system.set_reply_only_at_me(True) # 只回复@我")
print("   system.add_group_to_blacklist('群ID', '原因')")
print("   system.add_group_to_whitelist('群ID', '原因')")