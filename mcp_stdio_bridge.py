#!/usr/bin/env python3
"""
Bridge MCP stdio framing (Content-Length) <-> JSON line protocol.

Some MCP clients send framed JSON-RPC over stdio while this project's server
expects newline-delimited JSON. This shim translates both directions.
"""

import errno
import fcntl
import os
import select
import signal
import subprocess
import sys


def _wechat_mcp_debug_log(msg: str) -> None:
    path = os.environ.get("WECHAT_MCP_DEBUG_LOG", "").strip()
    if not path:
        return
    try:
        with open(path, "a", encoding="utf-8") as f:
            f.write("[mcp_stdio_bridge] %s\n" % msg)
    except OSError:
        pass


def _set_nonblocking(fd):
    flags = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)


def _emit_framed(out_fd, payload):
    if not payload:
        return
    header = ("Content-Length: %d\r\n\r\n" % len(payload)).encode("utf-8")
    os.write(out_fd, header + payload)


def _emit_line(out_fd, payload):
    if not payload:
        return
    os.write(out_fd, payload + b"\n")


def _drain_line_messages(buf):
    messages = []
    while True:
        idx = buf.find(b"\n")
        if idx < 0:
            break
        line = buf[:idx].strip()
        del buf[: idx + 1]
        if line:
            messages.append(line)
    return messages


def _drain_framed_messages(buf):
    messages = []
    while True:
        header_sep_len = 4
        header_end = buf.find(b"\r\n\r\n")
        if header_end < 0:
            # Some clients use LF-only framing.
            header_end = buf.find(b"\n\n")
            header_sep_len = 2
        if header_end < 0:
            break
        header_blob = bytes(buf[:header_end])
        del buf[: header_end + header_sep_len]

        content_length = None
        # Accept CRLF and LF header line endings.
        normalized = header_blob.replace(b"\r\n", b"\n")
        for line in normalized.split(b"\n"):
            if b":" not in line:
                continue
            k, v = line.split(b":", 1)
            if k.strip().lower() == b"content-length":
                try:
                    content_length = int(v.strip())
                except ValueError:
                    content_length = None
                break

        if content_length is None:
            continue
        if len(buf) < content_length:
            # Incomplete body, restore and wait for more.
            sep = b"\r\n\r\n" if header_sep_len == 4 else b"\n\n"
            buf[:0] = header_blob + sep
            break

        body = bytes(buf[:content_length])
        del buf[:content_length]
        messages.append(body)
    return messages


def main():
    _wechat_mcp_debug_log("start pid=%s cwd=%s" % (os.getpid(), os.getcwd()))
    script_dir = os.path.dirname(os.path.abspath(__file__))
    server_path = os.path.join(script_dir, "mcp_server.py")
    proc = subprocess.Popen(
        # Use the same interpreter as this bridge to avoid PATH drift
        # (for example accidentally launching system Python 3.9).
        [sys.executable, server_path],
        cwd=script_dir,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        # Keep MCP transport strictly on stdout framing; silence child stderr
        # because some MCP clients treat any side-channel output as transport
        # failure.
        stderr=subprocess.DEVNULL,
    )
    child_stdin_fd = proc.stdin.fileno()
    child_stdout_fd = proc.stdout.fileno()
    in_fd = sys.stdin.fileno()
    out_fd = sys.stdout.fileno()

    _set_nonblocking(in_fd)
    _set_nonblocking(child_stdout_fd)

    stdin_buf = bytearray()
    stdout_buf = bytearray()
    stdin_open = True
    child_open = True
    # None: unknown, True: framed mode, False: line mode
    client_framed_mode = None

    def _stop(_signum, _frame):
        try:
            proc.terminate()
        except OSError:
            pass

    signal.signal(signal.SIGTERM, _stop)
    signal.signal(signal.SIGINT, _stop)

    while True:
        if proc.poll() is not None and not child_open:
            break

        read_fds = []
        if stdin_open:
            read_fds.append(in_fd)
        if child_open:
            read_fds.append(child_stdout_fd)
        if not read_fds:
            break

        ready, _, _ = select.select(read_fds, [], [], 1.0)
        for fd in ready:
            if fd == in_fd:
                try:
                    chunk = os.read(in_fd, 65536)
                except OSError as e:
                    if e.errno in (errno.EAGAIN, errno.EWOULDBLOCK):
                        chunk = b""
                    else:
                        stdin_open = False
                        chunk = b""
                if not chunk:
                    stdin_open = False
                    try:
                        proc.stdin.close()
                    except OSError:
                        pass
                else:
                    stdin_buf.extend(chunk)
                    probe = bytes(stdin_buf).lstrip()
                    looks_framed = probe.startswith(b"Content-Length:")
                    if client_framed_mode is None:
                        client_framed_mode = looks_framed

                    framed = _drain_framed_messages(stdin_buf)
                    for msg in framed:
                        os.write(child_stdin_fd, msg + b"\n")

                    # If input looks like framed MCP traffic, do not fall back to
                    # line mode while headers/body may still be incomplete.
                    if not looks_framed:
                        for line in _drain_line_messages(stdin_buf):
                            os.write(child_stdin_fd, line + b"\n")

            elif fd == child_stdout_fd:
                try:
                    chunk = os.read(child_stdout_fd, 65536)
                except OSError as e:
                    if e.errno in (errno.EAGAIN, errno.EWOULDBLOCK):
                        chunk = b""
                    else:
                        child_open = False
                        chunk = b""
                if not chunk:
                    child_open = False
                else:
                    stdout_buf.extend(chunk)
                    for line in _drain_line_messages(stdout_buf):
                        if client_framed_mode is False:
                            _emit_line(out_fd, line)
                        else:
                            # Default to framed mode until detected otherwise.
                            _emit_framed(out_fd, line)

    if proc.poll() is None:
        try:
            proc.terminate()
        except OSError:
            pass
    return proc.wait()


if __name__ == "__main__":
    sys.exit(main())
