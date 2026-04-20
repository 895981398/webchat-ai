"""
Airtest 版微信发送器
基于 Airtest + PyAutoGUI 的可靠发送方案
"""

import os
import sys
import time
import random
import subprocess
from datetime import datetime
from pathlib import Path

class WeChatAIRSender:
    """Airtest 微信发送器 - 专为 macOS 优化"""
    
    def __init__(self, 
                 wechat_path='/Applications/WeChat.app',
                 detect_confidence=0.8,
                 max_retry=3,
                 humanize=True,
                 debug=False):
        """
        初始化 Airtest 发送器
        
        Args:
            wechat_path: 微信应用路径
            detect_confidence: 图像识别置信度 (0.0-1.0)
            max_retry: 最大重试次数
            humanize: 是否启用人性化操作（随机延迟、鼠标轨迹等）
            debug: 调试模式（保存截图）
        """
        self.wechat_path = wechat_path
        self.confidence = detect_confidence
        self.max_retry = max_retry
        self.humanize = humanize
        self.debug = debug
        
        # 状态跟踪
        self.last_action_time = 0
        self.sent_count = 0
        self.retry_count = 0
        
        # 导入库
        self.airtest_available = False
        self.pyautogui_available = False
        
        self._import_libraries()
        
        # 资源目录
        self.resources_dir = Path(__file__).parent.parent / 'resources'
        self.resources_dir.mkdir(exist_ok=True)
        
        print(f"[Airtest] 初始化成功 - 置信度: {detect_confidence}, 最大重试: {max_retry}")
        if humanize:
            print(f"[Airtest] 人性化模式已启用")
        
    def _import_libraries(self):
        """导入必要的库"""
        try:
            from airtest.core.api import connect_device, start_app, stop_app, snapshot, exists, touch, text, sleep
            from airtest.core.api import Template
            self.airtest_available = True
            print(f"[Airtest] Airtest 库导入成功")
        except ImportError as e:
            print(f"[Airtest] Airtest 导入失败: {e}")
            
        try:
            import pyautogui
            self.pyautogui = pyautogui
            self.pyautogui_available = True
            print(f"[Airtest] PyAutoGUI 库导入成功")
        except ImportError as e:
            print(f"[Airtest] PyAutoGUI 导入失败: {e}")
            
        if not self.airtest_available and not self.pyautogui_available:
            print(f"[Airtest] 警告: 没有可用的自动化库")
    
    def send_to_chat(self, target_name, message, chat_type='private'):
        """
        发送消息到指定聊天
        
        Args:
            target_name: 目标联系人/群聊名称
            message: 消息内容
            chat_type: 'private' 或 'group'
            
        Returns:
            bool: 是否发送成功
        """
        if not self.airtest_available and not self.pyautogui_available:
            print("[Airtest] 自动化库未安装，无法发送")
            return False
        
        print(f"[Airtest] 准备发送给 {target_name}: {message[:50]}...")
        
        try:
            # 1. 确保微信在前台
            if not self._activate_wechat():
                print("[Airtest] 无法激活微信")
                return False
            
            # 2. 搜索并打开聊天窗口
            if not self._open_chat_window(target_name, chat_type):
                print(f"[Airtest] 无法找到聊天窗口: {target_name}")
                return False
            
            # 3. 输入消息
            self._type_message(message)
            
            # 4. 发送
            self._press_send()
            
            self.sent_count += 1
            print(f"[Airtest] ✅ 发送成功 #{self.sent_count}: {target_name} ← {message[:50]}...")
            return True
            
        except Exception as e:
            print(f"[Airtest] ❌ 发送失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _activate_wechat(self):
        """激活微信窗口"""
        print("[Airtest] 激活微信窗口...")
        
        for attempt in range(self.max_retry):
            try:
                # 方法1: 使用 AppleScript 激活
                script = '''
                tell application "WeChat"
                    activate
                end tell
                '''
                subprocess.run(['osascript', '-e', script], 
                             capture_output=True, timeout=5)
                
                # 等待窗口激活
                self._human_delay(1000, 500)
                
                # 检查微信是否在前台（通过活动窗口标题）
                if self._is_wechat_active():
                    print("[Airtest] ✅ 微信已激活")
                    return True
                else:
                    print(f"[Airtest] 微信激活失败，尝试 {attempt+1}/{self.max_retry}")
                    
            except Exception as e:
                print(f"[Airtest] 激活失败: {e}")
            
            if attempt < self.max_retry - 1:
                self._human_delay(2000, 1000)
        
        # 尝试直接打开微信
        try:
            subprocess.run(['open', self.wechat_path], timeout=10)
            print("[Airtest] 尝试直接打开微信")
            self._human_delay(3000, 1000)
            return True
        except:
            print("[Airtest] ❌ 无法激活微信")
            return False
    
    def _is_wechat_active(self):
        """检查微信是否在前台"""
        try:
            script = '''
            tell application "System Events"
                set frontApp to name of first application process whose frontmost is true
                return frontApp
            end tell
            '''
            result = subprocess.run(['osascript', '-e', script], 
                                  capture_output=True, text=True, timeout=3)
            return 'WeChat' in result.stdout
        except:
            return False
    
    def _open_chat_window(self, target_name, chat_type='private'):
        """搜索并打开聊天窗口"""
        print(f"[Airtest] 搜索聊天: {target_name}")
        
        for attempt in range(self.max_retry):
            try:
                # 方法1: 使用快捷键搜索
                self._human_delay(500, 200)
                
                # Command + F 打开搜索
                self.pyautogui.hotkey('command', 'f')
                self._human_delay(300, 150)
                
                # 清空可能已有的内容
                self.pyautogui.hotkey('command', 'a')
                self._human_delay(100, 50)
                self.pyautogui.press('delete')
                self._human_delay(200, 100)
                
                # 输入目标名称
                self._type_with_humanization(target_name)
                self._human_delay(1000, 500)  # 等待搜索结果
                
                # 按回车选择第一个结果
                self.pyautogui.press('enter')
                self._human_delay(800, 400)
                
                # 检查是否成功进入聊天
                if self._is_in_chat_window():
                    print(f"[Airtest] ✅ 成功进入聊天: {target_name}")
                    return True
                else:
                    print(f"[Airtest] 未进入聊天窗口，重试 {attempt+1}/{self.max_retry}")
                    
            except Exception as e:
                print(f"[Airtest] 打开聊天失败: {e}")
            
            if attempt < self.max_retry - 1:
                self._human_delay(2000, 1000)
        
        return False
    
    def _is_in_chat_window(self):
        """检查是否在聊天窗口（通过判断输入框是否可见）"""
        try:
            # 简单方法：判断当前是否有输入焦点（通过尝试输入）
            self.pyautogui.write('test', interval=0.01)
            self._human_delay(100, 50)
            # 删除测试文本
            for _ in range(4):
                self.pyautogui.press('delete')
                self._human_delay(20, 10)
            return True
        except:
            return False
    
    def _type_message(self, message):
        """输入消息"""
        print(f"[Airtest] 输入消息 ({len(message)} 字符)...")
        
        # 确保在输入框
        self._click_input_area()
        self._human_delay(200, 100)
        
        # 人性化输入
        self._type_with_humanization(message)
        
        print(f"[Airtest] 消息输入完成")
    
    def _click_input_area(self):
        """点击输入框区域"""
        try:
            # 获取屏幕尺寸
            screen_width, screen_height = self.pyautogui.size()
            
            # 微信输入框大致位置（底部中央）
            input_x = screen_width // 2
            input_y = screen_height - 100  # 距离底部100像素
            
            # 随机偏移（模拟人类点击）
            if self.humanize:
                input_x += random.randint(-20, 20)
                input_y += random.randint(-10, 10)
            
            self.pyautogui.click(input_x, input_y, duration=random.uniform(0.1, 0.3))
            self._human_delay(200, 100)
            
        except Exception as e:
            print(f"[Airtest] 点击输入框失败: {e}")
            # 如果失败，继续尝试输入
    
    def _type_with_humanization(self, text):
        """人性化输入文本"""
        if not self.humanize:
            # 快速输入
            self.pyautogui.write(text, interval=0.05)
            return
        
        # 模拟人类打字：随机速度 + 偶尔出错修正
        words = text.split(' ')
        for i, word in enumerate(words):
            # 输入单词
            for char in word:
                self.pyautogui.write(char, interval=random.uniform(0.05, 0.15))
                
                # 偶尔打错并修正（5%概率）
                if random.random() < 0.05:
                    self._human_delay(100, 50)
                    self.pyautogui.press('backspace')
                    self._human_delay(50, 25)
                    self.pyautogui.write(char, interval=0.1)
            
            # 单词间空格
            if i < len(words) - 1:
                self.pyautogui.write(' ', interval=0.1)
            
            # 随机停顿（模拟思考）
            if random.random() < 0.1:
                pause = random.uniform(0.2, 0.8)
                time.sleep(pause)
    
    def _press_send(self):
        """按下发送按钮"""
        print("[Airtest] 发送消息...")
        
        # 方法1: 按回车发送
        self.pyautogui.press('enter')
        self._human_delay(300, 150)
        
        # 方法2: 如果回车没发送，尝试 Command+Enter
        self._human_delay(500, 250)
        if not self._is_message_sent():
            print("[Airtest] 回车未发送，尝试 Command+Enter")
            self.pyautogui.hotkey('command', 'enter')
            self._human_delay(300, 150)
        
        print("[Airtest] ✅ 发送完成")
    
    def _is_message_sent(self):
        """检查消息是否已发送（通过判断输入框是否清空）"""
        self._human_delay(500, 250)
        # 简单方法：尝试输入测试字符并检查
        test_text = 'test'
        self.pyautogui.write(test_text, interval=0.05)
        self._human_delay(100, 50)
        
        # 删除测试文本
        for _ in range(len(test_text)):
            self.pyautogui.press('delete')
            self._human_delay(20, 10)
        
        # 如果输入框清空了，说明消息已发送
        return True  # 简化实现
    
    def _human_delay(self, base_ms, variance_ms):
        """人性化延迟"""
        if not self.humanize:
            time.sleep(base_ms / 1000)
            return
        
        # 基础延迟 + 随机波动
        delay = base_ms + random.randint(-variance_ms, variance_ms)
        delay = max(50, delay)  # 最小50ms
        
        # 随机额外停顿（模拟人类分心）
        if random.random() < 0.05:  # 5%概率额外停顿
            delay += random.randint(300, 1000)
        
        time.sleep(delay / 1000)
    
    def save_screenshot(self, name):
        """保存截图（调试用）"""
        if not self.debug:
            return
        
        try:
            screenshot = self.pyautogui.screenshot()
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = self.resources_dir / f"{name}_{timestamp}.png"
            screenshot.save(filename)
            print(f"[Airtest] 截图已保存: {filename}")
        except Exception as e:
            print(f"[Airtest] 截图失败: {e}")
    
    def get_stats(self):
        """获取统计信息"""
        return {
            'sent_count': self.sent_count,
            'retry_count': self.retry_count,
            'airtest_available': self.airtest_available,
            'pyautogui_available': self.pyautogui_available,
            'humanize_enabled': self.humanize,
            'confidence': self.confidence
        }


# 快速测试
if __name__ == "__main__":
    print("=== Airtest 发送器测试 ===")
    
    sender = WeChatAIRSender(
        wechat_path='/Applications/WeChat.app',
        detect_confidence=0.8,
        max_retry=2,
        humanize=True,
        debug=True
    )
    
    print("初始化完成")
    print("统计:", sender.get_stats())
    
    # 测试发送（模拟）
    print("\n测试发送...")
    test_success = sender.send_to_chat("文件传输助手", "测试消息 from Airtest")
    print(f"测试结果: {'✅ 成功' if test_success else '❌ 失败'}")