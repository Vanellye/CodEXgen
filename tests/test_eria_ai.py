import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from tools.eria_pantheon.ai import AiiConversation
from tools.eria_pantheon.interface import ERIAPantheonInterface


class AiiConversationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.raw = b'{"project":"ERIA","source_records":901,"state":"preserved"}\n'
        (self.root / "sample.json").write_bytes(self.raw)
        self.chat = AiiConversation(self.root)

    def tearDown(self):
        self.temp.cleanup()

    def test_summary_is_bound_to_fresh_aei_inspection(self):
        result = self.chat.ask("sample.json", "Summarize this file")
        self.assertEqual(result["translator"], "Âï")
        self.assertEqual(result["status"], "answered")
        self.assertIn("JSON", result["answer"])
        self.assertEqual(result["source"]["sha256"], hashlib.sha256(self.raw).hexdigest())

    def test_question_returns_pointer_evidence(self):
        result = self.chat.ask("sample.json", "What is the source_records count?")
        self.assertEqual(result["status"], "answered")
        self.assertTrue(any("source_records" in item["pointer"] for item in result["evidence"]))
        self.assertTrue(any(item["value"] == "901" for item in result["evidence"]))

    def test_unknown_question_does_not_invent_answer(self):
        result = self.chat.ask("sample.json", "What is the weather on Mars?")
        self.assertEqual(result["status"], "insufficient_evidence")
        self.assertEqual(result["evidence"], [])

    def test_credential_like_path_is_rejected(self):
        (self.root / ".env").write_text("TOKEN=not-a-real-secret", encoding="utf-8")
        with self.assertRaises(ValueError):
            self.chat.ask(".env", "Summarize this file")

    def test_pantheon_routes_ai_ask_through_pons(self):
        class Repository:
            def __init__(self, root):
                self.root = root
        interface = ERIAPantheonInterface(Repository(self.root))
        response = json.loads(interface.handle(
            'ai.ask sample.json --question "What is source_records count?"'
        ))
        self.assertEqual(response["translator"], "Âï")
        self.assertEqual(response["engine"], "ERIA/PANTHEON")
        self.assertEqual(response["status"], "answered")
        self.assertTrue(response["evidence"])

    def test_source_bytes_remain_unchanged(self):
        self.chat.ask("sample.json", "Summarize this file")
        self.assertEqual((self.root / "sample.json").read_bytes(), self.raw)


if __name__ == "__main__":
    unittest.main()
