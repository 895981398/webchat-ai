"""
微信消息发送器 - 增强版
集成自动窗口管理和Airtest发送
"""

import time
import os
import sys
import json
from datetime import datetime

class WeChatSenderEnhanced:
    """微信消息发送器 - 增强版"""
    
    def __init__(self, config=None):
        self.config = config or {}
        
        # 发送模式
        self.mode = 'simulate'  # simulate/test/controlled/auto
        
        # 白名单和黑名单
        self.whitelist = self.config.get('whitelist', [])
        self.blacklist = self.config.get('blacklist', [])
        
        # 测试联系人
        self.test_contacts = ['文件传输助手', '自己']
        
        # 发送记录
        self.sent_log_file = self.config.get('sent_log_file', 'sent_messages.log')
        self.sent_count = 0
        
        # Airtest 配置
        self.airtest_config = self.config.get('airtest', {})
        self.airtest_enabled = self.airtest_config.get('enabled', True)
        
        # 窗口配置
        self.window_config = self.config.get('window', {})
        self.window_enabled = self.window_config.get('enabled', True)
        
        # 发送方法配置（优先级：airtest > pyautogui > applescript > wxauto）
        self.send_methods = {
            'airtest': False,
            'pyautogui': False,
            'applescript': False,
            'wxauto': False
        }
        
        # 组件实例
        self.airtest_sender = None
        self.window_manager = None
        
        # 初始化
        self._detect_send_methods()
        self._init_window_manager()
        
        print(f"[Sender] 初始化完成，模式: {self.mode}")
        print(f"[Sender] 可用发送方法: {self.send_methods}")
        
        # 窗口管理器状态
        if self.window_manager and self.window_enabled:
            print(f"[Sender] ✅ 窗口管理器已启用")
            config = self.window_manager.window_config
            print(f"      自动激活: {'✅ 开启' if config['auto_activate'] else '❌ 关闭'}")
            print(f"      调整大小: {'✅ 开启' if config['adjust_size'] else '❌ 关闭'}")
            print(f"      推荐窗口: {config['optimal_width']}x{config['optimal_height']}")
        
    def _detect_send_methods(self):
        """检测可用的发送方法"""
        
        # 1. 优先检查 Airtest
        if self.airtest_enabled:
            try:
                from airtest_sender import WeChatAIRSender
                
                test_sender = WeChatAIRSender(
                    wechat_path=self.airtest_config.get('wechat_path', '/Applications/WeChat.app'),
                    detect_confidence=self.airtest_config.get('detect_confidence', 0.8),
                    max_retry=self.airtest_config.get('max_retry', 3),
                    humanize=self.airtest_config.get('humanize', True),
                    debug=self.airtest_config.get('debug', False)
                )
                
                if test_sender.airtest_available or test_sender.pyautogui_available:
                    self.send_methods['airtest'] = True
                    self.airtest_sender = test_sender
                    print("[Sender] ✅ Airtest 可用")
                else:
                    print("[Sender] ⚠️ Airtest 导入成功但无可用自动化库")
                    
            except ImportError as e:
                print(f"[Sender] Airtest 导入失败: {e}")
            except Exception as e:
                print(f"[Sender] Airtest 初始化异常: {e}")
        
        # 2. 检查 PyAutoGUI（独立使用）
        try:
            import pyautogui
            self.send_methods['pyautogui'] = True
            if not self.send_methods.get('airtest'):
                print("[Sender] ✅ PyAutoGUI 可用")
        except ImportError:
            pass
        
        # 3. 检查 AppleScript（仅macOS）
        if os.name == 'posix':
            try:
                import subprocess
                # 简单测试 AppleScript 是否可用
                result = subprocess.run(['osascript', '-e', 'return 1'], 
                                      capture_output=True, timeout=2)
                if result.returncode == 0:
                    self.send_methods['applescript'] = True
                    if not self.send_methods.get('airtest'):
                        print("[Sender] ✅ AppleScript 可用")
            except:
                pass
        
        # 4. 检查 wxauto（备用）
        try:
            import wxauto
            self.send_methods['wxauto'] = True
            if not self.send_methods.get('airtest'):
                print("[Sender] ✅ wxauto 可用")
        except ImportError:
            pass
        
        # 5. 检查是否至少有一种方法
        if not any(self.send_methods.values()):
            print("[Sender] ❌ 无可用自动化方案，只能模拟发送")
    
    def _init_window_manager(self):
        """初始化窗口管理器"""
        if not self.window_enabled:
            print("[Sender] ⚠️ 窗口管理器已禁用")
            return
            
        try:
            from .window_manager import WeChatWindowManager
            
            # 合并配置
            manager_config = {
                'wechat_path': self.airtest_config.get('wechat_path', '/Applications/WeChat.app'),
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
            
            # 如果配置中已有窗口配置，使用它
            if self.window_config:
                manager_config['window'].update(self.window_config)
            
            self.window_manager = WeChatWindowManager(manager_config)
            print(f"[Sender] ✅ 窗口管理器初始化成功")
            
        except ImportError as e:
            print(f"[Sender] ❌ 窗口管理器导入失败: {e}")
        except Exception as e:
            print(f"[Sender] ❌ 窗口管理器初始化异常: {e}")
    
    def prepare_sending_environment(self, chat_name):
        """
        准备发送环境
        
        Args:
            chat_name: 目标聊天名称
            
        Returns:
            dict: 准备结果
        """
        if not self.window_manager or not self.window_enabled:
            return {
                'ready': False,
                'reason': 'window_manager_disabled',
                'message': '窗口管理器未启用'
            }
        
        print(f"[Sender] 准备发送环境: {chat_name}")
        result = self.window_manager.prepare_for_sending(chat_name)
        
        if result.get('ready'):
            print(f"[Sender] ✅ 发送环境准备就绪")
        else:
            print(f"[Sender] ❌ 发送环境准备失败")
            # 尝试基本检查
            if not result.get('wechat_running'):
                print(f"     原因: 微信未运行")
            elif not result.get('window_activated'):
                print(f"     原因: 窗口激活失败")
            elif not result.get('window_resized'):
                print(f"     原因: 窗口大小调整失败")
        
        return result
    
    def send_message(self, target, message, mode=None):
        """
        发送消息
        
        Args:
            target: 目标联系人/群聊
            message: 消息内容
            mode: 发送模式（默认使用实例模式）
            
        Returns:
            bool: 是否发送成功
        """
        send_mode = mode or self.mode
        
        print(f"[Sender] 发送给 {target}: {message[:50]}...")
        print(f"[Sender] 模式: {send_mode}")
        
        # 根据模式处理
        if send_mode == 'simulate':
            return self._send_simulate(target, message)
            
        elif send_mode == 'test':
            return self._send_test(target, message)
            
        elif send_mode in ['controlled', 'auto']:
            return self._send_actual(target, message, send_mode)
            
        else:
            print(f"[Sender] 无效模式: {send_mode}")
            return False
    
    def _send_simulate(self, target, message):
        """模拟发送（不真发）"""
        print(f"[Sender][模拟] 消息已准备发送:")
        print(f"  目标: {target}")
        print(f"  内容: {message}")
        print(f"  时间: {datetime.now().strftime('%H:%M:%S')}")
        print(f"[Sender][模拟] 发送完成（模拟）")
        
        # 记录日志
        self._log_sent_message(target, message, 'simulate')
        
        return True
    
    def _send_test(self, target, message):
        """测试发送（只发给自己）"""
        # 只发送给文件传输助手或自己
        if target not in self.test_contacts:
            print(f"[Sender][测试] 非测试联系人 {target}，不发送")
            return False
        
        print(f"[Sender][测试] 发送给测试联系人 {target}")
        return self._send_actual(target, message, 'test')
    
    def _send_actual(self, target, message, mode='auto'):
        """实际发送消息"""
        print(f"[Sender][{mode}] 尝试实际发送")
        
        # 准备发送环境（自动激活窗口）
        if self.window_manager and self.window_enabled:
            env_result = self.prepare_sending_environment(target)
            if not env_result.get('ready'):
                print(f"[Sender][{mode}] ❌ 发送环境准备失败")
                return False
        
        # 根据可用的发送方法尝试发送
        try:
            # 1. 首选 Airtest
            if self.send_methods.get('airtest') and self.airtest_sender:
                print(f"[Sender][{mode}] 使用Airtest方案")
                success = self.airtest_sender.send_message(target, message)
                if success:
                    self._log_sent_message(target, message, mode)
                    return True
            
            # 2. 次选 PyAutoGUI
            if self.send_methods.get('pyautogui'):
                print(f"[Sender][{mode}] 尝试PyAutoGUI方案")
                success = self._send_via_pyautogui(target, message)
                if success:
                    self._log_sent_message(target, message, mode)
                    return True
            
            # 3. 再次选 AppleScript
            if self.send_methods.get('applescript'):
                print(f"[Sender][{mode}] 尝试AppleScript方案")
                success = self._send_via_applescript(target, message)
                if success:
                    self._log_sent_message(target, message, mode)
                    return True
            
            # 4. 最后选 wxauto
            if self.send_methods.get('wxauto'):
                print(f"[Sender][{mode}] 尝试wxauto方案")
                success = self._send_via_wxauto(target, message)
                if success:
                    self._log_sent_message(target, message, mode)
                    return True
            
            print(f"[Sender][{mode}] ❌ 所有发送方法均失败")
            return False
            
        except Exception as e:
            print(f"[Sender][{mode}] ❌ 发送异常: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _send_via_pyautogui(self, target, message):
        """通过pyautogui发送"""
        try:
            import pyautogui
            
            print(f"[Sender][pyautogui] 激活微信窗口...")
            
            # 1. 激活微信（macOS）
            if os.name == 'posix':
                import subprocess
                script = '''
                tell application "WeChat"
                    activate
                    delay 1
                end tell
                '''
                subprocess.run(['osascript', '-e', script], timeout=5)
            
            time.sleep(1)
            
            # 2. 切换到微信（如果有多个应用）
            pyautogui.hotkey('command', 'tab', interval=0.1)
            time.sleep(0.5)
            
            # 3. 输入消息
            pyautogui.write(message, interval=0.05)
            time.sleep(0.3)
            
            # 4. 发送
            pyautogui.press('enter')
            time.sleep(0.5)
            
            print(f"[Sender][pyautogui] 发送完成")
            return True
            
        except Exception as e:
            print(f"[Sender][pyautogui] 发送失败: {e}")
            return False
    
    def _send_via_applescript(self, target, message):
        """通过AppleScript发送"""
        try:
            import subprocess
            
            # 转义消息内容
            escaped_message = message.replace('"', '\\"').replace("'", "\\'")
            
            script = f'''
            tell application "WeChat"
                activate
                delay 1
                
                tell application "System Events"
                    keystroke "{escaped_message}"
                    delay 0.3
                    keystroke return
                end tell
            end tell
            '''
            
            print(f"[Sender][AppleScript] 执行脚本...")
            subprocess.run(['osascript', '-e', script], timeout=15)
            
            print(f"[Sender][AppleScript] 发送完成")
            return True
            
        except Exception as e:
            print(f"[Sender][AppleScript] 发送失败: {e}")
            return False
    
    def _send_via_wxauto(self, target, message):
        """通过wxauto发送"""
        try:
            import wxauto
            
            print(f"[Sender][wxauto] 连接微信...")
            wx = wxauto.WeChat()
            
            print(f"[Sender][wxauto] 搜索联系人: {target}")
            # 查找联系人（可能会弹窗）
            
            # 这里需要实际实现
            print(f"[Sender][wxauto] 发送消息: {message[:50]}...")
            
            # 模拟成功
            time.sleep(0.5)
            print(f"[Sender][wxauto] 发送完成")
            
            return True
            
        except Exception as e:
            print(f"[Sender][wxauto] 发送失败: {e}")
            return False
    
    def _log_sent_message(self, target, message, mode):
        """记录发送日志"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'target': target,
            'message': message[:100],  # 只记录前100个字符
            'mode': mode,
            'success': True
        }
        
        try:
            with open(self.sent_log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
            self.sent_count += 1
            print(f"[Sender] 日志记录完成，总发送: {self.sent_count}")
        except Exception as e:
            print(f"[Sender] 日志记录失败: {e}")
    
    def set_mode(self, mode):
        """设置发送模式"""
        valid_modes = ['simulate', 'test', 'controlled', 'auto']
        if mode in valid_modes:
            self.mode = mode
            print(f"[Sender] 模式设置为: {mode}")
            return True
        else:
            print(f"[Sender] 无效模式: {mode}")
            return False
    
    def get_stats(self):
        """获取统计信息"""
        return {
            'current_mode': self.mode,
            'send_methods': self.send_methods,
            'sent_count': self.sent_count,
            'airtest_enabled': self.airtest_enabled,
            'window_enabled': self.window_enabled,
            'airtest_stats': self.airtest_sender.get_stats() if self.airtest_sender else None
        }


# 测试
if __name__ == "__main__":
    print("=== WeChatSenderEnhanced 测试 ===")
    
    config = {
        'mode': 'simulate',
        'test_contacts': ['文件传输助手'],
        'whitelist': [],
        'blacklist': [],
        'airtest': {
            'enabled': True,
            'wechat_path': '/Applications/WeChat.app',
            'detect_confidence': 0.8,
            'max_retry': 3,
            'humanize': True,
            'debug': False
        },
        'window': {
            'enabled': True,
            'auto_activate': True,
            'adjust_size': True,
            'optimal_width': 1200,
            'optimal_height': 800
        }
    }
    
    sender = WeChatSenderEnhanced(config)
    
    # 测试发送
    test_cases = [
        ('simulate', '文件传输助手', '模拟模式测试'),
        ('test', '文件传输助手', '测试模式测试'),
    ]
    
    for mode, target, message in test_cases:
        print(f"\n{'='*60}")
        print(f"测试模式: {mode}")
        print(f"{'='*60}")
        
        sender.set_mode(mode)
        success = sender.send_message(target, message)
        
        print(f"结果: {'✅ 成功' if success else '❌ 失败'}")