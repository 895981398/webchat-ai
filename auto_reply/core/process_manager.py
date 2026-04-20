"""
进程管理器
负责杀死后台机器人进程，确保只有一个实例运行
"""

import subprocess
import os
import signal
import time
import sys
from datetime import datetime

class ProcessManager:
    """进程管理器"""
    
    def __init__(self, config=None):
        self.config = config or {}
        
        # 进程配置
        self.process_config = {
            'target_processes': [
                'monitor_web.py',
                'wechat_bot',
                'auto_reply',
                'python3 -m monitor_web'
            ],
            'kill_before_start': True,
            'check_interval': 1.0,
            'max_retry': 3,
            'force_kill': False,
            'exclude_self': True,
            'log_kills': True
        }
        
        # 更新配置
        if 'process' in self.config:
            self.process_config.update(self.config['process'])
        
        # 当前进程信息
        self.current_pid = os.getpid()
        self.current_command = ' '.join(sys.argv)
        
        print(f"[ProcessManager] 初始化完成 (PID: {self.current_pid})")
        print(f"  杀进程启动: {'✅ 开启' if self.process_config['kill_before_start'] else '❌ 关闭'}")
        print(f"  强制杀死: {'✅ 开启' if self.process_config['force_kill'] else '❌ 关闭'}")
        print(f"  排除自身: {'✅ 开启' if self.process_config['exclude_self'] else '❌ 关闭'}")
    
    def find_bot_processes(self):
        """
        查找所有机器人相关进程
        
        Returns:
            list: 进程信息列表，每个元素为 (pid, command)
        """
        processes = []
        
        try:
            # macOS: 使用 pgrep 和 ps
            cmd = "ps aux | grep -E 'monitor_web|wechat_bot|auto_reply' | grep -v grep"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line:
                        parts = line.split()
                        pid = int(parts[1])
                        cmd = ' '.join(parts[10:])
                        
                        # 排除自身
                        if self.process_config['exclude_self'] and pid == self.current_pid:
                            continue
                        
                        processes.append((pid, cmd))
        
        except Exception as e:
            print(f"[ProcessManager] 查找进程失败: {e}")
        
        return processes
    
    def kill_process(self, pid):
        """
        杀死指定进程
        
        Args:
            pid: 进程ID
            
        Returns:
            bool: 是否成功杀死
        """
        try:
            # 1. 尝试正常终止
            os.kill(pid, signal.SIGTERM)
            print(f"[ProcessManager] 发送 SIGTERM 到 PID: {pid}")
            
            # 等待进程结束
            for i in range(5):  # 等待5秒
                try:
                    os.kill(pid, 0)  # 检查进程是否存在
                    time.sleep(0.5)
                except OSError:
                    print(f"[ProcessManager] ✅ 进程 {pid} 已终止")
                    return True
            
            # 2. 如果进程还在，强制杀死
            if self.process_config['force_kill']:
                print(f"[ProcessManager] 强制杀死 PID: {pid}")
                os.kill(pid, signal.SIGKILL)
                
                # 等待确认
                time.sleep(0.5)
                try:
                    os.kill(pid, 0)
                    print(f"[ProcessManager] ⚠️  进程 {pid} 可能还在运行")
                    return False
                except OSError:
                    print(f"[ProcessManager] ✅ 强制杀死 PID: {pid} 成功")
                    return True
            
            print(f"[ProcessManager] ❌ 进程 {pid} 仍在运行")
            return False
            
        except OSError as e:
            # 进程可能已经不存在了
            print(f"[ProcessManager] ⚠️  进程 {pid} 不存在或已终止: {e}")
            return True
        except Exception as e:
            print(f"[ProcessManager] ❌ 杀死进程 {pid} 异常: {e}")
            return False
    
    def kill_all_bot_processes(self):
        """
        杀死所有机器人相关进程
        
        Returns:
            dict: 结果统计
        """
        print("[ProcessManager] 开始清理机器人进程...")
        
        processes = self.find_bot_processes()
        
        if not processes:
            print("[ProcessManager] ✅ 没有找到需要清理的进程")
            return {
                'total_found': 0,
                'killed': 0,
                'failed': 0,
                'details': []
            }
        
        print(f"[ProcessManager] 找到 {len(processes)} 个相关进程:")
        for pid, cmd in processes:
            print(f"   PID: {pid} | {cmd[:60]}...")
        
        results = {
            'total_found': len(processes),
            'killed': 0,
            'failed': 0,
            'details': []
        }
        
        for pid, cmd in processes:
            print(f"\n[ProcessManager] 处理 PID: {pid}")
            print(f"  命令: {cmd[:80]}...")
            
            success = self.kill_process(pid)
            
            if success:
                results['killed'] += 1
                details = {
                    'pid': pid,
                    'status': 'killed',
                    'time': datetime.now().isoformat()
                }
            else:
                results['failed'] += 1
                details = {
                    'pid': pid,
                    'status': 'failed',
                    'time': datetime.now().isoformat()
                }
            
            results['details'].append(details)
        
        # 等待并再次检查
        time.sleep(2)
        remaining = self.find_bot_processes()
        
        if remaining:
            print(f"\n[ProcessManager] ⚠️  仍有 {len(remaining)} 个进程在运行:")
            for pid, cmd in remaining:
                print(f"    PID: {pid} | {cmd[:60]}...")
        else:
            print(f"\n[ProcessManager] ✅ 所有机器人进程已清理完成")
        
        return results
    
    def ensure_single_instance(self, lock_file=None):
        """
        确保只有一个实例运行（文件锁）
        
        Args:
            lock_file: 锁文件路径
            
        Returns:
            bool: 是否是唯一实例
        """
        if lock_file is None:
            lock_file = '/tmp/wechat_bot.lock'
        
        try:
            # 尝试创建锁文件
            lock_fd = os.open(lock_file, os.O_CREAT | os.O_EXCL | os.O_RDWR)
            
            # 写入当前进程信息
            lock_info = f"PID: {self.current_pid}\n"
            lock_info += f"Time: {datetime.now().isoformat()}\n"
            lock_info += f"Command: {self.current_command}\n"
            
            os.write(lock_fd, lock_info.encode())
            os.close(lock_fd)
            
            print(f"[ProcessManager] ✅ 获得锁: {lock_file}")
            print(f"   当前进程: PID={self.current_pid}")
            
            # 注册退出清理函数
            import atexit
            atexit.register(self._release_lock, lock_file)
            
            return True
            
        except OSError:
            # 锁文件已存在，检查进程是否还在运行
            try:
                with open(lock_file, 'r') as f:
                    content = f.read()
                
                # 提取PID
                import re
                match = re.search(r'PID:\s*(\d+)', content)
                if match:
                    old_pid = int(match.group(1))
                    
                    # 检查进程是否存在
                    try:
                        os.kill(old_pid, 0)
                        print(f"[ProcessManager] ❌ 进程 {old_pid} 仍在运行")
                        print(f"   退出当前进程，避免重复运行")
                        sys.exit(1)
                    except OSError:
                        # 进程不存在，可以覆盖锁文件
                        print(f"[ProcessManager] ⚠️  进程 {old_pid} 已终止，重新获取锁")
                        
                        # 删除旧的锁文件
                        os.remove(lock_file)
                        
                        # 重新调用自己
                        return self.ensure_single_instance(lock_file)
                else:
                    print(f"[ProcessManager] ❌ 锁文件格式错误，删除后重试")
                    os.remove(lock_file)
                    return self.ensure_single_instance(lock_file)
                    
            except Exception as e:
                print(f"[ProcessManager] ❌ 锁处理异常: {e}")
                return False
    
    def _release_lock(self, lock_file):
        """释放锁文件"""
        try:
            if os.path.exists(lock_file):
                os.remove(lock_file)
                print(f"[ProcessManager] 🔓 释放锁: {lock_file}")
        except Exception as e:
            print(f"[ProcessManager] ❌ 释放锁失败: {e}")
    
    def start_with_cleanup(self, main_function):
        """
        启动程序并自动清理旧进程
        
        Args:
            main_function: 主函数
            
        Returns:
            主函数的返回值
        """
        if self.process_config['kill_before_start']:
            print("[ProcessManager] 🧹 启动前清理旧进程...")
            kill_result = self.kill_all_bot_processes()
            
            if kill_result['failed'] > 0:
                print(f"[ProcessManager] ⚠️  清理不完全，仍有 {kill_result['failed']} 个进程未杀死")
        
        # 确保单实例
        single_instance = self.ensure_single_instance()
        if not single_instance:
            print("[ProcessManager] ❌ 无法确保单实例运行，退出")
            sys.exit(1)
        
        print("[ProcessManager] ✅ 进程环境准备完成")
        print("[ProcessManager] 🚀 启动主程序...")
        
        # 运行主函数
        return main_function()
    
    def get_process_info(self):
        """
        获取进程信息
        
        Returns:
            dict: 进程信息
        """
        return {
            'current_pid': self.current_pid,
            'current_command': self.current_command,
            'process_config': self.process_config,
            'timestamp': datetime.now().isoformat()
        }


# 测试
if __name__ == "__main__":
    print("=== ProcessManager 测试 ===")
    
    config = {
        'process': {
            'kill_before_start': True,
            'force_kill': False,
            'exclude_self': True
        }
    }
    
    manager = ProcessManager(config)
    
    # 测试查找进程
    print("\n1. 查找机器人进程...")
    processes = manager.find_bot_processes()
    
    if processes:
        print(f"找到 {len(processes)} 个进程:")
        for pid, cmd in processes[:3]:  # 只显示前3个
            print(f"  PID: {pid} | {cmd[:60]}...")
    else:
        print("没有找到相关进程")
    
    # 测试杀进程
    print("\n2. 杀死所有机器人进程...")
    result = manager.kill_all_bot_processes()
    
    print(f"\n结果统计:")
    print(f"  总共找到: {result['total_found']}")
    print(f"  成功杀死: {result['killed']}")
    print(f"  失败: {result['failed']}")
    
    # 测试单实例锁
    print("\n3. 测试单实例锁...")
    success = manager.ensure_single_instance()
    print(f"  单实例: {'✅ 成功' if success else '❌ 失败'}")