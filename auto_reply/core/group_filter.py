"""
群聊过滤器
负责识别 @我的消息和群聊开关
"""

import re
import json
import os
from pathlib import Path

class GroupFilter:
    """群聊消息过滤器"""
    
    def __init__(self, config=None):
        self.config = config or {}
        
        # 群聊配置
        self.group_config = {
            'enabled': True,  # 总开关
            'reply_only_at_me': True,  # 只回复@我的消息
            'blacklist': [],  # 群聊黑名单
            'whitelist': [],  # 群聊白名单
            'default_reply': False  # 默认不回复群聊
        }
        
        # 更新配置
        if 'group' in self.config:
            self.group_config.update(self.config['group'])
        
        # 用户ID（需要从微信数据中提取）
        self.user_id = self.config.get('user_id', '')
        self.user_name = self.config.get('user_name', '')
        
        # 加载自定义群聊规则
        self._load_group_rules()
        
        print(f"[GroupFilter] 初始化完成")
        print(f"  总开关: {'✅ 开启' if self.group_config['enabled'] else '❌ 关闭'}")
        print(f"  只回复@我: {'✅ 是' if self.group_config['reply_only_at_me'] else '❌ 否'}")
        print(f"  群聊黑名单: {len(self.group_config['blacklist'])} 个群")
        print(f"  群聊白名单: {len(self.group_config['whitelist'])} 个群")
    
    def _load_group_rules(self):
        """加载群聊规则文件"""
        rules_dir = Path(__file__).parent.parent / 'rules' / 'groups'
        rules_dir.mkdir(parents=True, exist_ok=True)
        
        # 黑名单文件
        blacklist_file = rules_dir / 'blacklist.json'
        if blacklist_file.exists():
            with open(blacklist_file, 'r', encoding='utf-8') as f:
                blacklist = json.load(f)
                self.group_config['blacklist'].extend(blacklist)
        
        # 白名单文件
        whitelist_file = rules_dir / 'whitelist.json'
        if whitelist_file.exists():
            with open(whitelist_file, 'r', encoding='utf-8') as f:
                whitelist = json.load(f)
                self.group_config['whitelist'].extend(whitelist)
    
    def is_group_chat(self, username):
        """
        判断是否为群聊
        
        Args:
            username: 聊天对象ID
            
        Returns:
            bool: 是否为群聊
        """
        # 简单的判断逻辑：群聊ID通常包含@chatroom
        if not username:
            return False
        
        # 检查是否是群聊
        is_group = '@chatroom' in username
        
        # 检查是否在自定义群聊列表中
        if not is_group and self.group_config.get('custom_groups'):
            is_group = username in self.group_config['custom_groups']
        
        return is_group
    
    def should_reply_to_group(self, group_username, message_content):
        """
        判断是否应该回复群聊消息
        
        Args:
            group_username: 群聊ID
            message_content: 消息内容
            
        Returns:
            dict: 包含判断结果和原因
        """
        result = {
            'should_reply': False,
            'reason': '',
            'filtered_by': ''
        }
        
        # 1. 检查群聊总开关
        if not self.group_config['enabled']:
            result['reason'] = '群聊总开关关闭'
            result['filtered_by'] = 'global_switch'
            return result
        
        # 2. 检查是否在黑名单
        if group_username in self.group_config['blacklist']:
            result['reason'] = '群聊在黑名单中'
            result['filtered_by'] = 'blacklist'
            return result
        
        # 3. 检查是否在白名单
        if group_username in self.group_config['whitelist']:
            # 白名单群聊直接回复
            result['should_reply'] = True
            result['reason'] = '群聊在白名单中'
            result['filtered_by'] = 'whitelist'
            return result
        
        # 4. 检查是否只回复@我的消息
        if self.group_config['reply_only_at_me']:
            if self._is_mentioned_in_message(message_content):
                result['should_reply'] = True
                result['reason'] = '消息@了我'
                result['filtered_by'] = 'at_me'
            else:
                result['reason'] = '消息没有@我'
                result['filtered_by'] = 'not_at_me'
        else:
            # 默认回复所有群聊消息
            result['should_reply'] = True
            result['reason'] = '群聊消息（非@模式）'
            result['filtered_by'] = 'all_groups'
        
        return result
    
    def _is_mentioned_in_message(self, message_content):
        """
        判断消息是否@了我 - 精确匹配
        
        Args:
            message_content: 消息内容
            
        Returns:
            bool: 是否@了我
        """
        if not message_content:
            return False
        
        # 转换为小写用于不区分大小写的匹配
        content_lower = message_content.lower()
        
        # 1. 检查@我的用户名（精确匹配）
        if self.user_name:
            user_name_lower = self.user_name.lower()
            
            # 检查 @用户名（半角）
            if f'@{user_name_lower}' in content_lower:
                return True
            
            # 检查 ＠用户名（全角）
            if f'＠{user_name_lower}' in content_lower:
                return True
            
            # 检查 @我的其他可能形式
            # 例如：@张三、@三哥、@zhangsan
            possible_mentions = [
                f'@{user_name_lower}',     # 半角@
                f'＠{user_name_lower}',     # 全角＠
                f'@ {user_name_lower}',    # 半角@后有空格
                f'＠ {user_name_lower}',    # 全角＠后有空格
                f'@{user_name_lower} ',    # 半角@后有内容加空格
                f'＠{user_name_lower} ',    # 全角＠后有内容加空格
            ]
            
            for mention in possible_mentions:
                if mention in content_lower:
                    return True
        
        # 2. 检查昵称（如果有）
        nickname = self.config.get('nickname', '')
        if nickname:
            nickname_lower = nickname.lower()
            
            # 检查 @昵称（半角）
            if f'@{nickname_lower}' in content_lower:
                return True
            
            # 检查 ＠昵称（全角）
            if f'＠{nickname_lower}' in content_lower:
                return True
            
            # 检查 @昵称的其他形式
            possible_nicknames = [
                f'@{nickname_lower}',     # 半角@
                f'＠{nickname_lower}',     # 全角＠
                f'@ {nickname_lower}',    # 半角@后有空格
                f'＠ {nickname_lower}',    # 全角＠后有空格
                f'@{nickname_lower} ',    # 半角@后有内容加空格
                f'＠{nickname_lower} ',    # 全角＠后有内容加空格
            ]
            
            for nick_mention in possible_nicknames:
                if nick_mention in content_lower:
                    return True
        
        # 3. 检查明确的@我关键词
        mention_keywords = [
            '提到我',
            'at me',
            'mention me',
            '艾特我',
            'call me',
            'ping me',
        ]
        
        for keyword in mention_keywords:
            if keyword in content_lower:
                return True
        
        # 4. 检查微信特定的@格式
        # 微信中的@通常会有特殊标记
        if '@' in message_content:
            # 提取所有@后面的内容
            at_matches = re.findall(r'[@＠]([^\s@＠]+)', message_content)
            
            # 如果有配置，可以检查是否@的是我的微信ID
            wechat_id = self.config.get('wechat_id', '')
            if wechat_id and wechat_id in at_matches:
                return True
            
            # 或者检查是否@的是我的显示名
            display_name = self.config.get('display_name', '')
            if display_name and display_name in at_matches:
                return True
        
        return False
    
    def add_to_blacklist(self, group_username, reason=''):
        """
        添加群聊到黑名单
        
        Args:
            group_username: 群聊ID
            reason: 原因
            
        Returns:
            bool: 是否成功添加
        """
        if group_username not in self.group_config['blacklist']:
            self.group_config['blacklist'].append(group_username)
            
            # 保存到文件
            self._save_group_rules()
            
            print(f"[GroupFilter] 已添加到黑名单: {group_username}")
            if reason:
                print(f"    原因: {reason}")
            
            return True
        
        return False
    
    def remove_from_blacklist(self, group_username):
        """
        从黑名单移除群聊
        
        Args:
            group_username: 群聊ID
            
        Returns:
            bool: 是否成功移除
        """
        if group_username in self.group_config['blacklist']:
            self.group_config['blacklist'].remove(group_username)
            
            # 保存到文件
            self._save_group_rules()
            
            print(f"[GroupFilter] 已从黑名单移除: {group_username}")
            return True
        
        return False
    
    def add_to_whitelist(self, group_username, reason=''):
        """
        添加群聊到白名单
        
        Args:
            group_username: 群聊ID
            reason: 原因
            
        Returns:
            bool: 是否成功添加
        """
        if group_username not in self.group_config['whitelist']:
            self.group_config['whitelist'].append(group_username)
            
            # 保存到文件
            self._save_group_rules()
            
            print(f"[GroupFilter] 已添加到白名单: {group_username}")
            if reason:
                print(f"    原因: {reason}")
            
            return True
        
        return False
    
    def remove_from_whitelist(self, group_username):
        """
        从白名单移除群聊
        
        Args:
            group_username: 群聊ID
            
        Returns:
            bool: 是否成功移除
        """
        if group_username in self.group_config['whitelist']:
            self.group_config['whitelist'].remove(group_username)
            
            # 保存到文件
            self._save_group_rules()
            
            print(f"[GroupFilter] 已从白名单移除: {group_username}")
            return True
        
        return False
    
    def _save_group_rules(self):
        """保存群聊规则到文件"""
        rules_dir = Path(__file__).parent.parent / 'rules' / 'groups'
        rules_dir.mkdir(parents=True, exist_ok=True)
        
        # 保存黑名单
        blacklist_file = rules_dir / 'blacklist.json'
        with open(blacklist_file, 'w', encoding='utf-8') as f:
            json.dump(self.group_config['blacklist'], f, ensure_ascii=False, indent=2)
        
        # 保存白名单
        whitelist_file = rules_dir / 'whitelist.json'
        with open(whitelist_file, 'w', encoding='utf-8') as f:
            json.dump(self.group_config['whitelist'], f, ensure_ascii=False, indent=2)
    
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
            print(f"[GroupFilter] ✅ 群聊回复已启用")
        else:
            print(f"[GroupFilter] ❌ 群聊回复已禁用")
        
        return enable
    
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
            print(f"[GroupFilter] ✅ 设置为只回复@我的消息")
        else:
            print(f"[GroupFilter] ✅ 设置为回复所有群聊消息")
        
        return only_at_me
    
    def get_stats(self):
        """获取统计信息"""
        return {
            'enabled': self.group_config['enabled'],
            'reply_only_at_me': self.group_config['reply_only_at_me'],
            'blacklist_count': len(self.group_config['blacklist']),
            'whitelist_count': len(self.group_config['whitelist']),
            'user_name': self.user_name,
            'user_id': self.user_id
        }


# 测试
if __name__ == "__main__":
    print("=== GroupFilter 测试 ===")
    
    config = {
        'user_name': '张三',
        'user_id': 'wxid_zhangsan'
    }
    
    filter = GroupFilter(config)
    
    # 测试群聊判断
    test_cases = [
        ('wxid_group@chatroom', '大家好'),
        ('wxid_group@chatroom', '@张三 你好'),
        ('wxid_zhangsan', '私聊消息'),
        ('wxid_group@chatroom', '＠张三 提到你了'),
    ]
    
    for username, content in test_cases:
        print(f"\n测试: {username} -> {content}")
        if filter.is_group_chat(username):
            result = filter.should_reply_to_group(username, content)
            print(f"  结果: {result['should_reply']}")
            print(f"  原因: {result['reason']}")
        else:
            print("  这不是群聊")