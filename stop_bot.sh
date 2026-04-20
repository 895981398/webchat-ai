#!/bin/bash

# 🛑 微信机器人停止脚本
# 功能：
#   1. 停止监控系统
#   2. 清理所有相关进程
#   3. 清理日志文件

set -e

echo "🛑 微信机器人 - 停止脚本"
echo "="*60
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# 步骤 1: 停止监控系统进程
log_info "停止监控系统..."

# 从 .bot_pid 读取进程ID
if [ -f ".bot_pid" ]; then
    BOT_PID=$(cat .bot_pid)
    log_info "找到进程ID: $BOT_PID"
    
    # 检查进程是否存在
    if kill -0 $BOT_PID 2>/dev/null; then
        log_info "终止进程 $BOT_PID..."
        kill $BOT_PID 2>/dev/null || true
        
        # 等待3秒
        echo -n "等待进程退出"
        for i in {1..6}; do
            if ! kill -0 $BOT_PID 2>/dev/null; then
                echo ""
                log_success "进程已终止"
                break
            fi
            echo -n "."
            sleep 0.5
        done
        
        # 如果还在运行，强制杀死
        if kill -0 $BOT_PID 2>/dev/null; then
            log_warning "进程仍在运行，强制杀死..."
            kill -9 $BOT_PID 2>/dev/null || true
            sleep 1
            log_success "强制杀死完成"
        fi
    else:
        log_warning "进程 $BOT_PID 不存在"
    fi
    
    # 清理文件
    rm -f .bot_pid
else
    log_warning "未找到 .bot_pid 文件"
fi

# 步骤 2: 清理所有相关进程
log_info "清理所有相关进程..."

# 查找所有相关进程
PROCESSES=$(ps aux | grep -E "monitor_web\.py|python.*monitor_web|wechat.*bot" | grep -v grep | awk '{print $2}')

if [ -n "$PROCESSES" ]; then
    log_info "找到进程: $PROCESSES"
    
    # 终止所有进程
    for pid in $PROCESSES; do
        log_info "终止进程 $pid..."
        kill $pid 2>/dev/null || true
    done
    
    # 等待
    sleep 2
    
    # 检查是否还有进程
    REMAINING=$(ps aux | grep -E "monitor_web\.py|python.*monitor_web|wechat.*bot" | grep -v grep | awk '{print $2}')
    
    if [ -n "$REMAINING" ]; then
        log_warning "仍有进程运行，强制杀死..."
        for pid in $REMAINING; do
            kill -9 $pid 2>/dev/null || true
        done
        sleep 1
    fi
    
    log_success "进程清理完成"
else:
    log_success "没有找到相关进程"
fi

# 步骤 3: 清理端口占用
log_info "清理端口占用 (5678)..."

if lsof -ti:5678 > /dev/null 2>&1; then
    log_warning "端口 5678 仍有占用，强制清理..."
    kill -9 $(lsof -ti:5678) 2>/dev/null || true
    sleep 1
    log_success "端口清理完成"
else
    log_success "端口 5678 空闲"
fi

# 步骤 4: 运行Python进程清理
log_info "运行高级进程清理..."
PYTHON_CLEANUP=$(cat << 'EOF'
import subprocess
import time
import os

def cleanup_processes():
    """清理所有机器人相关进程"""
    print("🧹 高级进程清理...")
    
    # 查找相关进程
    cmd = "ps aux | grep -E 'monitor_web|wechat_bot|auto_reply' | grep -v grep | awk '{print $2}'"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.stdout.strip():
        pids = result.stdout.strip().split('\n')
        print(f"找到 {len(pids)} 个进程: {pids}")
        
        for pid in pids:
            try:
                print(f"  终止 PID: {pid}")
                os.kill(int(pid), 9)  # SIGKILL
                time.sleep(0.1)
            except:
                pass
        
        print("✅ 进程清理完成")
    else:
        print("✅ 没有需要清理的进程")

def check_port_5678():
    """检查端口 5678"""
    print("🔍 检查端口 5678...")
    
    cmd = "lsof -ti:5678 2>/dev/null"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.stdout.strip():
        pids = result.stdout.strip().split('\n')
        print(f"端口 5678 被占用: {pids}")
        return False
    else:
        print("✅ 端口 5678 空闲")
        return True

if __name__ == "__main__":
    cleanup_processes()
    time.sleep(1)
    check_port_5678()
EOF
)

echo "$PYTHON_CLEANUP" | python3

# 步骤 5: 清理临时文件
log_info "清理临时文件..."

# 清理缓存文件
rm -f .bot_pid .bot_info 2>/dev/null || true

# 清理锁文件
rm -f /tmp/wechat_bot.lock 2>/dev/null || true

# 清理Python缓存
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true

log_success "临时文件清理完成"

# 步骤 6: 显示停止信息
echo
echo -e "${GREEN}✅ 微信机器人已停止${NC}"
echo
echo "📋 清理完成:"
echo "  1. ✅ 监控系统进程"
echo "  2. ✅ 所有相关进程"
echo "  3. ✅ 端口占用"
echo "  4. ✅ 临时文件"
echo "  5. ✅ 缓存文件"
echo
echo "💡 提示: 可以重新运行 start_bot.sh 启动"
echo "       ./start_bot.sh"