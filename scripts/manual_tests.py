#!/usr/bin/env python3
"""
手动测试入口集合。

用于集中运行依赖本机微信/GUI 的脚本型测试，不参与 unittest 自动回归。
"""

import argparse
import os
import runpy
import sys


SCRIPT_MAP = {
    "actual_send": os.path.join("scripts", "test_actual_send.py"),
    "auto_window": os.path.join("scripts", "test_auto_window.py"),
    "group_chat": os.path.join("scripts", "test_group_chat_feature.py"),
    "integration": os.path.join("scripts", "test_integration.py"),
    "final_integration": os.path.join("scripts", "test_final_integration.py"),
}


def main():
    parser = argparse.ArgumentParser(description="Run manual GUI/integration scripts.")
    parser.add_argument("name", choices=sorted(SCRIPT_MAP.keys()))
    args = parser.parse_args()

    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    script_path = os.path.join(root, SCRIPT_MAP[args.name])
    if not os.path.exists(script_path):
        print(f"script not found: {script_path}")
        return 1

    runpy.run_path(script_path, run_name="__main__")
    return 0


if __name__ == "__main__":
    sys.exit(main())
