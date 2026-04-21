# OpenClaw + WeChat MCP（配置与排障）

## 1. 可移植安装（推荐：完整仓库）

本仓库的 bundle 位于 `openclaw-wechat-mcp-bundle/`。`launch_mcp.py` 会向上解析仓库根目录并启动根目录下的 `mcp_stdio_bridge.py`，因此 **必须把整个仓库克隆到本机**，不能只拷贝 bundle 子目录（否则找不到 `mcp_stdio_bridge.py`）。

- 将 OpenClaw 插件路径指向：`<repo>/openclaw-wechat-mcp-bundle`
- `openclaw-wechat-mcp-bundle/.mcp.json` 使用 `python3` + `launch_mcp.py`，**无硬编码绝对路径**
- 若本机没有 `python3` 命令，可在已安装的 `.mcp.json` 里把 `command` 改成你的解释器路径（例如 Homebrew：`/usr/local/bin/python3`）

## 2. 两套工具前缀（`wechat__*` 与 `WeChat-2__*`）

若 OpenClaw 里同时注册了 **bundle 的 wechat** 和 **`~/.openclaw/openclaw.json` 里 `mcp.servers` 的另一条 WeChat**，会出现两套同名能力、前缀不同，浪费上下文且易混用。

**建议只保留一条来源：**

- 只用 bundle：从 `openclaw.json` 的 `mcp.servers` 中移除重复的 WeChat 条目（或禁用对应插件），保留插件 bundle 提供的 `wechat__*`。
- 只用全局 `mcp.servers`：卸载或禁用本仓库的 wechat bundle，并在 `mcp.servers` 中只配置一条指向 `mcp_stdio_bridge.py` 的服务。

配置完成后在新会话执行 `/tools verbose`，确认只剩一套 `wechat__`（或你故意保留的一套）。

## 3. 可选调试日志（不污染 stdio）

MCP 要求 **stdout/stderr 仅用于协议**；向 stderr 打日志可能导致客户端判定连接失败。需要排障时，设置环境变量把日志写到文件：

```bash
export WECHAT_MCP_DEBUG_LOG=/tmp/wechat-mcp-debug.log
```

- 在 `mcp_stdio_bridge.py` 进程（bridge）中会写少量启动/方向探测信息。
- 子进程 `mcp_server.py` 若继承该环境变量，也会向同一文件追加（子进程 stderr 对 bridge 仍关闭，不影响传输）。

在 OpenClaw 的 `mcp.servers.*.env` 或 bundle 的 `.mcp.json` 的 `env` 里加入 `WECHAT_MCP_DEBUG_LOG` 即可。

## 4. 自检清单

1. Gateway 正常：`openclaw gateway status` 中 RPC probe ok。
2. 新会话：`/new wechat-mcp`（或你的专用 agent），再 `/tools verbose`。
3. 列表中应出现 `wechat__get_recent_sessions` 等；若出现两套前缀，按第 2 节收敛配置。
4. 调用失败时查看 `WECHAT_MCP_DEBUG_LOG`（若已设置）与 `openclaw` 日志文件。

## 5. 自动化测试

仓库内对 stdio bridge 的缓冲解析有单元测试（不启动微信）：

```bash
python3 -m unittest discover -q -s tests
```
