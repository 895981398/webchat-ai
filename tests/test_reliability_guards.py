import unittest
from unittest.mock import MagicMock, patch
import importlib.util


class ControlPanelRequestParsingTests(unittest.TestCase):
    def _build_auto_reply_stub(self):
        auto_reply = MagicMock()
        auto_reply.mode = "simulate"
        auto_reply.set_mode.return_value = True
        auto_reply.handle_message.return_value = {"action": "simulate", "reply": "ok"}
        auto_reply.state.runtime_state = {
            "start_time": 0,
            "is_running": True,
            "message_count": 0,
            "reply_count": 0,
            "error_count": 0,
        }
        auto_reply.state.state = {"conversation_history": []}
        auto_reply.state.save_state.return_value = True
        auto_reply.state.clear_context.return_value = True
        auto_reply.state.get_runtime_stats.return_value = {"ok": True}
        return auto_reply

    def test_modes_endpoint_handles_empty_json_body(self):
        if importlib.util.find_spec("flask") is None:
            self.skipTest("flask is not installed")
        from auto_reply.web.control_panel import ControlPanel

        panel = ControlPanel(self._build_auto_reply_stub(), config={"web_port": 0})
        client = panel.app.test_client()

        response = client.post("/api/modes", data="", content_type="application/json")

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertFalse(payload["success"])
        self.assertIn("无效模式", payload["message"])

    def test_system_command_endpoint_handles_empty_json_body(self):
        if importlib.util.find_spec("flask") is None:
            self.skipTest("flask is not installed")
        from auto_reply.web.control_panel import ControlPanel

        panel = ControlPanel(self._build_auto_reply_stub(), config={"web_port": 0})
        client = panel.app.test_client()

        response = client.post("/api/system/command", data="", content_type="application/json")

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertFalse(payload["success"])
        self.assertIn("未知命令", payload["message"])


class AutoReplyBehaviorTests(unittest.TestCase):
    def test_group_message_no_longer_rejected_by_duplicate_at_check(self):
        from auto_reply import AutoReplySystem

        with patch("auto_reply.WeChatSender") as sender_cls, patch(
            "auto_reply.ReplyEngine"
        ) as engine_cls, patch("auto_reply.SafetyControllerEnhanced") as safety_cls, patch(
            "auto_reply.StateManager"
        ) as state_cls, patch("auto_reply.ProcessManager") as process_cls:
            sender_cls.return_value = MagicMock()
            engine = MagicMock()
            engine.generate_reply.return_value = "ok"
            engine_cls.return_value = engine
            safety = MagicMock()
            safety.check_message.return_value = True
            safety._is_group_chat.return_value = True
            safety._is_mentioned_in_message.return_value = False
            safety_cls.return_value = safety
            state_cls.return_value = MagicMock()
            process = MagicMock()
            process.process_config = {"kill_before_start": False, "force_kill": False}
            process_cls.return_value = process

            system = AutoReplySystem({"group": {"reply_only_at_me": False}})
            system.mode = "simulate"
            result = system.handle_message({"username": "g@chatroom", "content": "hello"})

        self.assertIsNotNone(result)
        self.assertEqual(result["action"], "simulate")
        self.assertEqual(result["reply"], "ok")

    def test_sender_send_message_handles_none_message(self):
        from auto_reply.core.sender import WeChatSender

        with patch.object(WeChatSender, "_detect_send_methods", return_value=None):
            sender = WeChatSender({"sent_log_file": "sent_messages.log"})
            ok = sender.send_message("文件传输助手", None, mode="simulate")

        self.assertTrue(ok)


if __name__ == "__main__":
    unittest.main()
