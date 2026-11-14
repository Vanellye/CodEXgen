#!/usr/bin/env python3
"""Regression tests for ERIA Æ database translation and preservation rules."""
from __future__ import annotations

import json
import hashlib
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from eria_database_translator import (  # noqa: E402
    canonical_envelope,
    read_bytes,
    sniff_format,
    translate,
)


class TranslatorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def test_sqlite_magic_signature_is_detected(self):
        source = self.root / "without_extension"
        source.write_bytes(b"SQLite format 3\x00" + b"\x00" * 40)
        self.assertEqual(sniff_format(source, read_bytes(source)), "sqlite")

    def test_sqlite_reader_sees_committed_wal_rows_without_writing(self):
        source = self.root / "wal_source.sqlite3"
        db = sqlite3.connect(source)
        try:
            self.assertEqual(db.execute("PRAGMA journal_mode=WAL").fetchone()[0], "wal")
            db.execute("CREATE TABLE source_records(id INTEGER PRIMARY KEY, value TEXT)")
            db.execute("INSERT INTO source_records(value) VALUES ('preserve-me')")
            db.commit()
            self.assertTrue(Path(str(source) + "-wal").exists())

            before = source.read_bytes()
            envelope = canonical_envelope(source, read_bytes(source))
            table = envelope["content"]["tables"]["source_records"]
            self.assertEqual(table["row_count"], 1)
            self.assertFalse(table["truncated"])
            self.assertEqual(table["rows"][0][1], "preserve-me")
            self.assertEqual(envelope["content"]["integrity"], "ok")
            self.assertEqual(source.read_bytes(), before)
        finally:
            db.close()

    def test_json_translation_creates_manifest_and_preserves_source(self):
        source = self.root / "source.json"
        source.write_text('{"answer": 42}\n', encoding="utf-8")
        original = source.read_bytes()
        output = self.root / "derived.json"

        manifest = translate(source, output, "json")

        self.assertEqual(source.read_bytes(), original)
        self.assertEqual(manifest["source_sha256"], hashlib.sha256(original).hexdigest())
        self.assertTrue(output.is_file())
        self.assertTrue(Path(str(output) + ".manifest.json").is_file())
        decoded = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(decoded["content"]["value"]["answer"], 42)

    def test_existing_output_is_never_overwritten(self):
        source = self.root / "source.txt"
        source.write_text("original", encoding="utf-8")
        output = self.root / "existing.json"
        output.write_text("keep", encoding="utf-8")

        with self.assertRaises(FileExistsError):
            translate(source, output, "json")

        self.assertEqual(output.read_text(encoding="utf-8"), "keep")

    def test_binary_source_remains_lossless_base64(self):
        source = self.root / "opaque.bin"
        raw = bytes((0, 255, 1, 2, 128))
        source.write_bytes(raw)
        envelope = canonical_envelope(source, read_bytes(source))
        import base64
        self.assertEqual(
            base64.b64decode(envelope["content"]["data"]),
            raw,
        )
        self.assertEqual(envelope["content"]["kind"], "opaque")


if __name__ == "__main__":
    unittest.main(verbosity=2)
