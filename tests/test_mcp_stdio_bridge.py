"""
Unit tests for mcp_stdio_bridge framing helpers (no subprocess, no WeChat DB).
POSIX only: the bridge module imports fcntl.
"""

import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

try:
    import fcntl  # noqa: F401

    from mcp_stdio_bridge import _drain_framed_messages, _drain_line_messages
except ImportError:
    fcntl = None
    _drain_framed_messages = None
    _drain_line_messages = None


@unittest.skipUnless(
    fcntl is not None and _drain_framed_messages is not None,
    "mcp_stdio_bridge framing tests require POSIX (fcntl)",
)
class DrainFramedTests(unittest.TestCase):
    def test_crlf_headers_single_body(self):
        body = b'{"jsonrpc":"2.0","id":1}'
        raw = (b"Content-Length: %d\r\n\r\n" % len(body)) + body
        buf = bytearray(raw)
        msgs = _drain_framed_messages(buf)
        self.assertEqual(msgs, [body])
        self.assertEqual(buf, b"")

    def test_lf_only_header_separator(self):
        body = b'{"x":1}'
        raw = (b"Content-Length: %d\n\n" % len(body)) + body
        buf = bytearray(raw)
        msgs = _drain_framed_messages(buf)
        self.assertEqual(msgs, [body])
        self.assertEqual(buf, b"")

    def test_incomplete_body_keeps_buffer(self):
        body = b'{"ok":true}'
        hdr = b"Content-Length: %d\r\n\r\n" % len(body)
        buf = bytearray(hdr + body[:3])
        msgs = _drain_framed_messages(buf)
        self.assertEqual(msgs, [])
        self.assertEqual(bytes(buf), hdr + body[:3])

    def test_two_back_to_back_messages(self):
        b1 = b'{"id":1}'
        b2 = b'{"id":2}'
        raw = (
            (b"Content-Length: %d\r\n\r\n" % len(b1))
            + b1
            + (b"Content-Length: %d\r\n\r\n" % len(b2))
            + b2
        )
        buf = bytearray(raw)
        msgs = _drain_framed_messages(buf)
        self.assertEqual(msgs, [b1, b2])


@unittest.skipUnless(
    fcntl is not None and _drain_line_messages is not None,
    "mcp_stdio_bridge framing tests require POSIX (fcntl)",
)
class DrainLineTests(unittest.TestCase):
    def test_multiple_lines(self):
        buf = bytearray(b"one\ntwo\n")
        msgs = _drain_line_messages(buf)
        self.assertEqual(msgs, [b"one", b"two"])
        self.assertEqual(buf, b"")

    def test_skips_empty_lines(self):
        buf = bytearray(b"a\n\nb\n")
        msgs = _drain_line_messages(buf)
        self.assertEqual(msgs, [b"a", b"b"])


if __name__ == "__main__":
    unittest.main()
