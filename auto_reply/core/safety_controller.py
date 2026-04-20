"""
安全控制系统
控制发送频率、内容过滤等安全措施
"""

import time
import os
import json
from datetime import datetime

class SafetyController:
    """安全控制器"""
    
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
            ]
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
        
        print("[SafetyController] 初始化完成")
        
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
            
    def _merge_config(self, user_config):
        """合并用户配置"""
        for key in self.safety_config:
            if key in user_config:
                if isinstance(self.safety_config[key], dict):
                    self.safety_config[key].update(user_config[key])
                else:
                    self.safety_config[key] = user_config[key]
                    
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
        print(f"[Safety] 安全检查: {message_data.get('username', 'unknown')}")
        
        checks = [
            ('频率限制', self._check_rate_limit),
            ('时间限制', self._check_time_restriction),
            ('内容过滤', lambda: self._check_content(message_data.get('content', ''))),
            ('黑名单', lambda: self._check_blacklist(message_data.get('username'))),
        ]
        
        for check_name, check_func in checks:
            if not check_func():
                print(f"[Safety] ❌ {check_name} 检查失败")
                return False
                
        print("[Safety] ✅ 所有安全检查通过")
        return True
        
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
        
    def add_to_blacklist(self, username):
        """添加到黑名单"""
        blacklist = self.safety_config.get('blacklist', [])
        if username not in blacklist:
            blacklist.append(username)
            self.safety_config['blacklist'] = blacklist
            self._save_config()
            print(f"[Safety] 添加到黑名单: {username}")
            
    def remove_from_blacklist(self, username):
        """从黑名单移除"""
        blacklist = self.safety_config.get('blacklist', [])
        if username in blacklist:
            blacklist.remove(username)
            self.safety_config['blacklist'] = blacklist
            self._save_config()
            print(f"[Safety] 从黑名单移除: {username}")
            
    def add_to_whitelist(self, username):
        """添加到白名单"""
        whitelist = self.safety_config.get('whitelist', [])
        if username not in whitelist:
            whitelist.append(username)
            self.safety_config['whitelist'] = whitelist
            self._save_config()
            print(f"[Safety] 添加到白名单: {username}")
            
    def remove_from_whitelist(self, username):
        """从白名单移除"""
        whitelist = self.safety_config.get('whitelist', [])
        if username in whitelist:
            whitelist.remove(username)
            self.safety_config['whitelist'] = whitelist
            self._save_config()
            print(f"[Safety] 从白名单移除: {username}")
            
    def _save_config(self):
        """保存配置到文件"""
        rules_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'rules')
        safety_file = os.path.join(rules_dir, 'safety_rules.json')
        
        with open(safety_file, 'w', encoding='utf-8') as f:
            json.dump(self.safety_config, f, ensure_ascii=False, indent=2)
            
    def get_stats(self):
        """获取统计信息"""
        now = time.time()
        
        stats = {
            'sent_today': len(self.sent_records['day']),
            'sent_last_hour': len([t for t in self.sent_records['hour'] if now - t < 3600]),
            'sent_last_minute': len([t for t in self.sent_records['minute'] if now - t < 60]),
            'blacklist_count': len(self.safety_config.get('blacklist', [])),
            'whitelist_count': len(self.safety_config.get('whitelist', [])),
            'current_mode': 'simulate'  # 从config获取
        }
        
        return stats