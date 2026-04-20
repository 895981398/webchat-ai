"""
微信窗口管理器
负责自动打开微信、调整窗口大小、确保窗口在前台
"""

import subprocess
import time
import os
import platform
from datetime import datetime

class WeChatWindowManager:
    """微信窗口管理器"""
    
    def __init__(self, config=None):
        self.config = config or {}
        
        # 平台检测
        self.platform = platform.system()
        
        # 微信路径
        self.wechat_path = self.config.get('wechat_path', '')
        if not self.wechat_path:
            if self.platform == 'Darwin':  # macOS
                self.wechat_path = '/Applications/WeChat.app'
            elif self.platform == 'Windows':
                self.wechat_path = 'C:\\Program Files (x86)\\Tencent\\WeChat\\WeChat.exe'
            else:
                self.wechat_path = '/usr/bin/wechat'  # Linux可能性较小
        
        # 窗口配置
        self.window_config = {
            'auto_activate': True,      # 自动激活窗口
            'ensure_frontmost': True,   # 确保在最前
            'adjust_size': True,        # 调整窗口大小
            'min_width': 800,           # 最小宽度
            'min_height': 600,          # 最小高度
            'optimal_width': 1200,      # 最佳宽度
            'optimal_height': 800,      # 最佳高度
            'position': 'center',       # 窗口位置
            'check_interval': 1.0,      # 检查间隔(秒)
            'max_retry': 3              # 最大重试次数
        }
        
        # 更新配置
        if 'window' in self.config:
            self.window_config.update(self.config['window'])
        
        print(f"[WindowManager] 初始化完成 ({self.platform})")
        print(f"  微信路径: {self.wechat_path}")
        print(f"  自动激活: {'✅ 开启' if self.window_config['auto_activate'] else '❌ 关闭'}")
        print(f"  调整大小: {'✅ 开启' if self.window_config['adjust_size'] else '❌ 关闭'}")
    
    def ensure_wechat_running(self):
        """
        确保微信正在运行
        
        Returns:
            bool: 微信是否在运行
        """
        print("[WindowManager] 检查微信运行状态...")
        
        if self.platform == 'Darwin':
            # macOS 检查
            try:
                result = subprocess.run(
                    ['pgrep', '-x', 'WeChat'],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    print(f"✅ 微信正在运行 (PID: {result.stdout.strip()})")
                    return True
                else:
                    print("❌ 微信未运行")
                    return False
            except Exception as e:
                print(f"❌ 检查微信状态失败: {e}")
                return False
        
        elif self.platform == 'Windows':
            # Windows 检查
            try:
                import psutil
                for proc in psutil.process_iter(['name']):
                    if proc.info['name'] and 'WeChat' in proc.info['name']:
                        print(f"✅ 微信正在运行 (PID: {proc.pid})")
                        return True
                print("❌ 微信未运行")
                return False
            except ImportError:
                # 简单检查
                result = subprocess.run(
                    ['tasklist', '/FI', 'IMAGENAME eq WeChat.exe'],
                    capture_output=True,
                    text=True
                )
                return 'WeChat.exe' in result.stdout
        
        return False
    
    def launch_wechat(self):
        """
        启动微信
        
        Returns:
            bool: 启动是否成功
        """
        print(f"[WindowManager] 启动微信...")
        
        if not os.path.exists(self.wechat_path):
            print(f"❌ 微信路径不存在: {self.wechat_path}")
            return False
        
        try:
            if self.platform == 'Darwin':
                # macOS: 使用 open 命令
                subprocess.run(['open', '-a', self.wechat_path], check=True)
                print(f"✅ 已启动微信: {os.path.basename(self.wechat_path)}")
            elif self.platform == 'Windows':
                # Windows: 直接运行
                subprocess.run([self.wechat_path], check=True)
                print(f"✅ 已启动微信")
            else:
                # Linux: 尝试运行
                subprocess.run([self.wechat_path], check=True)
                print(f"✅ 已启动微信")
            
            # 等待微信启动
            time.sleep(3)
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ 启动微信失败: {e}")
            return False
        except Exception as e:
            print(f"❌ 启动异常: {e}")
            return False
    
    def activate_wechat_window(self):
        """
        激活微信窗口（使其在前台）
        
        Returns:
            bool: 激活是否成功
        """
        if not self.window_config['auto_activate']:
            print("[WindowManager] 自动激活已关闭")
            return False
        
        print("[WindowManager] 激活微信窗口...")
        
        try:
            if self.platform == 'Darwin':
                # 方法1: 使用AppleScript
                script = '''
                tell application "System Events"
                    set frontApp to name of first application process whose frontmost is true
                    if frontApp is not "WeChat" then
                        tell application "WeChat" to activate
                        delay 0.5
                    end if
                end tell
                '''
                
                subprocess.run(['osascript', '-e', script], 
                              capture_output=True, text=True, timeout=5)
                
                # 方法2: 使用快捷键切换到微信
                import pyautogui
                pyautogui.hotkey('command', 'tab', interval=0.1)
                time.sleep(0.3)
                
                print("✅ 微信窗口已激活")
                return True
                
            elif self.platform == 'Windows':
                # Windows: 使用 pygetwindow
                try:
                    import pygetwindow as gw
                    wechat_windows = gw.getWindowsWithTitle('微信')
                    if wechat_windows:
                        wechat_windows[0].activate()
                        print("✅ 微信窗口已激活")
                        return True
                    else:
                        print("❌ 未找到微信窗口")
                        return False
                except ImportError:
                    print("⚠️  需要安装 pygetwindow: pip install pygetwindow")
                    return False
            
            return False
            
        except Exception as e:
            print(f"❌ 激活窗口失败: {e}")
            return False
    
    def adjust_window_size(self):
        """
        调整微信窗口大小
        
        Returns:
            bool: 调整是否成功
        """
        if not self.window_config['adjust_size']:
            print("[WindowManager] 窗口大小调整已关闭")
            return False
        
        print("[WindowManager] 调整微信窗口大小...")
        
        try:
            if self.platform == 'Darwin':
                # macOS: 使用AppleScript调整窗口大小和位置
                width = self.window_config['optimal_width']
                height = self.window_config['optimal_height']
                
                script = f'''
                tell application "System Events"
                    tell process "WeChat"
                        set frontmost to true
                        delay 0.3
                        
                        -- 获取屏幕尺寸
                        tell application "Finder"
                            set screenSize to bounds of window of desktop
                            set screenWidth to item 3 of screenSize
                            set screenHeight to item 4 of screenSize
                        end tell
                        
                        -- 计算居中位置
                        set windowWidth to {width}
                        set windowHeight to {height}
                        set posX to (screenWidth - windowWidth) / 2
                        set posY to (screenHeight - windowHeight) / 2
                        
                        -- 设置窗口位置和大小
                        set position of window 1 to {{posX, posY}}
                        set size of window 1 to {{windowWidth, windowHeight}}
                    end tell
                end tell
                '''
                
                result = subprocess.run(['osascript', '-e', script], 
                                       capture_output=True, text=True, timeout=5)
                
                if result.returncode == 0:
                    print(f"✅ 窗口已调整为 {width}x{height}")
                    return True
                else:
                    print(f"❌ 调整窗口失败: {result.stderr}")
                    return False
                
            elif self.platform == 'Windows':
                # Windows: 使用 pygetwindow
                try:
                    import pygetwindow as gw
                    wechat_windows = gw.getWindowsWithTitle('微信')
                    if wechat_windows:
                        window = wechat_windows[0]
                        window.restore()  # 确保不是最大化
                        window.resizeTo(
                            self.window_config['optimal_width'],
                            self.window_config['optimal_height']
                        )
                        
                        # 居中窗口
                        screen_width, screen_height = gw.getScreenSize()
                        window.moveTo(
                            (screen_width - window.width) // 2,
                            (screen_height - window.height) // 2
                        )
                        
                        print(f"✅ 窗口已调整为 {window.width}x{window.height}")
                        return True
                    else:
                        print("❌ 未找到微信窗口")
                        return False
                except ImportError:
                    print("⚠️  需要安装 pygetwindow: pip install pygetwindow")
                    return False
            
            return False
            
        except Exception as e:
            print(f"❌ 调整窗口失败: {e}")
            return False
    
    def ensure_chat_window_visible(self, chat_name):
        """
        确保指定聊天窗口可见
        
        Args:
            chat_name: 聊天名称
            
        Returns:
            bool: 是否可见
        """
        print(f"[WindowManager] 确保聊天窗口可见: {chat_name}")
        
        # 对于简单的实现，我们假设用户已经打开了正确的聊天窗口
        # 在实际应用中，可能需要实现点击聊天列表等功能
        
        # 这里可以添加检查逻辑，比如：
        # 1. 检查当前聊天窗口标题
        # 2. 如果不是目标聊天，点击左侧聊天列表
        
        print("⚠️  请确保已打开聊天窗口: {chat_name}")
        return True
    
    def prepare_for_sending(self, chat_name=None):
        """
        准备发送环境
        
        Args:
            chat_name: 目标聊天名称
            
        Returns:
            dict: 准备结果
        """
        result = {
            'wechat_running': False,
            'window_activated': False,
            'window_resized': False,
            'chat_visible': False,
            'ready': False
        }
        
        print("[WindowManager] 准备发送环境...")
        
        # 1. 确保微信运行
        if not self.ensure_wechat_running():
            print("❌ 微信未运行，尝试启动...")
            if not self.launch_wechat():
                print("❌ 无法启动微信")
                return result
        
        result['wechat_running'] = True
        
        # 2. 激活窗口
        if self.window_config['ensure_frontmost']:
            result['window_activated'] = self.activate_wechat_window()
        
        # 3. 调整窗口大小
        if self.window_config['adjust_size']:
            result['window_resized'] = self.adjust_window_size()
        
        # 4. 确保聊天窗口可见
        if chat_name:
            result['chat_visible'] = self.ensure_chat_window_visible(chat_name)
        
        # 5. 最终检查
        result['ready'] = all([
            result['wechat_running'],
            result['window_activated'] or not self.window_config['ensure_frontmost'],
            result['window_resized'] or not self.window_config['adjust_size']
        ])
        
        if result['ready']:
            print("✅ 发送环境准备就绪")
        else:
            print("❌ 发送环境准备失败")
        
        return result
    
    def get_window_info(self):
        """
        获取窗口信息
        
        Returns:
            dict: 窗口信息
        """
        info = {
            'platform': self.platform,
            'wechat_path': self.wechat_path,
            'config': self.window_config,
            'timestamp': datetime.now().isoformat()
        }
        
        # 尝试获取实际窗口状态
        try:
            if self.platform == 'Darwin':
                script = '''
                tell application "System Events"
                    if exists process "WeChat" then
                        set wechatProcess to process "WeChat"
                        if exists window 1 of wechatProcess then
                            set win to window 1 of wechatProcess
                            set winPos to position of win
                            set winSize to size of win
                            return (item 1 of winPos) & "," & (item 2 of winPos) & "|" & (item 1 of winSize) & "," & (item 2 of winSize)
                        else
                            return "no_window"
                        end if
                    else
                        return "not_running"
                    end if
                end tell
                '''
                
                result = subprocess.run(['osascript', '-e', script], 
                                       capture_output=True, text=True, timeout=3)
                
                if result.returncode == 0:
                    output = result.stdout.strip()
                    if output == "not_running":
                        info['status'] = 'not_running'
                    elif output == "no_window":
                        info['status'] = 'no_window'
                    else:
                        info['status'] = 'running'
                        pos_str, size_str = output.split('|')
                        info['position'] = [int(x) for x in pos_str.split(',')]
                        info['size'] = [int(x) for x in size_str.split(',')]
                else:
                    info['status'] = 'unknown'
                    
            info['wechat_running'] = self.ensure_wechat_running()
            
        except Exception as e:
            info['status'] = 'error'
            info['error'] = str(e)
        
        return info


# 测试
if __name__ == "__main__":
    print("=== WeChatWindowManager 测试 ===")
    
    config = {
        'window': {
            'auto_activate': True,
            'adjust_size': True,
            'optimal_width': 1200,
            'optimal_height': 800
        }
    }
    
    manager = WeChatWindowManager(config)
    
    # 测试准备
    result = manager.prepare_for_sending("文件传输助手")
    
    print(f"\n📊 准备结果:")
    for key, value in result.items():
        print(f"  {key}: {value}")
    
    # 获取窗口信息
    print(f"\n📋 窗口信息:")
    info = manager.get_window_info()
    for key, value in info.items():
        if key not in ['config']:
            print(f"  {key}: {value}")