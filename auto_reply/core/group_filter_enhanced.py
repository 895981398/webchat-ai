"""
增强版群聊过滤器 - 支持白名单机制
功能：
1. 默认关闭所有群聊回复
2. 只回复白名单群聊的@我消息
3. 灵活管理白名单
"""

import json
import os
import re
from pathlib import Path
from datetime import datetime

class GroupFilterEnhanced:
    """增强版群聊过滤器 - 白名单机制"""
    
    def __init__(self, config=None):
        self.config = config or {}
        
        # 群聊配置 - 默认关闭所有群聊回复
        self.group_config = {
            'enabled': False,           # 总开关：默认关闭群聊回复
            'reply_only_at_me': True,   # 只回复@我的消息
            'whitelist_mode': True,     # 白名单模式：只回复白名单群聊
            'whitelist': [],            # 白名单群聊
            'blacklist': [],            # 黑名单群聊
            'strict_mention_check': True,  # 严格检查@我
            'auto_detect_nicknames': False,  # 不自动检测昵称
        }
        
        # 更新配置
        if 'group' in self.config:
            self.group_config.update(self.config['group'])
        
        # 用户信息（可选，用于@我检测）
        self.user_name = self.config.get('user_name', '')
        self.nickname = self.config.get('nickname', '')
        
        # 加载白名单和黑名单
        self._load_group_lists()
        
        print(f"[GroupFilterEnhanced] 初始化完成")
        print(f"  群聊总开关: {'✅ 开启' if self.group_config['enabled'] else '❌ 关闭（默认）'}")
        print(f"  白名单模式: {'✅ 开启' if self.group_config['whitelist_mode'] else '❌ 关闭'}")
        print(f"  只回复@我: {'✅ 开启' if self.group_config['reply_only_at_me'] else '❌ 关闭'}")
        print(f"  白名单群聊: {len(self.group_config['whitelist'])} 个")
        print(f"  黑名单群聊: {len(self.group_config['blacklist'])} 个")
        
        if self.group_config['whitelist_mode'] and not self.group_config['whitelist']:
            print(f"[GroupFilterEnhanced] ⚠️  白名单模式已开启，但白名单为空")
            print(f"    除非添加群聊到白名单，否则不会回复任何群聊消息")
    
    def _load_group_lists(self):
        """加载群聊名单"""
        rules_dir = Path(__file__).parent.parent / 'rules' / 'groups'
        rules_dir.mkdir(parents=True, exist_ok=True)
        
        # 加载白名单
        whitelist_file = rules_dir / 'whitelist.json'
        if whitelist_file.exists():
            with open(whitelist_file, 'r', encoding='utf-8') as f:
                whitelist = json.load(f)
                self.group_config['whitelist'].extend(whitelist)
        
        # 加载黑名单
        blacklist_file = rules_dir / 'blacklist.json'
        if blacklist_file.exists():
            with open(blacklist_file, 'r', encoding='utf-8') as f:
                blacklist = json.load(f)
                self.group_config['blacklist'].extend(blacklist)
    
    def _save_group_lists(self):
        """保存群聊名单"""
        rules_dir = Path(__file__).parent.parent / 'rules' / 'groups'
        rules_dir.mkdir(parents=True, exist_ok=True)
        
        # 保存白名单
        whitelist_file = rules_dir / 'whitelist.json'
        with open(whitelist_file, 'w', encoding='utf-8') as f:
            json.dump(self.group_config['whitelist'], f, ensure_ascii=False, indent=2)
        
        # 保存黑名单
        blacklist_file = rules_dir / 'blacklist.json'
        with open(blacklist_file, 'w', encoding='utf-8') as f:
            json.dump(self.group_config['blacklist'], f, ensure_ascii=False, indent=2)
    
    def is_group_chat(self, username):
        """
        判断是否为群聊
        
        Args:
            username: 聊天对象ID
            
        Returns:
            bool: 是否为群聊
        """
        if not username:
            return False
        
        # 简单的判断逻辑：群聊ID通常包含@chatroom
        is_group = '@chatroom' in username
        
        # 检查是否在自定义群聊列表中
        if not is_group and self.group_config.get('custom_groups'):
            is_group = username in self.group_config['custom_groups']
        
        return is_group
    
    def should_reply_to_group(self, group_username, message_content):
        """
        判断是否应该回复群聊消息 - 白名单机制
        
        Args:
            group_username: 群聊ID
            message_content: 消息内容
            
        Returns:
            dict: 包含判断结果和原因
        """
        result = {
            'should_reply': False,
            'reason': '',
            'filtered_by': '',
            'in_whitelist': False,
            'mentioned': False
        }
        
        # 1. 检查群聊总开关
        if not self.group_config['enabled']:
            result['reason'] = '群聊总开关关闭'
            result['filtered_by'] = 'global_switch'
            return result
        
        # 2. 检查是否在黑名单中
        if group_username in self.group_config['blacklist']:
            result['reason'] = '群聊在黑名单中'
            result['filtered_by'] = 'blacklist'
            return result
        
        # 3. 检查是否在白名单中
        in_whitelist = group_username in self.group_config['whitelist']
        result['in_whitelist'] = in_whitelist
        
        # 白名单模式：不在白名单就不回复
        if self.group_config['whitelist_mode'] and not in_whitelist:
            result['reason'] = '群聊不在白名单中'
            result['filtered_by'] = 'not_in_whitelist'
            return result
        
        # 4. 白名单群聊，检查@我规则
        if self.group_config['reply_only_at_me']:
            is_mentioned = self._is_mentioned_in_message(message_content)
            result['mentioned'] = is_mentioned
            
            if is_mentioned:
                result['should_reply'] = True
                result['reason'] = '白名单群聊，消息@了我'
                result['filtered_by'] = 'whitelist_at_me'
            else:
                result['reason'] = '白名单群聊，但消息没有@我'
                result['filtered_by'] = 'whitelist_not_at_me'
        else:
            # 白名单群聊，回复所有消息
            result['should_reply'] = True
            result['reason'] = '白名单群聊，回复所有消息'
            result['filtered_by'] = 'whitelist_all'
        
        return result
    
    def _is_mentioned_in_message(self, message_content):
        """
        判断消息是否@了我 - 严格模式
        
        Args:
            message_content: 消息内容
            
        Returns:
            bool: 是否@了我
        """
        if not message_content:
            return False
        
        # 1. 检查明确的@我关键词
        mention_keywords = [
            '提到我', 'mention me', 'at me',
            '艾特我', 'call me', 'ping me',
            '我一下', '我啊', '我啊'
        ]
        
        content_lower = message_content.lower()
        for keyword in mention_keywords:
            if keyword in content_lower:
                return True
        
        # 2. 检查@符号（如果配置了用户信息）
        if self.user_name or self.nickname:
            # 检查@用户名
            if self.user_name:
                user_name_lower = self.user_name.lower()
                if f'@{user_name_lower}' in content_lower:
                    return True
                if f'＠{user_name_lower}' in content_lower:
                    return True
            
            # 检查@昵称
            if self.nickname:
                nickname_lower = self.nickname.lower()
                if f'@{nickname_lower}' in content_lower:
                    return True
                if f'＠{nickname_lower}' in content_lower:
                    return True
        
        # 3. 检查微信消息的mention字段（如果有）
        # 这里可以扩展，如果微信数据中有mention flag
        
        return False
    
    # 白名单管理方法
    def add_to_whitelist(self, group_username, group_name='', reason=''):
        """
        添加群聊到白名单
        
        Args:
            group_username: 群聊ID（必须）
            group_name: 群聊名称（可选）
            reason: 原因（可选）
            
        Returns:
            bool: 是否成功添加
        """
        if group_username not in self.group_config['whitelist']:
            # 创建白名单条目
            entry = {
                'username': group_username,
                'name': group_name or group_username,
                'added_at': datetime.now().isoformat(),
                'reason': reason or '用户手动添加'
            }
            
            self.group_config['whitelist'].append(entry)
            self._save_group_lists()
            
            print(f"[GroupFilterEnhanced] ✅ 已添加到白名单:")
            print(f"  群聊ID: {group_username}")
            if group_name:
                print(f"  群聊名: {group_name}")
            if reason:
                print(f"  原因: {reason}")
            
            return True
        
        print(f"[GroupFilterEnhanced] ⚠️  群聊已在白名单中: {group_username}")
        return False
    
    def remove_from_whitelist(self, group_username):
        """
        从白名单移除群聊
        
        Args:
            group_username: 群聊ID
            
        Returns:
            bool: 是否成功移除
        """
        original_count = len(self.group_config['whitelist'])
        
        # 移除匹配的条目
        self.group_config['whitelist'] = [
            entry for entry in self.group_config['whitelist']
            if entry.get('username') != group_username
        ]
        
        if len(self.group_config['whitelist']) < original_count:
            self._save_group_lists()
            print(f"[GroupFilterEnhanced] ✅ 已从白名单移除: {group_username}")
            return True
        
        print(f"[GroupFilterEnhanced] ⚠️  群聊不在白名单中: {group_username}")
        return False
    
    def get_whitelist(self):
        """
        获取白名单列表
        
        Returns:
            list: 白名单群聊
        """
        return self.group_config['whitelist']
    
    def is_in_whitelist(self, group_username):
        """
        检查群聊是否在白名单中
        
        Args:
            group_username: 群聊ID
            
        Returns:
            bool: 是否在白名单中
        """
        for entry in self.group_config['whitelist']:
            if entry.get('username') == group_username:
                return True
        return False
    
    # 群聊总开关
    def enable_group_reply(self, enable=True):
        """
        启用或禁用群聊回复
        
        Args:
            enable: 是否启用
            
        Returns:
            bool: 新状态
        """
        self.group_config['enabled'] = enable
        
        if enable:
            print(f"[GroupFilterEnhanced] ✅ 群聊回复已启用")
            print(f"  白名单模式: {'✅ 开启' if self.group_config['whitelist_mode'] else '❌ 关闭'}")
            print(f"  白名单群聊数: {len(self.group_config['whitelist'])}")
        else:
            print(f"[GroupFilterEnhanced] ❌ 群聊回复已禁用")
            print(f"  所有群聊消息将被忽略")
        
        return enable
    
    # 白名单模式开关
    def enable_whitelist_mode(self, enable=True):
        """
        启用或禁用白名单模式
        
        Args:
            enable: 是否启用白名单模式
            
        Returns:
            bool: 新状态
        """
        self.group_config['whitelist_mode'] = enable
        
        if enable:
            print(f"[GroupFilterEnhanced] ✅ 白名单模式已启用")
            print(f"  只回复白名单中的群聊")
            print(f"  当前白名单: {len(self.group_config['whitelist'])} 个群聊")
        else:
            print(f"[GroupFilterEnhanced] ❌ 白名单模式已禁用")
            print(f"  将根据其他规则处理群聊消息")
        
        return enable
    
    # 只回复@我开关
    def set_reply_only_at_me(self, only_at_me=True):
        """
        设置是否只回复@我的消息
        
        Args:
            only_at_me: 是否只回复@我的消息
            
        Returns:
            bool: 新状态
        """
        self.group_config['reply_only_at_me'] = only_at_me
        
        if only_at_me:
            print(f"[GroupFilterEnhanced] ✅ 设置为只回复@我的消息")
        else:
            print(f"[GroupFilterEnhanced] ✅ 设置为回复所有消息（在白名单中）")
        
        return only_at_me
    
    def get_stats(self):
        """获取统计信息"""
        return {
            'enabled': self.group_config['enabled'],
            'whitelist_mode': self.group_config['whitelist_mode'],
            'reply_only_at_me': self.group_config['reply_only_at_me'],
            'whitelist_count': len(self.group_config['whitelist']),
            'blacklist_count': len(self.group_config['blacklist']),
            'user_name': self.user_name,
            'nickname': self.nickname
        }


# 测试
if __name__ == "__main__":
    print("=== GroupFilterEnhanced 测试 ===")
    
    config = {
        'user_name': '张哥',
        'nickname': '张总',
        'group': {
            'enabled': False,           # 默认关闭群聊回复
            'whitelist_mode': True,     # 白名单模式
            'reply_only_at_me': True,   # 只回复@我
            'whitelist': [
                {'username': 'family@chatroom', 'name': '家庭群'},
                {'username': 'work@chatroom', 'name': '工作群'},
            ]
        }
    }
    
    filter = GroupFilterEnhanced(config)
    
    # 测试用例
    test_cases = [
        ('family@chatroom', '@张哥 回家吃饭', True, '白名单群聊，@我了'),
        ('family@chatroom', '今天天气不错', False, '白名单群聊，没@我'),
        ('work@chatroom', '提到我一下', True, '白名单群聊，提到我了'),
        ('friends@chatroom', '@张哥 打游戏', False, '非白名单群聊'),
        ('family@chatroom', '@李四 你好', False, '白名单群聊，@别人'),
    ]
    
    for username, content, expected, description in test_cases:
        print(f"\n测试: {description}")
        print(f"  群聊: {username}")
        print(f"  消息: {content}")
        
        result = filter.should_reply_to_group(username, content)
        
        print(f"  结果: {'✅ 应该回复' if result['should_reply'] else '❌ 不应该回复'}")
        print(f"  原因: {result['reason']}")
        print(f"  预期: {'✅ 正确' if result['should_reply'] == expected else '❌ 错误'}")