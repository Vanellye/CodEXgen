"""Tests for the ERIA canonical conversion engine."""
import json
import tempfile
import unittest
from pathlib import Path

from tools.eria_conversion_engine import ConversionError, convert_file


class ConversionEngineTests(unittest.TestCase):
    def test_json_to_csv_preserves_source_and_writes_manifest(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / "source.json"
            output = root / "derived.csv"
            original = b'[{"name":"Ada","count":3},{"name":"Lin","count":4}]'
            source.write_bytes(original)

            converted, manifest_path = convert_file(source, output, "csv")

            self.assertEqual(source.read_bytes(), original)
            self.assertEqual(converted, output)
            self.assertTrue(output.exists())
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(manifest["source"]["sha256"],
                             __import__("hashlib").sha256(original).hexdigest())
            self.assertEqual(manifest["validation"]["semantic_accuracy"],
                             "not-evaluated")

    def test_existing_output_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / "source.txt"
            output = root / "derived.txt"
            source.write_text("hello", encoding="utf-8")
            output.write_text("keep me", encoding="utf-8")

            with self.assertRaises(ConversionError):
                convert_file(source, output, "txt")

            self.assertEqual(output.read_text(encoding="utf-8"), "keep me")

    def test_invalid_json_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / "broken.json"
            source.write_text("{broken", encoding="utf-8")
            with self.assertRaises(ConversionError):
                convert_file(source, root / "out.json", "json")


if __name__ == "__main__":
    unittest.main()
