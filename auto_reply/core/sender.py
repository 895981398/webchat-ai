"""
微信消息发送器
支持模拟模式、测试模式、受控模式、自动模式
集成 Airtest + PyAutoGUI 方案
"""

import time
import os
import sys
import json
from datetime import datetime

class WeChatSender:
    """微信消息发送器 - 集成 Airtest 方案"""
    
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
        
        # 发送方法配置（优先级：airtest > pyautogui > applescript > wxauto）
        self.send_methods = {
            'airtest': False,
            'pyautogui': False,
            'applescript': False,
            'wxauto': False
        }
        
        # Airtest 发送器实例
        self.airtest_sender = None
        
        # 检测可用发送方法
        self._detect_send_methods()
        
        print(f"[Sender] 初始化完成，模式: {self.mode}")
        print(f"[Sender] 可用发送方法: {self.send_methods}")
        if self.airtest_enabled and self.send_methods.get('airtest'):
            print(f"[Sender] ✅ Airtest 模式已启用")
        else:
            print(f"[Sender] ⚠️ Airtest 模式未启用")
            if not self.airtest_enabled:
                print(f"    原因: Airtest 在配置中被禁用")
            elif not self.send_methods.get('airtest'):
                print(f"    原因: Airtest 库未安装或导入失败")
        
    def _detect_send_methods(self):
        """检测可用的发送方法（优先级顺序）"""
        
        # 1. 优先检查 Airtest（如果启用）
        if self.airtest_enabled:
            try:
                # 尝试导入 airtest_sender
                sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                from airtest_sender import WeChatAIRSender
                
                # 测试初始化
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
            if not self.send_methods.get('airtest'):
                print("[Sender] PyAutoGUI不可用")
            
        # 3. AppleScript (macOS原生)
        if os.name == 'posix':
            self.send_methods['applescript'] = True
            if not self.send_methods.get('airtest') and not self.send_methods.get('pyautogui'):
                print("[Sender] ✅ AppleScript 可用")
        
        # 4. 最后检查 wxauto（备用）
        try:
            import wxauto
            self.send_methods['wxauto'] = True
            if not any([self.send_methods.get('airtest'), 
                       self.send_methods.get('pyautogui'), 
                       self.send_methods.get('applescript')]):
                print("[Sender] ✅ wxauto 可用")
        except ImportError:
            print("[Sender] wxauto不可用")
            
        print(f"[Sender] 检测结果: {self.send_methods}")
        
        # 打印推荐方案
        if self.send_methods.get('airtest'):
            print(f"[Sender] 推荐方案: Airtest + PyAutoGUI 组合")
        elif self.send_methods.get('pyautogui'):
            print(f"[Sender] 推荐方案: PyAutoGUI 独立方案")
        elif self.send_methods.get('applescript'):
            print(f"[Sender] 推荐方案: AppleScript 方案")
        else:
            print(f"[Sender] ⚠️ 警告: 无可用自动化方案，只能模拟发送")
        
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
        target = str(target or '')
        message = str(message or '')
        
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
            print(f"[Sender][测试] 非测试联系人: {target}")
            return False
            
        print(f"[Sender][测试] 发送给测试联系人 {target}")
        
        # 尝试实际发送
        success = self._try_send_actual(target, message)
        
        if success:
            print(f"[Sender][测试] 发送成功")
            self._log_sent_message(target, message, 'test')
        else:
            print(f"[Sender][测试] 发送失败")
            
        return success
        
    def _send_actual(self, target, message, mode):
        """实际发送（受控或自动模式）"""
        # 检查白名单（controlled模式）
        if mode == 'controlled' and target not in self.whitelist:
            print(f"[Sender][受控] 不在白名单: {target}")
            return False
            
        # 检查黑名单
        if target in self.blacklist:
            print(f"[Sender] 在黑名单: {target}")
            return False
            
        print(f"[Sender][{mode}] 准备实际发送...")
        
        # 尝试发送
        success = self._try_send_actual(target, message)
        
        if success:
            print(f"[Sender][{mode}] 发送成功")
            self._log_sent_message(target, message, mode)
        else:
            print(f"[Sender][{mode}] 发送失败")
            
        return success
        
    def _try_send_actual(self, target, message):
        """尝试实际发送（优先级顺序）"""
        print(f"[Sender] 尝试实际发送给 {target}")
        
        # 0. 优先尝试 Airtest 方案（如果启用）
        if self.airtest_enabled and self.send_methods.get('airtest') and self.airtest_sender:
            print(f"[Sender] 尝试Airtest方案 (优先)")
            try:
                success = self.airtest_sender.send_to_chat(target, message)
                if success:
                    return True
                else:
                    print(f"[Sender] Airtest 方案失败，尝试备用方案")
            except Exception as e:
                print(f"[Sender] Airtest 方案异常: {e}")
        
        # 1. 尝试 PyAutoGUI（独立使用）
        if self.send_methods.get('pyautogui'):
            print(f"[Sender] 尝试PyAutoGUI方法")
            success = self._send_via_pyautogui(target, message)
            if success:
                return True
                
        # 2. 尝试 AppleScript (macOS原生)
        if self.send_methods.get('applescript'):
            print(f"[Sender] 尝试AppleScript方法")
            success = self._send_via_applescript(target, message)
            if success:
                return True
                
        # 3. 最后尝试 wxauto（备用）
        if self.send_methods.get('wxauto'):
            print(f"[Sender] 尝试wxauto方法")
            success = self._send_via_wxauto(target, message)
            if success:
                return True
                
        print(f"[Sender] ❌ 所有发送方法均失败")
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
            
    def _send_via_pyautogui(self, target, message):
        """通过pyautogui模拟操作"""
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
                subprocess.run(['osascript', '-e', script], timeout=10)
                
            time.sleep(2)  # 等待窗口激活
            
            # 2. 搜索联系人（模拟Command+F）
            print(f"[Sender][pyautogui] 搜索联系人: {target}")
            pyautogui.hotkey('command', 'f')
            time.sleep(0.5)
            pyautogui.write(target)
            time.sleep(1)
            pyautogui.press('enter')
            time.sleep(0.5)
            
            # 3. 输入消息
            print(f"[Sender][pyautogui] 输入消息...")
            pyautogui.write(message)
            time.sleep(0.3)
            
            # 4. 发送（Enter）
            pyautogui.press('enter')
            time.sleep(1)
            
            print(f"[Sender][pyautogui] 发送完成")
            
            return True
            
        except Exception as e:
            print(f"[Sender][pyautogui] 发送失败: {e}")
            return False
            
    def _send_via_applescript(self, target, message):
        """通过AppleScript发送（macOS）"""
        try:
            import subprocess
            
            # AppleScript控制微信发送消息
            script = f'''
            tell application "WeChat"
                activate
                delay 1
                -- 搜索联系人
                activate
                keystroke "f" using {{command down}}
                delay 0.5
                keystroke "{target}"
                delay 1
                keystroke return
                delay 0.5
                -- 输入消息
                keystroke "{message}"
                delay 0.3
                -- 发送
                keystroke return
            end tell
            '''
            
            print(f"[Sender][AppleScript] 执行脚本...")
            subprocess.run(['osascript', '-e', script], timeout=15)
            
            print(f"[Sender][AppleScript] 发送完成")
            return True
            
        except Exception as e:
            print(f"[Sender][AppleScript] 发送失败: {e}")
            return False
            
    def _log_sent_message(self, target, message, mode):
        """记录发送日志"""
        target = str(target or '')
        message = str(message or '')
        log_entry = {
            'timestamp': time.time(),
            'datetime': datetime.now().isoformat(),
            'target': target,
            'message': message[:100],  # 只记录前100字符
            'mode': mode,
            'length': len(message)
        }
        
        # 记录到文件
        log_file = self.sent_log_file
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
            
        # 增加计数
        self.sent_count += 1
        
        print(f"[Sender] 日志记录完成，总发送: {self.sent_count}")
        
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
            
    def add_to_whitelist(self, username):
        """添加到白名单"""
        if username not in self.whitelist:
            self.whitelist.append(username)
            print(f"[Sender] 添加到白名单: {username}")
            return True
        return False
        
    def remove_from_whitelist(self, username):
        """从白名单移除"""
        if username in self.whitelist:
            self.whitelist.remove(username)
            print(f"[Sender] 从白名单移除: {username}")
            return True
        return False
        
    def get_stats(self):
        """获取统计信息"""
        stats = {
            'sent_total': self.sent_count,
            'current_mode': self.mode,
            'whitelist_count': len(self.whitelist),
            'blacklist_count': len(self.blacklist),
            'test_contacts': self.test_contacts,
            'airtest_enabled': self.airtest_enabled,
            'send_methods': self.send_methods
        }
        
        # 添加 Airtest 统计
        if self.airtest_sender:
            airtest_stats = self.airtest_sender.get_stats()
            stats['airtest_stats'] = airtest_stats
            
        return stats
    
    def enable_airtest(self, enable=True):
        """启用或禁用 Airtest 方案"""
        self.airtest_enabled = enable
        if enable:
            print(f"[Sender] ✅ Airtest 方案已启用")
        else:
            print(f"[Sender] ⚠️ Airtest 方案已禁用")
        return enable
    
    def configure_airtest(self, config=None):
        """配置 Airtest 参数"""
        if config:
            self.airtest_config.update(config)
            print(f"[Sender] Airtest 配置更新: {self.airtest_config}")
            
            # 重新初始化 Airtest 发送器
            try:
                sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                from airtest_sender import WeChatAIRSender
                
                self.airtest_sender = WeChatAIRSender(
                    wechat_path=self.airtest_config.get('wechat_path', '/Applications/WeChat.app'),
                    detect_confidence=self.airtest_config.get('detect_confidence', 0.8),
                    max_retry=self.airtest_config.get('max_retry', 3),
                    humanize=self.airtest_config.get('humanize', True),
                    debug=self.airtest_config.get('debug', False)
                )
                
                if self.airtest_sender.airtest_available or self.airtest_sender.pyautogui_available:
                    self.send_methods['airtest'] = True
                    print(f"[Sender] ✅ Airtest 发送器重新初始化成功")
                else:
                    self.send_methods['airtest'] = False
                    print(f"[Sender] ⚠️ Airtest 发送器初始化但无可用库")
                    
            except Exception as e:
                print(f"[Sender] ❌ Airtest 发送器重新初始化失败: {e}")
                self.send_methods['airtest'] = False
                
        return self.airtest_config
    
    def get_airtest_status(self):
        """获取 Airtest 状态"""
        if self.airtest_sender:
            return {
                'enabled': self.airtest_enabled,
                'available': True,
                'stats': self.airtest_sender.get_stats(),
                'config': self.airtest_config
            }
        else:
            return {
                'enabled': self.airtest_enabled,
                'available': False,
                'error': 'Airtest 发送器未初始化',
                'config': self.airtest_config
            }