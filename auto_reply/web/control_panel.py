"""
Web控制面板
提供自动回复系统的Web界面
"""

from flask import Flask, render_template, jsonify, request
import json
import threading
import time
from datetime import datetime

class ControlPanel:
    """Web控制面板"""
    
    def __init__(self, auto_reply_system, config=None):
        self.auto_reply = auto_reply_system
        self.config = config or {}
        
        # Web应用配置
        self.port = self.config.get('web_port', 8080)
        self.host = self.config.get('web_host', '0.0.0.0')
        
        # 创建Flask应用
        self.app = Flask(__name__, 
                         template_folder='templates',
                         static_folder='static')
        
        # 设置路由
        self._setup_routes()
        
        # 运行状态
        self.is_running = False
        self.server_thread = None
        
        print(f"[ControlPanel] 初始化完成，端口: {self.port}")
        
    def _setup_routes(self):
        """设置路由"""
        
        @self.app.route('/')
        def index():
            """主页"""
            return render_template('control.html')
            
        @self.app.route('/api/status')
        def api_status():
            """系统状态API"""
            stats = {
                'system': {
                    'uptime': time.time() - self.auto_reply.state.runtime_state['start_time'],
                    'is_running': self.auto_reply.state.runtime_state['is_running'],
                    'version': '1.0.0'
                },
                'message_stats': {
                    'total': self.auto_reply.state.runtime_state['message_count'],
                    'replies': self.auto_reply.state.runtime_state['reply_count'],
                    'errors': self.auto_reply.state.runtime_state['error_count']
                },
                'current_mode': self.auto_reply.mode,
                'timestamp': datetime.now().isoformat()
            }
            
            return jsonify(stats)
            
        @self.app.route('/api/modes', methods=['GET', 'POST'])
        def api_modes():
            """模式管理API"""
            if request.method == 'POST':
                data = request.json
                mode = data.get('mode')
                
                if mode in ['simulate', 'test', 'controlled', 'auto']:
                    success = self.auto_reply.set_mode(mode)
                    return jsonify({
                        'success': success,
                        'mode': mode,
                        'message': f'模式已设置为: {mode}'
                    })
                else:
                    return jsonify({
                        'success': False,
                        'message': f'无效模式: {mode}'
                    })
                    
            else:
                # 返回可用模式
                modes = [
                    {'name': 'simulate', 'description': '模拟模式'},
                    {'name': 'test', 'description': '测试模式'},
                    {'name': 'controlled', 'description': '受控模式'},
                    {'name': 'auto', 'description': '自动模式'}
                ]
                
                return jsonify({
                    'current_mode': self.auto_reply.mode,
                    'modes': modes
                })
                
        @self.app.route('/api/messages', methods=['GET'])
        def api_messages():
            """消息历史API"""
            limit = request.args.get('limit', 50, type=int)
            offset = request.args.get('offset', 0, type=int)
            
            # 获取消息历史（简化版本）
            history = self.auto_reply.state.state.get('conversation_history', [])
            start = max(0, len(history) - limit - offset)
            end = len(history) - offset
            
            messages = history[max(0, start):end]
            
            return jsonify({
                'messages': messages,
                'total': len(history),
                'limit': limit,
                'offset': offset
            })
            
        @self.app.route('/api/test/send', methods=['POST'])
        def api_test_send():
            """测试发送API"""
            data = request.json
            target = data.get('target', '文件传输助手')
            message = data.get('message', '测试消息')
            mode = data.get('mode', 'simulate')
            
            print(f"[WebAPI] 测试发送: {target} -> {message}")
            
            # 记录测试请求
            self.auto_reply.state.record_message({
                'username': target,
                'content': message,
                'source': 'web_test'
            })
            
            # 处理消息
            result = self.auto_reply.handle_message({
                'username': target,
                'content': message,
                'sender': target,
                'timestamp': time.time()
            })
            
            return jsonify({
                'success': True,
                'result': result,
                'message': '测试发送请求已处理'
            })
            
        @self.app.route('/api/system/command', methods=['POST'])
        def api_system_command():
            """系统命令API"""
            data = request.json
            command = data.get('command')
            
            commands = {
                'save_state': lambda: self.auto_reply.state.save_state(),
                'clear_context': lambda: self.auto_reply.state.clear_context(),
                'get_stats': lambda: self.auto_reply.state.get_runtime_stats()
            }
            
            if command in commands:
                try:
                    result = commands[command]()
                    return jsonify({
                        'success': True,
                        'command': command,
                        'result': result
                    })
                except Exception as e:
                    return jsonify({
                        'success': False,
                        'error': str(e)
                    })
            else:
                return jsonify({
                    'success': False,
                    'message': f'未知命令: {command}'
                })
                
    def start(self):
        """启动Web服务"""
        if self.is_running:
            print("[ControlPanel] Web服务已在运行")
            return False
            
        def run_server():
            print(f"[ControlPanel] 启动Web服务: http://localhost:{self.port}")
            self.app.run(host=self.host, port=self.port, debug=False, use_reloader=False)
            
        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()
        
        # 等待服务启动
        for _ in range(30):
            try:
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex(('localhost', self.port))
                sock.close()
                
                if result == 0:
                    self.is_running = True
                    print(f"[ControlPanel] Web服务已启动: http://localhost:{self.port}")
                    return True
                    
            except:
                pass
                
            time.sleep(0.1)
            
        print("[ControlPanel] Web服务启动失败")
        return False
        
    def stop(self):
        """停止Web服务"""
        # 由于Flask在子线程中运行，我们无法直接停止
        # 可以记录状态，实际停止需要外部控制
        self.is_running = False
        print("[ControlPanel] Web服务停止信号已发送")
        
    def get_url(self):
        """获取Web地址"""
        return f"http://localhost:{self.port}"