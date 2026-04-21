#!/usr/bin/env python3
"""
OpenClaw bundle entry: resolve repository root from this bundle directory and exec
mcp_stdio_bridge.py. Keeps .mcp.json free of absolute paths.

The bundle must live inside the cloned repo at:
  <repo>/openclaw-wechat-mcp-bundle/launch_mcp.py
so that ../mcp_stdio_bridge.py exists.
"""

import os
import sys

_BUNDLE_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.abspath(os.path.join(_BUNDLE_DIR, ".."))
_BRIDGE = os.path.join(_REPO_ROOT, "mcp_stdio_bridge.py")

if not os.path.isfile(_BRIDGE):
    sys.stderr.write(
        "wechat-mcp: expected %s (clone the full wechat-decrypt repo; "
        "bundle must be at <repo>/openclaw-wechat-mcp-bundle/).\n" % _BRIDGE
    )
    sys.exit(1)

os.chdir(_REPO_ROOT)
os.execv(sys.executable, [sys.executable, _BRIDGE])
