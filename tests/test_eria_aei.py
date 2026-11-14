import csv
import hashlib
import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

from tools.eria_pantheon.aei import AeiError, inspect_file
from tools.eria_pantheon.interface import ERIAPantheonInterface

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from eria_repository_conversation import Conversation


class AeiTranslatorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def test_json_translation_retains_source_digest_and_bytes(self):
        raw = b'{"name":"ERIA","count":901}\n'
        path = self.root / "sample.json"
        path.write_bytes(raw)
        result = inspect_file(self.root, "sample.json")
        self.assertEqual(result.format, "JSON")
        self.assertEqual(result.status, "decoded")
        self.assertEqual(result.source_sha256, hashlib.sha256(raw).hexdigest())
        self.assertEqual(result.data["value"]["count"], 901)
        self.assertEqual(path.read_bytes(), raw)
        self.assertEqual(result.source_authority, "NON_AUTHORITATIVE")
        self.assertEqual(result.derived_authority, "NON_AUTHORITATIVE")

    def test_csv_translation(self):
        (self.root / "rows.csv").write_text("id,name\n1,Ada\n2,Lin\n", encoding="utf-8")
        result = inspect_file(self.root, "rows.csv")
        self.assertEqual(result.format, "CSV")
        self.assertEqual(result.data["columns"], ["id", "name"])
        self.assertEqual(len(result.data["rows_preview"]), 2)

    def test_xml_translation(self):
        (self.root / "record.xml").write_text(
            '<record id="7"><name>ERIA</name></record>', encoding="utf-8"
        )
        result = inspect_file(self.root, "record.xml")
        self.assertEqual(result.format, "XML")
        self.assertEqual(result.data["tag"], "record")
        self.assertEqual(result.data["children"][0]["text"], "ERIA")

    def test_sqlite_is_opened_read_only(self):
        path = self.root / "records.sqlite3"
        connection = sqlite3.connect(path)
        connection.execute("CREATE TABLE records(id INTEGER, value TEXT)")
        connection.execute("INSERT INTO records VALUES(1, 'preserve')")
        connection.commit()
        connection.close()
        before = path.read_bytes()
        result = inspect_file(self.root, "records.sqlite3")
        self.assertEqual(result.format, "SQLite")
        self.assertEqual(result.data["tables"][0]["rows_preview"][0]["value"], "preserve")
        self.assertEqual(path.read_bytes(), before)

    def test_path_escape_is_rejected(self):
        with self.assertRaises(AeiError):
            inspect_file(self.root, "../outside.json")

    def test_symlink_is_not_followed(self):
        target = self.root / "target.txt"
        target.write_text("safe", encoding="utf-8")
        link = self.root / "link.txt"
        link.symlink_to(target)
        with self.assertRaises(AeiError):
            inspect_file(self.root, "link.txt")


    def test_pantheon_interface_exposes_aei_inspect_and_translate(self):
        class Repository:
            def __init__(self, root):
                self.root = root
        (self.root / "question.json").write_text('{"answer":42}', encoding="utf-8")
        interface = ERIAPantheonInterface(Repository(self.root))
        for command in ("aei.inspect question.json", "aei.translate question.json"):
            response = json.loads(interface.handle(command))
            self.assertEqual(response["translator"], "Æị")
            self.assertEqual(response["data"]["value"]["answer"], 42)

    def test_conversation_engine_routes_aei_commands(self):
        class Repository:
            def __init__(self, root):
                self.root = root
        (self.root / "routed.json").write_text('{"ok":true}', encoding="utf-8")
        response = Conversation(Repository(self.root)).ask("aei.inspect routed.json")
        self.assertIn('"translator": "Æị"', response)
        self.assertIn('"ok": true', response)

    def test_binary_is_metadata_only(self):
        (self.root / "blob.bin").write_bytes(b"\x00\x01\x02")
        result = inspect_file(self.root, "blob.bin")
        self.assertEqual(result.status, "metadata_only")
        self.assertTrue(result.data["binary"])


if __name__ == "__main__":
    unittest.main()
