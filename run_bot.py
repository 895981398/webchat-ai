#!/usr/bin/env python3
"""
微信机器人一键启动脚本
功能：
1. 自动杀死旧进程
2. 启动微信（如果未运行）
3. 激活并调整微信窗口
4. 启动监控系统
"""

import os
import sys
import subprocess
import time
import signal
from datetime import datetime

def colored(text, color):
    """彩色输出"""
    colors = {
        'green': '\033[0;32m',
        'red': '\033[0;31m',
        'yellow': '\033[1;33m',
        'blue': '\033[0;34m',
        'cyan': '\033[0;36m',
        'reset': '\033[0m'
    }
    return f"{colors.get(color, '')}{text}{colors['reset']}"

def log_info(message):
    """信息日志"""
    print(colored(f"[INFO] {message}", "blue"))

def log_success(message):
    """成功日志"""
    print(colored(f"[SUCCESS] {message}", "green"))

def log_warning(message):
    """警告日志"""
    print(colored(f"[WARNING] {message}", "yellow"))

def log_error(message):
    """错误日志"""
    print(colored(f"[ERROR] {message}", "red"))

def check_wechat_running():
    """检查微信是否运行"""
    try:
        result = subprocess.run(
            ['pgrep', '-x', 'WeChat'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return int(result.stdout.strip())
        return None
    except Exception:
        return None

def launch_wechat():
    """启动微信"""
    wechat_path = "/Applications/WeChat.app"
    
    if not os.path.exists(wechat_path):
        log_error(f"找不到微信应用: {wechat_path}")
        return False
    
    log_info("启动微信...")
    try:
        subprocess.run(['open', '-a', wechat_path], check=True)
        log_success("微信启动命令已发送")
        
        # 等待微信启动
        log_info("等待微信启动...")
        for i in range(15):
            time.sleep(1)
            if check_wechat_running():
                log_success("微信启动成功")
                return True
            if i < 14:
                print(".", end="", flush=True)
        print()
        
        log_warning("微信启动超时，请检查")
        return False
        
    except subprocess.CalledProcessError as e:
        log_error(f"微信启动失败: {e}")
        return False

def kill_old_processes():
    """杀死旧进程"""
    log_info("清理旧进程...")
    
    # 查找所有相关进程
    try:
        # 查找 monitor_web.py 进程
        cmd = "ps aux | grep -E 'monitor_web\\.py|python.*monitor_web' | grep -v grep | awk '{print $2}'"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            log_info(f"找到 {len(pids)} 个进程")
            
            for pid in pids:
                if pid and pid != str(os.getpid()):
                    try:
                        log_info(f"  终止 PID: {pid}")
                        os.kill(int(pid), signal.SIGTERM)
                    except:
                        pass
            
            # 等待一下
            time.sleep(2)
            
            # 再次检查并强制杀死
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.stdout.strip():
                log_warning("仍有进程运行，强制杀死...")
                for pid in result.stdout.strip().split('\n'):
                    if pid:
                        try:
                            os.kill(int(pid), signal.SIGKILL)
                        except:
                            pass
    
    except Exception as e:
        log_error(f"进程清理异常: {e}")
    
    # 检查端口占用
    log_info("检查端口占用...")
    try:
        cmd = "lsof -ti:5678 2>/dev/null"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            log_info(f"端口 5678 被占用: {pids}")
            
            for pid in pids:
                if pid:
                    try:
                        os.kill(int(pid), signal.SIGKILL)
                    except:
                        pass
    except:
        pass
    
    log_success("进程清理完成")

def activate_wechat_window():
    """激活微信窗口"""
    log_info("激活微信窗口...")
    
    script = '''
    tell application "System Events"
        if exists process "WeChat" then
            tell process "WeChat"
                set frontmost to true
                delay 0.5
                
                -- 获取屏幕尺寸

                tell application "Finder"
                    set screenSize to bounds of window of desktop
                    set screenWidth to item 3 of screenSize
                    set screenHeight to item 4 of screenSize
                end tell
                
                -- 调整窗口大小和位置

                set windowWidth to 1200
                set windowHeight to 800
                set posX to (screenWidth - windowWidth) / 2
                set posY to (screenHeight - windowHeight) / 2
                
                set position of window 1 to {posX, posY}
                set size of window 1 to {windowWidth, windowHeight}
                
                delay 1
            end tell
        end if
    end tell
    '''
    
    try:
        subprocess.run(['osascript', '-e', script], check=True, timeout=10)
        log_success("微信窗口已激活并调整大小")
        return True
    except Exception as e:
        log_error(f"窗口激活失败: {e}")
        return False

def start_monitor_web():
    """启动监控系统"""
    log_info("启动监控系统...")
    
    # 创建日志目录
    os.makedirs("logs", exist_ok=True)
    
    # 生成日志文件名

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = f"logs/wechat_bot_{timestamp}.log"
    
    log_info(f"日志文件: {log_file}")
    log_info(f"Web界面: http://localhost:5678")
    log_info("")
    
    # 显示使用指南

    print(colored("📋 使用指南", "cyan"))
    print("="*40)
    print("1. 确保微信在前台")
    print("2. 打开与'文件传输助手'的聊天窗口")
    print("3. 发送消息测试自动回复")
    print("4. 观察Web界面和控制台输出")
    print("")
    
    print(colored("🔧 发送模式", "cyan"))
    print("="*40)
    print("simulate: 只模拟，不实际发送")
    print("test:     只发送给测试联系人")
    print("controlled: 只发送给白名单")
    print("auto:     自动回复所有消息")
    print("")
    
    # 检查模式
    config_file = "auto_reply_config.json"
    current_mode = "simulate"
    
    if os.path.exists(config_file):
        try:
            import json
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                if 'auto_reply' in config:
                    current_mode = config['auto_reply'].get('mode', 'simulate')
        except:
            pass
    
    print(colored(f"🎯 当前模式: {current_mode}", "yellow"))
    print("")
    
    if current_mode == "test":
        print(colored("💡 测试模式提示:", "green"))
        print("  - 只会回复给'文件传输助手'")
        print("  - 不会影响其他联系人")
        print("  - 适合实际测试自动回复")
    elif current_mode == "simulate":
        print(colored("💡 模拟模式提示:", "yellow"))
        print("  - 只模拟发送，不实际发送")
        print("  - 适合开发和调试")
    
    print("")
    print(colored("🚀 启动监控系统...", "green"))
    print("  按 Ctrl+C 停止")
    print("="*60)
    
    try:
        # 启动监控系统
        process = subprocess.Popen(
            ['python3', 'monitor_web.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # 保存进程ID

        with open(".bot_pid", "w") as f:
            f.write(str(process.pid))
        
        with open(".bot_info", "w") as f:
            f.write(f"启动时间: {datetime.now().isoformat()}\n")
            f.write(f"日志文件: {log_file}\n")
            f.write(f"模式: {current_mode}\n")
        
        # 读取输出并写入日志

        try:
            with open(log_file, "w") as log:
                log.write(f"微信机器人启动日志 - {timestamp}\n")
                log.write("="*60 + "\n\n")
                
                while True:
                    line = process.stdout.readline()
                    if not line and process.poll() is not None:
                        break
                    if line:
                        print(line.strip())
                        log.write(line)
                        log.flush()
                        sys.stdout.flush()
        
        except KeyboardInterrupt:
            log_info("正在停止监控系统...")
            process.terminate()
            try:
                process.wait(timeout=5)
                log_success("监控系统已停止")
            except subprocess.TimeoutExpired:
                log_warning("进程未正常退出，强制杀死...")
                process.kill()
                process.wait()
    
    except Exception as e:
        log_error(f"启动失败: {e}")
        return False
    
    return True

def main():
    """主函数"""
    print(colored("🚀 微信机器人一键启动", "green"))
    print(colored("="*60, "green"))
    print(colored("时间: ", "blue") + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print()
    
    try:
        # 1. 清理旧进程
        kill_old_processes()
        
        # 2. 检查并启动微信
        wechat_pid = check_wechat_running()
        if wechat_pid:
            log_success(f"微信已运行 (PID: {wechat_pid})")
        else:
            if launch_wechat():
                # 等待微信完全启动

                time.sleep(3)
        
        # 3. 激活并调整窗口
        activate_wechat_window()
        
        # 等待一下

        time.sleep(2)
        
        # 4. 启动监控系统
        start_monitor_web()
        
    except KeyboardInterrupt:
        log_info("用户中断启动")
        sys.exit(0)
    except Exception as e:
        log_error(f"启动异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()