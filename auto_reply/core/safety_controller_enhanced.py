"""
安全控制器 - 增强版
集成群聊过滤和@我检测
"""

import time
import os
import json
from datetime import datetime

class SafetyControllerEnhanced:
    """安全控制器 - 增强版"""
    
    def __init__(self, config=None):
        self.config = config or {}
        
        # 安全配置
        self.safety_config = {
            'rate_limit': {
                'max_per_minute': 3,      # 每分钟最大发送数
                'max_per_hour': 30,       # 每小时最大发送数
                'min_interval_seconds': 20  # 最小发送间隔
            },
            'time_restriction': {
                'night_start': 23,        # 23:00
                'night_end': 7           # 7:00
            },
            'blacklist': [],
            'whitelist': [],
            'sensitive_keywords': [
                '政治', '敏感', '违法', '违规', '广告', '垃圾',
                '色情', '暴力', '诈骗', '钓鱼', '病毒', '恶意'
            ],
            'group': {
                'enabled': True,           # 群聊总开关
                'reply_only_at_me': True,  # 只回复@我的消息
                'blacklist': [],           # 群聊黑名单
                'whitelist': [],           # 群聊白名单
                'default_reply': False     # 默认不回复群聊
            }
        }
        
        # 用户信息（从微信数据获取）
        self.user_info = {
            'user_id': self.config.get('user_id', ''),
            'user_name': self.config.get('user_name', ''),
            'nickname': self.config.get('nickname', '')
        }
        
        # 加载配置文件
        self._load_config()
        
        # 发送记录
        self.sent_records = {
            'minute': [],
            'hour': [],
            'day': []
        }
        
        # 初始化时间
        self.current_day = datetime.now().day
        
        # 创建群聊规则目录
        self._create_group_rules_dir()
        
        print("[SafetyController] 初始化完成")
        
        # 打印群聊设置
        group_config = self.safety_config['group']
        print(f"  群聊设置:")
        print(f"    总开关: {'✅ 开启' if group_config['enabled'] else '❌ 关闭'}")
        print(f"    只回复@我: {'✅ 是' if group_config['reply_only_at_me'] else '❌ 否'}")
        print(f"    群聊黑名单: {len(group_config['blacklist'])} 个群")
        print(f"    群聊白名单: {len(group_config['whitelist'])} 个群")
        
    def _create_group_rules_dir(self):
        """创建群聊规则目录"""
        rules_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'rules', 'groups')
        os.makedirs(rules_dir, exist_ok=True)
        
        # 创建群聊黑名单文件
        blacklist_file = os.path.join(rules_dir, 'blacklist.json')
        if not os.path.exists(blacklist_file):
            with open(blacklist_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
        
        # 创建群聊白名单文件
        whitelist_file = os.path.join(rules_dir, 'whitelist.json')
        if not os.path.exists(whitelist_file):
            with open(whitelist_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
        
    def _load_config(self):
        """加载安全配置"""
        rules_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'rules')
        safety_file = os.path.join(rules_dir, 'safety_rules.json')
        
        if os.path.exists(safety_file):
            try:
                with open(safety_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    # 合并配置
                    self._merge_config(user_config)
                    print(f"[SafetyController] 加载用户配置: {safety_file}")
            except Exception as e:
                print(f"[SafetyController] 加载配置失败: {e}")
        else:
            # 创建默认配置
            self._create_default_config(safety_file)
            
        # 加载群聊规则
        self._load_group_rules()
            
    def _merge_config(self, user_config):
        """合并用户配置"""
        for key in self.safety_config:
            if key in user_config:
                if isinstance(self.safety_config[key], dict):
                    self.safety_config[key].update(user_config[key])
                else:
                    self.safety_config[key] = user_config[key]
                    
    def _load_group_rules(self):
        """加载群聊规则"""
        rules_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'rules', 'groups')
        
        # 加载群聊黑名单
        blacklist_file = os.path.join(rules_dir, 'blacklist.json')
        if os.path.exists(blacklist_file):
            try:
                with open(blacklist_file, 'r', encoding='utf-8') as f:
                    blacklist = json.load(f)
                    self.safety_config['group']['blacklist'] = blacklist
            except Exception as e:
                print(f"[SafetyController] 加载群聊黑名单失败: {e}")
        
        # 加载群聊白名单
        whitelist_file = os.path.join(rules_dir, 'whitelist.json')
        if os.path.exists(whitelist_file):
            try:
                with open(whitelist_file, 'r', encoding='utf-8') as f:
                    whitelist = json.load(f)
                    self.safety_config['group']['whitelist'] = whitelist
            except Exception as e:
                print(f"[SafetyController] 加载群聊白名单失败: {e}")
                    
    def _create_default_config(self, config_file):
        """创建默认配置"""
        rules_dir = os.path.dirname(config_file)
        os.makedirs(rules_dir, exist_ok=True)
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(self.safety_config, f, ensure_ascii=False, indent=2)
        print(f"[SafetyController] 创建默认配置: {config_file}")
        
    def check_message(self, message_data):
        """
        消息安全检查
        
        Args:
            message_data: 消息数据
            
        Returns:
            bool: 是否通过安全检查
        """
        username = message_data.get('username', 'unknown')
        content = message_data.get('content', '')
        
        print(f"[Safety] 安全检查: {username}")
        
        # 1. 群聊过滤
        if self._is_group_chat(username):
            print(f"[Safety] 👥 群聊消息检测")
            
            # 群聊安全检查
            group_result = self._check_group_message(username, content)
            
            if not group_result['should_reply']:
                print(f"[Safety] ❌ 群聊过滤: {group_result['reason']}")
                return False
            else:
                print(f"[Safety] ✅ 群聊允许: {group_result['reason']}")
        
        # 2. 其他安全检查
        checks = [
            ('频率限制', self._check_rate_limit),
            ('时间限制', self._check_time_restriction),
            ('内容过滤', lambda: self._check_content(content)),
            ('黑名单', lambda: self._check_blacklist(username)),
        ]
        
        for check_name, check_func in checks:
            if not check_func():
                print(f"[Safety] ❌ {check_name} 检查失败")
                return False
                
        print("[Safety] ✅ 所有安全检查通过")
        return True
        
    def _is_group_chat(self, username):
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
        group_config = self.safety_config.get('group', {})
        custom_groups = group_config.get('custom_groups', [])
        if not is_group and custom_groups:
            is_group = username in custom_groups
        
        return is_group
    
    def _check_group_message(self, group_username, message_content):
        """
        检查群聊消息
        
        Args:
            group_username: 群聊ID
            message_content: 消息内容
            
        Returns:
            dict: 检查结果
        """
        result = {
            'should_reply': False,
            'reason': '',
            'filtered_by': ''
        }
        
        group_config = self.safety_config.get('group', {})
        
        # 1. 检查群聊总开关
        if not group_config.get('enabled', True):
            result['reason'] = '群聊总开关关闭'
            result['filtered_by'] = 'global_switch'
            return result
        
        # 2. 检查是否在群聊黑名单
        if group_username in group_config.get('blacklist', []):
            result['reason'] = '群聊在黑名单中'
            result['filtered_by'] = 'blacklist'
            return result
        
        # 3. 检查是否在群聊白名单
        if group_username in group_config.get('whitelist', []):
            # 白名单群聊直接回复
            result['should_reply'] = True
            result['reason'] = '群聊在白名单中'
            result['filtered_by'] = 'whitelist'
            return result
        
        # 4. 检查是否只回复@我的消息
        if group_config.get('reply_only_at_me', True):
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
        判断消息是否@了我
        
        Args:
            message_content: 消息内容
            
        Returns:
            bool: 是否@了我
        """
        if not message_content:
            return False
        
        # 获取用户信息
        user_name = self.user_info.get('user_name', '')
        nickname = self.user_info.get('nickname', '')
        
        # 方法1: 检查@符号和我的用户名
        if user_name and f'@{user_name}' in message_content:
            return True
        
        # 方法2: 检查@我的昵称
        if nickname and f'@{nickname}' in message_content:
            return True
        
        # 方法3: 检查常见的@格式
        at_patterns = [
            '提到我',
            'at me',
            'call me',
            'ping me',
            'mention me'
        ]
        
        for pattern in at_patterns:
            if pattern.lower() in message_content.lower():
                return True
        
        # 方法4: 检查@所有人（如果@我设置为包含@所有人）
        if '@所有人' in message_content or '@all' in message_content.lower():
            # 这里可以根据配置决定是否回复@所有人
            group_config = self.safety_config.get('group', {})
            reply_to_all = not group_config.get('reply_only_at_me', True)
            return reply_to_all
        
        return False
        
    def _check_rate_limit(self):
        """检查频率限制"""
        now = time.time()
        
        # 清理过期记录
        self._cleanup_sent_records(now)
        
        # 检查每分钟限制
        minute_limit = self.safety_config['rate_limit']['max_per_minute']
        recent_minute = [t for t in self.sent_records['minute'] if now - t < 60]
        if len(recent_minute) >= minute_limit:
            print(f"[Safety] 每分钟限制: {len(recent_minute)}/{minute_limit}")
            return False
            
        # 检查每小时限制
        hour_limit = self.safety_config['rate_limit']['max_per_hour']
        recent_hour = [t for t in self.sent_records['hour'] if now - t < 3600]
        if len(recent_hour) >= hour_limit:
            print(f"[Safety] 每小时限制: {len(recent_hour)}/{hour_limit}")
            return False
            
        # 检查最小间隔
        min_interval = self.safety_config['rate_limit']['min_interval_seconds']
        if self.sent_records['minute']:
            last_sent = max(self.sent_records['minute'])
            if now - last_sent < min_interval:
                print(f"[Safety] 发送间隔过短: {now - last_sent:.1f}s < {min_interval}s")
                return False
                
        return True
        
    def _cleanup_sent_records(self, now):
        """清理发送记录"""
        # 清理过期记录
        self.sent_records['minute'] = [t for t in self.sent_records['minute'] if now - t < 60]
        self.sent_records['hour'] = [t for t in self.sent_records['hour'] if now - t < 3600]
        
        # 如果跨天，清理每日记录
        if datetime.now().day != self.current_day:
            self.sent_records['day'] = []
            self.current_day = datetime.now().day
            
    def _check_time_restriction(self):
        """检查时间限制"""
        current_hour = datetime.now().hour
        night_start = self.safety_config['time_restriction']['night_start']
        night_end = self.safety_config['time_restriction']['night_end']
        
        # 夜间不发送
        if night_start <= current_hour or current_hour < night_end:
            print(f"[Safety] 夜间限制: {current_hour}点")
            return False
            
        return True
        
    def _check_content(self, content):
        """检查内容是否包含敏感词"""
        if not content:
            return True
            
        content_lower = content.lower()
        sensitive_keywords = self.safety_config.get('sensitive_keywords', [])
        
        for keyword in sensitive_keywords:
            if keyword.lower() in content_lower:
                print(f"[Safety] 检测到敏感词: {keyword}")
                return False
                
        return True
        
    def _check_blacklist(self, username):
        """检查黑名单"""
        if not username:
            return True
            
        blacklist = self.safety_config.get('blacklist', [])
        if username in blacklist:
            print(f"[Safety] 黑名单用户: {username}")
            return False
            
        return True
        
    def record_sent_message(self):
        """记录已发送消息"""
        now = time.time()
        
        self.sent_records['minute'].append(now)
        self.sent_records['hour'].append(now)
        self.sent_records['day'].append(now)
        
        print(f"[Safety] 记录发送: {datetime.now().strftime('%H:%M:%S')}")
        
    # 群聊管理方法
    def add_group_to_blacklist(self, group_username, reason=''):
        """添加群聊到黑名单"""
        group_config = self.safety_config.get('group', {})
        blacklist = group_config.get('blacklist', [])
        
        if group_username not in blacklist:
            blacklist.append(group_username)
            group_config['blacklist'] = blacklist
            self._save_group_rules()
            
            print(f"[Safety] 添加群聊到黑名单: {group_username}")
            if reason:
                print(f"    原因: {reason}")
            
            return True
        
        return False
    
    def remove_group_from_blacklist(self, group_username):
        """从黑名单移除群聊"""
        group_config = self.safety_config.get('group', {})
        blacklist = group_config.get('blacklist', [])
        
        if group_username in blacklist:
            blacklist.remove(group_username)
            group_config['blacklist'] = blacklist
            self._save_group_rules()
            
            print(f"[Safety] 从黑名单移除群聊: {group_username}")
            return True
        
        return False
    
    def add_group_to_whitelist(self, group_username, reason=''):
        """添加群聊到白名单"""
        group_config = self.safety_config.get('group', {})
        whitelist = group_config.get('whitelist', [])
        
        if group_username not in whitelist:
            whitelist.append(group_username)
            group_config['whitelist'] = whitelist
            self._save_group_rules()
            
            print(f"[Safety] 添加群聊到白名单: {group_username}")
            if reason:
                print(f"    原因: {reason}")
            
            return True
        
        return False
    
    def remove_group_from_whitelist(self, group_username):
        """从白名单移除群聊"""
        group_config = self.safety_config.get('group', {})
        whitelist = group_config.get('whitelist', [])
        
        if group_username in whitelist:
            whitelist.remove(group_username)
            group_config['whitelist'] = whitelist
            self._save_group_rules()
            
            print(f"[Safety] 从白名单移除群聊: {group_username}")
            return True
        
        return False
    
    def enable_group_reply(self, enable=True):
        """启用或禁用群聊回复"""
        group_config = self.safety_config.get('group', {})
        group_config['enabled'] = enable
        
        if enable:
            print(f"[Safety] ✅ 群聊回复已启用")
        else:
            print(f"[Safety] ❌ 群聊回复已禁用")
        
        return enable
    
    def set_reply_only_at_me(self, only_at_me=True):
        """设置是否只回复@我的消息"""
        group_config = self.safety_config.get('group', {})
        group_config['reply_only_at_me'] = only_at_me
        
        if only_at_me:
            print(f"[Safety] ✅ 设置为只回复@我的消息")
        else:
            print(f"[Safety] ✅ 设置为回复所有群聊消息")
        
        return only_at_me
    
    def _save_group_rules(self):
        """保存群聊规则到文件"""
        rules_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'rules', 'groups')
        os.makedirs(rules_dir, exist_ok=True)
        
        group_config = self.safety_config.get('group', {})
        
        # 保存群聊黑名单
        blacklist_file = os.path.join(rules_dir, 'blacklist.json')
        with open(blacklist_file, 'w', encoding='utf-8') as f:
            json.dump(group_config.get('blacklist', []), f, ensure_ascii=False, indent=2)
        
        # 保存群聊白名单
        whitelist_file = os.path.join(rules_dir, 'whitelist.json')
        with open(whitelist_file, 'w', encoding='utf-8') as f:
            json.dump(group_config.get('whitelist', []), f, ensure_ascii=False, indent=2)
        
    def get_stats(self):
        """获取统计信息"""
        now = time.time()
        
        stats = {
            'sent_today': len(self.sent_records['day']),
            'sent_last_hour': len([t for t in self.sent_records['hour'] if now - t < 3600]),
            'sent_last_minute': len([t for t in self.sent_records['minute'] if now - t < 60]),
            'blacklist_count': len(self.safety_config.get('blacklist', [])),
            'whitelist_count': len(self.safety_config.get('whitelist', [])),
            'current_mode': 'simulate',  # 从config获取
            'group_enabled': self.safety_config.get('group', {}).get('enabled', True),
            'reply_only_at_me': self.safety_config.get('group', {}).get('reply_only_at_me', True),
            'group_blacklist_count': len(self.safety_config.get('group', {}).get('blacklist', [])),
            'group_whitelist_count': len(self.safety_config.get('group', {}).get('whitelist', []))
        }
        
        return stats


# 测试
if __name__ == "__main__":
    print("=== SafetyControllerEnhanced 测试 ===")
    
    config = {
        'user_name': '张三',
        'nickname': '三哥'
    }
    
    controller = SafetyControllerEnhanced(config)
    
    # 测试消息
    test_messages = [
        {'username': 'wxid_group@chatroom', 'content': '大家好'},
        {'username': 'wxid_group@chatroom', 'content': '@张三 你好'},
        {'username': 'wxid_group@chatroom', 'content': '@三哥 晚上好'},
        {'username': 'wxid_group@chatroom', 'content': '@所有人 开会了'},
        {'username': 'wxid_zhangsan', 'content': '私聊消息'},
    ]
    
    for msg in test_messages:
        print(f"\n测试: {msg['username']} -> {msg['content']}")
        result = controller.check_message(msg)
        print(f"结果: {'✅ 通过' if result else '❌ 拒绝'}")