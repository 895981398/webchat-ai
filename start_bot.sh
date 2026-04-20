#!/bin/bash

# 🚀 微信机器人智能启动脚本
# 功能：
#   1. 自动杀死旧进程
#   2. 自动打开微信
#   3. 调整窗口大小
#   4. 启动监控系统

set -e  # 遇到错误退出

echo "🔄 微信机器人 - 智能启动"
echo "="*60
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 函数：彩色输出
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 步骤 1: 检查端口占用
log_info "检查端口占用 (5678)..."
if lsof -ti:5678 > /dev/null 2>&1; then
    log_warning "端口 5678 被占用，尝试清理..."
    
    # 获取占用进程
    pids=$(lsof -ti:5678)
    log_info "占用进程: $pids"
    
    # 尝试正常终止
    for pid in $pids; do
        log_info "终止进程 $pid..."
        kill $pid 2>/dev/null || true
    done
    
    # 等待3秒
    sleep 3
    
    # 检查是否还有进程
    if lsof -ti:5678 > /dev/null 2>&1; then
        log_warning "仍有进程，强制杀死..."
        kill -9 $(lsof -ti:5678) 2>/dev/null || true
        sleep 1
    fi
fi

log_success "端口检查完成"

# 步骤 2: 检查并启动微信
log_info "检查微信状态..."
if pgrep -x "WeChat" > /dev/null; then
    wechat_pid=$(pgrep -x "WeChat")
    log_success "微信已运行 (PID: $wechat_pid)"
else
    log_warning "微信未运行，尝试启动..."
    
    # 检查微信路径
    if [ -d "/Applications/WeChat.app" ]; then
        log_info "启动微信..."
        open -a "/Applications/WeChat.app"
        
        # 等待启动
        echo -n "等待微信启动"
        for i in {1..10}; do
            if pgrep -x "WeChat" > /dev/null; then
                echo ""
                log_success "微信启动成功"
                break
            fi
            echo -n "."
            sleep 1
        done
        
        # 最终检查
        if ! pgrep -x "WeChat" > /dev/null; then
            log_error "微信启动失败"
            exit 1
        fi
    else
        log_error "找不到微信应用，请确保微信已安装"
        exit 1
    fi
fi

# 步骤 3: 激活微信窗口并调整大小
log_info "准备微信窗口..."
log_info "注意: 观察微信窗口是否自动激活并调整大小"

# 运行Python脚本激活窗口
PYTHON_SCRIPT=$(cat << 'EOF'
import subprocess
import time

def activate_wechat():
    """激活微信窗口"""
    print("🪟 激活微信窗口...")
    
    # 激活窗口
    script = '''
    tell application "WeChat"
        activate
        delay 1
    end tell
    '''
    
    try:
        subprocess.run(['osascript', '-e', script], timeout=5)
        print("✅ 微信窗口已激活")
        return True
    except Exception as e:
        print(f"❌ 激活失败: {e}")
        return False

def adjust_window_size():
    """调整窗口大小"""
    print("📐 调整窗口大小...")
    
    script = '''
    tell application "System Events"
        tell process "WeChat"
            set frontmost to true
            delay 0.5
            
            -- 获取屏幕尺寸
            tell application "Finder"
                set screenSize to bounds of window of desktop
                set screenWidth to item 3 of screenSize
                set screenHeight to item 4 of screenSize
            end tell
            
            -- 计算居中位置
            set windowWidth to 1200
            set windowHeight to 800
            set posX to (screenWidth - windowWidth) / 2
            set posY to (screenHeight - windowHeight) / 2
            
            -- 设置窗口位置和大小
            set position of window 1 to {posX, posY}
            set size of window 1 to {windowWidth, windowHeight}
            
            -- 模拟点击以获取焦点
            delay 0.5
        end tell
    end tell
    '''
    
    try:
        subprocess.run(['osascript', '-e', script], timeout=5)
        print("✅ 窗口大小已调整 (1200x800)")
        return True
    except Exception as e:
        print(f"❌ 调整失败: {e}")
        return False

if __name__ == "__main__":
    # 激活窗口
    if not activate_wechat():
        exit(1)
    
    # 等待一下
    time.sleep(2)
    
    # 调整大小
    if not adjust_window_size():
        exit(1)
    
    print("✅ 窗口准备完成")
EOF
)

echo "$PYTHON_SCRIPT" | python3

# 步骤 4: 启动监控系统
log_info "启动监控系统..."
log_info "注意: 系统将在后台运行，请查看输出"
echo

# 创建日志目录
mkdir -p logs
LOG_FILE="logs/wechat_bot_$(date '+%Y%m%d_%H%M%S').log"

# 启动监控系统
log_info "日志文件: $LOG_FILE"
log_info "Web界面: http://localhost:5678"
echo

# 提示
echo -e "${YELLOW}📋 使用说明:${NC}"
echo "  1. 确保微信在前台，并已打开聊天窗口"
echo "  2. 发送消息测试自动回复"
echo "  3. 查看控制台日志和Web界面"
echo
echo -e "${YELLOW}🔧 模式说明:${NC}"
echo "  - simulate: 只模拟，不实际发送"
echo "  - test: 只发送给测试联系人（文件传输助手）"
echo "  - controlled: 只发送给白名单"
echo "  - auto: 自动回复所有消息"
echo

# 启动
log_info "🚀 启动中..."
python3 monitor_web.py 2>&1 | tee "$LOG_FILE" &

# 获取进程ID
BOT_PID=$!
log_success "监控系统已启动 (PID: $BOT_PID)"
log_info "日志文件: $LOG_FILE"

# 保存进程信息
echo "$BOT_PID" > .bot_pid
echo "日志文件: $LOG_FILE" > .bot_info

echo
echo -e "${GREEN}✅ 微信机器人启动完成${NC}"
echo "📊 启动信息已保存到: .bot_pid, .bot_info"
echo "📱 请打开浏览器访问: http://localhost:5678"
echo "💬 在微信中发送消息测试自动回复"