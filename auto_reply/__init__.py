"""
微信自动回复机器人模块 - 增强版
支持群聊过滤和@我检测
"""

from .core.sender import WeChatSender
from .core.reply_engine import ReplyEngine
from .core.safety_controller_enhanced import SafetyControllerEnhanced
from .core.state_manager import StateManager
from .core.process_manager import ProcessManager

class AutoReplySystem:
    """自动回复系统主类 - 增强版"""
    
    def __init__(self, config=None):
        self.config = config or {}
        self.sender = WeChatSender(self.config)
        self.engine = ReplyEngine(self.config)
        self.safety = SafetyControllerEnhanced(self.config)
        self.state = StateManager(self.config)
        self.process = ProcessManager(self.config)
        
        # 运行模式
        self.mode = 'simulate'  # simulate/test/controlled/auto
        
        # 初始化状态
        self.is_initialized = False
        self.last_message = None
        
        # 启动前清理
        self._cleanup_before_start()
        
    def initialize(self):
        """初始化系统"""
        if self.is_initialized:
            return
            
        print("[AutoReply] 初始化系统...")
        
        # 加载规则
        self._load_rules()
        
        self.is_initialized = True
        print("[AutoReply] 系统初始化完成")
        
    def _load_rules(self):
        """加载规则配置"""
        import os
        import json
        
        rules_dir = os.path.join(os.path.dirname(__file__), 'rules')
        
        # 加载关键词
        keywords_file = os.path.join(rules_dir, 'keywords.json')
        if os.path.exists(keywords_file):
            with open(keywords_file, 'r', encoding='utf-8') as f:
                self.keywords = json.load(f)
        else:
            self.keywords = {}
            
        # 加载安全规则
        safety_file = os.path.join(rules_dir, 'safety_rules.json')
        if os.path.exists(safety_file):
            with open(safety_file, 'r', encoding='utf-8') as f:
                self.safety_rules = json.load(f)
        else:
            self.safety_rules = {}
            
        # 检查是否为群聊模式
        group_config = self.config.get('group', {})
        if not group_config.get('enabled', True):
            print("[AutoReply] ⚠️ 群聊总开关关闭，群聊消息将被忽略")
        elif group_config.get('reply_only_at_me', True):
            print("[AutoReply] ✅ 群聊模式: 只回复@我的消息")
        else:
            print("[AutoReply] ✅ 群聊模式: 回复所有群聊消息")
        
        # 检查进程管理器状态
        if self.process:
            print(f"[AutoReply] ✅ 进程管理器已启用")
            proc_config = self.process.process_config
            print(f"      启动前清理: {'✅ 开启' if proc_config['kill_before_start'] else '❌ 关闭'}")
            print(f"      强制杀死: {'✅ 开启' if proc_config['force_kill'] else '❌ 关闭'}")
    
    def _cleanup_before_start(self):
        """启动前清理进程"""
        if self.process and self.process.process_config.get('kill_before_start', True):
            print("[AutoReply] 🧹 启动前清理旧进程...")
            result = self.process.kill_all_bot_processes()
            
            if result['killed'] > 0:
                print(f"[AutoReply] ✅ 已清理 {result['killed']} 个旧进程")
            else:
                print(f"[AutoReply] ✅ 无需清理，系统干净")
            
    def handle_message(self, message_data):
        """
        处理新消息 - 增强版，支持群聊过滤
        
        Args:
            message_data: 消息数据字典，包含:
                - username: 发送者/群聊ID
                - content: 消息内容
                - timestamp: 时间戳
                - sender: 实际发送者（群聊时）
                - type: 消息类型（用于判断是否为群聊）
        """
        if not self.is_initialized:
            self.initialize()
            
        username = message_data.get('username', '')
        content = message_data.get('content', '')
        
        print(f"[AutoReply] 处理消息: {username}")
        print(f"          内容: {content[:50]}...")
        
        # 安全检查
        if not self.safety.check_message(message_data):
            print("[AutoReply] 安全检查未通过")
            return None
            
        # 生成回复
        reply = self.engine.generate_reply(message_data)
        
        # 如果是群聊，特殊处理
        if self.safety._is_group_chat(username):
            print(f"[AutoReply] 👥 群聊消息处理")
            
            # 检查是否@我
            is_at_me = self.safety._is_mentioned_in_message(content)
            if not is_at_me:
                print(f"[AutoReply] ⚠️ 群聊消息未@我，跳过回复")
                return None
            else:
                print(f"[AutoReply] ✅ 群聊消息@了我，继续处理")
        
        # 根据模式处理
        if self.mode == 'simulate':
            print(f"[AutoReply][模拟] 将回复: {reply}")
            return {"action": "simulate", "reply": reply, "is_group": self.safety._is_group_chat(username)}
            
        elif self.mode == 'test':
            # 只发送给测试联系人
            if username in self.config.get('test_contacts', []):
                success = self.sender.send_message(
                    username, 
                    reply,
                    mode='test'
                )
                return {"action": "test", "success": success, "reply": reply, "is_group": self.safety._is_group_chat(username)}
            else:
                print(f"[AutoReply] ⚠️ 非测试联系人 ({username})，不发送")
                return None
                
        elif self.mode in ['controlled', 'auto']:
            # 后续实现
            print(f"[AutoReply] ⚠️ 模式 {self.mode} 暂未完全实现")
            
            # 受控模式下检查白名单
            if self.mode == 'controlled':
                whitelist = self.config.get('whitelist', [])
                if username not in whitelist:
                    print(f"[AutoReply] ❌ 不在白名单中 ({username})，不发送")
                    return None
            
            # 实际发送
            success = self.sender.send_message(
                username, 
                reply,
                mode=self.mode
            )
            return {"action": self.mode, "success": success, "reply": reply, "is_group": self.safety._is_group_chat(username)}
            
        return None
        
    def set_mode(self, mode):
        """设置运行模式"""
        valid_modes = ['simulate', 'test', 'controlled', 'auto']
        if mode in valid_modes:
            self.mode = mode
            print(f"[AutoReply] 模式设置为: {mode}")
            return True
        else:
            print(f"[AutoReply] 无效模式: {mode}")
            return False
    
    # 群聊管理方法
    def enable_group_reply(self, enable=True):
        """启用或禁用群聊回复"""
        return self.safety.enable_group_reply(enable)
    
    def set_reply_only_at_me(self, only_at_me=True):
        """设置是否只回复@我的消息"""
        return self.safety.set_reply_only_at_me(only_at_me)
    
    def add_group_to_blacklist(self, group_username, reason=''):
        """添加群聊到黑名单"""
        return self.safety.add_group_to_blacklist(group_username, reason)
    
    def remove_group_from_blacklist(self, group_username):
        """从黑名单移除群聊"""
        return self.safety.remove_group_from_blacklist(group_username)
    
    def add_group_to_whitelist(self, group_username, reason=''):
        """添加群聊到白名单"""
        return self.safety.add_group_to_whitelist(group_username, reason)
    
    def remove_group_from_whitelist(self, group_username):
        """从白名单移除群聊"""
        return self.safety.remove_group_from_whitelist(group_username)
    
    def get_group_stats(self):
        """获取群聊统计信息"""
        stats = self.safety.get_stats()
        return {
            'enabled': stats.get('group_enabled', True),
            'reply_only_at_me': stats.get('reply_only_at_me', True),
            'blacklist_count': stats.get('group_blacklist_count', 0),
            'whitelist_count': stats.get('group_whitelist_count', 0)
        }
    
    # 进程管理方法
    def cleanup_old_processes(self):
        """清理所有旧进程"""
        if self.process:
            return self.process.kill_all_bot_processes()
        return {'total_found': 0, 'killed': 0, 'failed': 0}
    
    def ensure_single_instance(self):
        """确保单实例运行"""
        if self.process:
            return self.process.ensure_single_instance()
        return True
    
    def get_process_stats(self):
        """获取进程统计信息"""
        if self.process:
            result = self.process.kill_all_bot_processes()
            return {
                'killed': result['killed'],
                'failed': result['failed'],
                'total': result['total_found']
            }
        return {'killed': 0, 'failed': 0, 'total': 0}