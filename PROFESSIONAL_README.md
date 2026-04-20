# 🤖 WeChat AI Auto Reply System

[![GitHub Stars](https://img.shields.io/github/stars/895981398/webchat-ai?style=social)](https://github.com/895981398/webchat-ai/stargazers)
[![GitHub Issues](https://img.shields.io/github/issues/895981398/webchat-ai)](https://github.com/895981398/webchat-ai/issues)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

一个功能丰富的微信自动回复机器人，支持智能群聊过滤、窗口自动管理和进程清理。

## ✨ 核心特性

### 🔒 **智能群聊控制**
- ✅ **白名单机制** - 只回复指定群聊的@我消息
- ✅ **默认安全** - 默认不回复任何群聊
- ✅ **精确管理** - 按需开启特定群聊回复

### 🖼️ **自动窗口管理**
- ✅ **自动激活** - 发送前确保微信窗口在前台
- ✅ **智能调整** - 自动调整窗口到最佳大小（1200×800）
- ✅ **跨平台支持** - macOS (AppleScript) / Windows (pygetwindow)

### 🧹 **进程自动清理**
- ✅ **单实例运行** - 每次启动自动清理旧进程
- ✅ **避免冲突** - 防止多实例干扰

### 💬 **多种回复模式**
- **`simulate`** - 仅模拟，不实际发送

- **`test`** - 测试模式，回复测试联系人

- **`controlled`** - 受控模式，仅回复白名单

- **`auto`** - 自动模式，智能判断回复

### 📊 **实时Web监控**
- **实时消息流** - 查看所有微信消息
- **发送状态** - 监控自动回复状态
- **控制面板** - 管理回复规则

---

## 🚀 快速开始

### 1. 克隆仓库
```bash
git clone https://github.com/895981398/webchat-ai.git
cd webchat-ai
```

### 2. 安装依赖
```bash
pip3 install -r requirements.txt
```

### 3. 一键启动
```bash
./start_bot.sh
```

### 4. 访问监控面板
打开浏览器访问：http://localhost:5678

---

## ⚙️ 配置指南

### 1. 基础配置
编辑 `auto_reply_config.json`：
```json
{
  "auto_reply": {
    "mode": "test",  // simulate/test/controlled/auto
    "user_name": "你的微信昵称",
    "nickname": "你的别名"
  }
}
```

### 2. 开启群聊白名单
```json
{
  "auto_reply": {
    "group": {
      "enabled": true,           // 启用群聊回复
      "whitelist_mode": true,    // 白名单模式
      "reply_only_at_me": true,  // 只回复@我消息
      "whitelist": [
        {
          "username": "family@chatroom",
          "name": "家庭群",
          "reason": "重要通知"
        }
      ]
    }
  }
}
```

---

## 🛠️ 使用方法

### 🏠 本地部署
```bash
# 启动机器人
./start_bot.sh

# 或使用Python脚本
python3 run_bot.py

# 快速测试
python3 quick_start.py
```

### 📱 Web监控
启动后访问：
- **主监控面板**：http://localhost:5678
- **实时消息流**：实时显示所有微信消息

### 🎯 群聊管理
```bash
# 查看白名单
python3 manage_group_whitelist.py show

# 添加群聊到白名单
python3 manage_group_whitelist.py add "群聊ID@chatroom" "群聊名称"

# 启用群聊回复
python3 manage_group_whitelist.py enable
```

---

## 📁 项目结构

```
webchat-ai/
├── auto_reply/                 # 自动回复核心系统
│   ├── core/                   # 核心模块
│   │   ├── group_filter.py              # 群聊过滤器
│   │   ├── group_filter_enhanced.py     # 增强版（白名单机制）
│   │   ├── window_manager.py           # 窗口管理器
│   │   ├── process_manager.py          # 进程管理器
│   │   ├── sender_enhanced.py          # 增强发送器
│   │   └── safety_controller_enhanced.py # 增强安全控制器
│   ├── web/                    # Web监控界面
│   └── rules/                  # 回复规则
├── monitor_web.py              # 主程序（Web监控+自动回复）
├── auto_reply_config.json      # 配置文件
├── start_bot.sh                # 一键启动脚本
├── stop_bot.sh                 # 一键停止脚本
└── requirements.txt            # Python依赖
```

---

## 🔧 技术支持

### 常见问题
1. **微信窗口无法激活** → 检查macOS权限设置
2. **监控面板无法访问** → 检查端口5678是否被占用
3. **群聊消息不回复** → 确认群聊已添加到白名单

### 故障排除
```bash
# 检查依赖
pip3 list | grep -E "pyautogui|pynput|requests"

# 检查端口
lsof -i :5678

# 查看日志
cat logs/wechat_bot_*.log
```

---

## 📄 许可证

本项目基于 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request 来改进这个项目！

1. Fork 仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

---

## 🌟 特性总结

| 特性 | 状态 | 描述 |
|------|------|------|
| 群聊白名单 | ✅ | 精确控制可回复群聊 |
| 窗口自动管理 | ✅ | 自动激活和调整窗口 |
| 进程自动清理 | ✅ | 避免多实例冲突 |
| Web监控面板 | ✅ | 实时查看消息流 |
| 多种发送模式 | ✅ | 模拟/测试/控制/自动 |
| 智能@我检测 | ✅ | 不依赖固定昵称 |
| 安全防护 | ✅ | 默认不回复群聊 |
| 跨平台支持 | ✅ | macOS / Windows |

---

## 📞 联系我们

如果你有任何问题或建议：

- **GitHub Issues**: [提交新Issue](https://github.com/895981398/webchat-ai/issues)
- **邮箱**: 你的邮箱地址

---

**享受智能微信自动回复体验！** 🚀