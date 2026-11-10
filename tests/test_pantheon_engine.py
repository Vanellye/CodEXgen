"""Safety and provenance tests for Pantheon source analysis."""
from __future__ import annotations
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from python.pantheon.engine import AnalysisError, analyze_approved_files, generate_pantheon_modules

class PantheonEngineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "repo"
        self.source = self.root / "python"
        self.output = self.root / "pantheon_generated"
        self.source.mkdir(parents=True)
        self.sample = self.source / "sample.py"
        self.sample.write_text(
            '"""sample module"""\n'
            'class Vessel:\n'
            '    """A documented class."""\n'
            '    def carry(self, item, *, safe=True):\n'
            '        return item\n'
            'async def observe(signal):\n'
            '    """Observe without acting."""\n'
            '    return signal\n',
            encoding="utf-8",
        )

    def tearDown(self):
        self.temp.cleanup()

    def test_extracts_top_level_interfaces_and_hash(self):
        records = analyze_approved_files(self.source, ["sample.py"])
        self.assertEqual(records[0]["components"][0]["name"], "Vessel")
        self.assertEqual(records[0]["components"][0]["methods"], ["carry"])
        self.assertEqual(records[0]["components"][1]["kind"], "async_function")
        self.assertEqual(len(records[0]["sha256"]), 64)

    def test_generates_separate_catalog_and_manifest(self):
        manifest = generate_pantheon_modules(self.source, self.output, ["sample.py"])
        self.assertFalse(manifest["execution_performed"])
        self.assertTrue((self.output / "manifest.json").is_file())
        module = self.output / manifest["generated_artifacts"][0]["path"]
        compiled = compile(module.read_text(encoding="utf-8"), str(module), "exec")
        self.assertIsNotNone(compiled)
        saved = json.loads((self.output / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(saved["approved_sources"][0]["source_path"], "sample.py")
        self.assertEqual(saved["schema_version"], 1)
        self.assertEqual(saved["provenance"]["digest_algorithm"], "sha256")
        recorded_digest = saved.pop("manifest_sha256")
        canonical = json.dumps(
            saved, ensure_ascii=False, sort_keys=True,
            separators=(",", ":"), allow_nan=False,
        ).encode("utf-8")
        self.assertEqual(recorded_digest, hashlib.sha256(canonical).hexdigest())

    def test_rejects_unapproved_or_traversal_paths(self):
        with self.assertRaises(AnalysisError):
            analyze_approved_files(self.source, ["../outside.py"])
        with self.assertRaises(AnalysisError):
            analyze_approved_files(self.source, ["missing.py"])

    def test_rejects_output_inside_source_tree(self):
        with self.assertRaises(AnalysisError):
            generate_pantheon_modules(self.source, self.source / "generated", ["sample.py"])

    def test_does_not_overwrite_existing_output_artifacts(self):
        self.output.mkdir()
        (self.output / "keep.txt").write_text("historical", encoding="utf-8")
        with self.assertRaises(AnalysisError):
            generate_pantheon_modules(self.source, self.output, ["sample.py"])
        self.assertEqual((self.output / "keep.txt").read_text(encoding="utf-8"), "historical")

    def test_top_level_side_effects_are_not_executed(self):
        marker = self.root / "must_not_exist.txt"
        source = self.source / "side_effect.py"
        source.write_text(
            "from pathlib import Path" + chr(10)
            + f"Path({str(marker)!r}).write_text('executed')" + chr(10),
            encoding="utf-8",
        )
        analyze_approved_files(self.source, ["side_effect.py"])
        self.assertFalse(marker.exists())

    def test_rejects_syntax_errors_without_writing_output(self):
        broken = self.source / "broken.py"
        broken.write_text("def incomplete(:\n", encoding="utf-8")
        with self.assertRaises(AnalysisError):
            generate_pantheon_modules(self.source, self.output, ["broken.py"])
        self.assertFalse(self.output.exists())

if __name__ == "__main__":
    unittest.main()
