#!/usr/bin/env python3
"""Compatibility shim forwarding to scripts/test_auto_window.py."""

import os
import runpy


if __name__ == "__main__":
    root = os.path.dirname(os.path.abspath(__file__))
    runpy.run_path(os.path.join(root, "scripts", "test_auto_window.py"), run_name="__main__")
else:
    import unittest

    raise unittest.SkipTest("script-style test moved to scripts/test_auto_window.py")
