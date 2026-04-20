"""
状态管理器
管理自动回复系统的运行状态
"""

import json
import os
import time
from datetime import datetime

class StateManager:
    """状态管理器"""
    
    def __init__(self, config=None):
        self.config = config or {}
        
        # 系统状态
        self.state_file = self.config.get('state_file', 'auto_reply_state.json')
        self.state = self._load_state()
        
        # 运行时状态
        self.runtime_state = {
            'start_time': time.time(),
            'last_message_time': 0,
            'message_count': 0,
            'reply_count': 0,
            'error_count': 0,
            'is_running': True
        }
        
        # 会话上下文（临时存储）
        self.conversation_context = {}
        
        print("[StateManager] 初始化完成")
        
    def _load_state(self):
        """加载持久化状态"""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                    print(f"[StateManager] 加载状态: {self.state_file}")
                    return state
            except Exception as e:
                print(f"[StateManager] 加载状态失败: {e}")
                
        # 默认状态
        default_state = {
            'version': '1.0',
            'created_at': datetime.now().isoformat(),
            'last_save': 0,
            'total_messages': 0,
            'total_replies': 0,
            'modes_used': {},
            'conversation_history': [],
            'settings': {
                'learning_enabled': True,
                'auto_save_interval': 300,  # 5分钟
                'max_history_length': 1000
            }
        }
        
        return default_state
        
    def save_state(self):
        """保存状态到文件"""
        # 更新状态
        self.state['last_save'] = time.time()
        self.state['total_messages'] = self.runtime_state.get('message_count', 0)
        self.state['total_replies'] = self.runtime_state.get('reply_count', 0)
        
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, ensure_ascii=False, indent=2)
            print(f"[StateManager] 状态已保存: {self.state_file}")
            return True
        except Exception as e:
            print(f"[StateManager] 保存状态失败: {e}")
            return False
            
    def record_message(self, message_data, reply_data=None):
        """记录消息"""
        self.runtime_state['message_count'] += 1
        self.runtime_state['last_message_time'] = time.time()
        
        # 记录到历史
        record = {
            'timestamp': time.time(),
            'datetime': datetime.now().isoformat(),
            'message': message_data,
            'reply': reply_data
        }
        
        self.state['conversation_history'].append(record)
        
        # 限制历史长度
        max_len = self.state['settings']['max_history_length']
        if len(self.state['conversation_history']) > max_len:
            self.state['conversation_history'] = self.state['conversation_history'][-max_len:]
            
        # 自动保存（每10条消息）
        if self.runtime_state['message_count'] % 10 == 0:
            self.save_state()
            
        print(f"[StateManager] 记录消息 #{self.runtime_state['message_count']}")
        
    def record_reply(self, reply_data):
        """记录回复"""
        self.runtime_state['reply_count'] += 1
        
        # 记录模式使用
        mode = reply_data.get('mode', 'simulate')
        if mode not in self.state['modes_used']:
            self.state['modes_used'][mode] = 0
        self.state['modes_used'][mode] += 1
        
        print(f"[StateManager] 记录回复 #{self.runtime_state['reply_count']}, 模式: {mode}")
        
    def record_error(self, error_data):
        """记录错误"""
        self.runtime_state['error_count'] += 1
        
        error_record = {
            'timestamp': time.time(),
            'error': error_data,
            'message_count': self.runtime_state['message_count']
        }
        
        if 'errors' not in self.state:
            self.state['errors'] = []
        self.state['errors'].append(error_record)
        
        print(f"[StateManager] 记录错误 #{self.runtime_state['error_count']}: {error_data}")
        
    def get_context(self, username):
        """获取对话上下文"""
        return self.conversation_context.get(username, {})
        
    def update_context(self, username, context_data):
        """更新对话上下文"""
        if username not in self.conversation_context:
            self.conversation_context[username] = {}
            
        self.conversation_context[username].update(context_data)
        
        # 清理过期的上下文（30分钟）
        current_time = time.time()
        for user in list(self.conversation_context.keys()):
            context = self.conversation_context[user]
            if 'last_update' in context:
                if current_time - context['last_update'] > 1800:  # 30分钟
                    del self.conversation_context[user]
                    
        # 更新时间戳
        self.conversation_context[username]['last_update'] = current_time
        
        print(f"[StateManager] 更新上下文: {username}")
        
    def clear_context(self, username=None):
        """清理上下文"""
        if username:
            if username in self.conversation_context:
                del self.conversation_context[username]
                print(f"[StateManager] 清理上下文: {username}")
        else:
            self.conversation_context.clear()
            print("[StateManager] 清理所有上下文")
            
    def get_runtime_stats(self):
        """获取运行时统计"""
        uptime = time.time() - self.runtime_state['start_time']
        
        stats = {
            'uptime_seconds': uptime,
            'uptime_human': self._format_uptime(uptime),
            'message_count': self.runtime_state['message_count'],
            'reply_count': self.runtime_state['reply_count'],
            'error_count': self.runtime_state['error_count'],
            'last_message_seconds': time.time() - self.runtime_state['last_message_time'] if self.runtime_state['last_message_time'] > 0 else -1,
            'is_running': self.runtime_state['is_running'],
            'context_count': len(self.conversation_context)
        }
        
        return stats
        
    def _format_uptime(self, seconds):
        """格式化运行时间"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m {secs}s"
        elif minutes > 0:
            return f"{minutes}m {secs}s"
        else:
            return f"{secs}s"
            
    def get_persistent_stats(self):
        """获取持久化统计"""
        stats = {
            'total_messages': self.state.get('total_messages', 0),
            'total_replies': self.state.get('total_replies', 0),
            'modes_used': self.state.get('modes_used', {}),
            'last_save': self.state.get('last_save', 0),
            'history_length': len(self.state.get('conversation_history', [])),
            'error_count': len(self.state.get('errors', [])),
            'created_at': self.state.get('created_at', '')
        }
        
        return stats
        
    def set_setting(self, key, value):
        """设置配置"""
        if 'settings' not in self.state:
            self.state['settings'] = {}
            
        self.state['settings'][key] = value
        self.save_state()
        
        print(f"[StateManager] 设置 {key} = {value}")
        
    def get_setting(self, key, default=None):
        """获取配置"""
        return self.state.get('settings', {}).get(key, default)
        
    def stop(self):
        """停止系统"""
        self.runtime_state['is_running'] = False
        self.save_state()
        
        print("[StateManager] 系统停止")
        
    def start(self):
        """启动系统"""
        self.runtime_state['is_running'] = True
        self.runtime_state['start_time'] = time.time()
        
        print("[StateManager] 系统启动")