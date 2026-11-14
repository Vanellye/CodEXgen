import json
import tempfile
import unittest
from pathlib import Path

from tools.eria_quality_bridge import QualityBridge


class QualityBridgeTests(unittest.TestCase):
    def test_refresh_persists_report_findings_and_ranked_candidates(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            root.mkdir()
            (root / "a.py").write_text("def shared():\n    eval('x')\n", encoding="utf-8")
            (root / "b.py").write_text("def shared():\n    return 2\n", encoding="utf-8")
            bridge = QualityBridge(root, Path(tmp) / "source.sqlite3", Path(tmp) / "qualitative")
            report = bridge.refresh()
            self.assertTrue(Path(report["report_path"]).is_file())
            self.assertEqual(report["summary"]["files_assessed"], 2)
            self.assertEqual(len(bridge.findings("high")), 1)
            self.assertEqual(bridge.candidates()[0]["symbol"], "shared")
            self.assertTrue(bridge.summary()["ready"])


    def test_inspection_verifies_report_fingerprint_and_answer_uses_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            root.mkdir()
            source = root / "module.py"
            source.write_text("def explainable():\\n    return 1\\n", encoding="utf-8")
            bridge = QualityBridge(root, Path(tmp) / "source.sqlite3", Path(tmp) / "qualitative")
            bridge.refresh()
            inspected = bridge.inspect("module.py")
            self.assertTrue(inspected["matches_report_snapshot"])
            self.assertEqual(inspected["path"], "module.py")
            answer = bridge.answer("Why does explainable function exist?")
            self.assertIn("Âï QUALITATIVE REVIEW", answer)
            source.write_text("def explainable():\\n    return 2\\n", encoding="utf-8")
            self.assertFalse(bridge.inspect("module.py")["matches_report_snapshot"])

    def test_proposal_is_stored_without_repository_mutation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            root.mkdir()
            a = root / "a.py"
            b = root / "b.py"
            a.write_text("def shared():\n    return 1\n", encoding="utf-8")
            b.write_text("def shared():\n    return 2\n", encoding="utf-8")
            before = (a.read_bytes(), b.read_bytes())
            bridge = QualityBridge(root, Path(tmp) / "source.sqlite3", Path(tmp) / "qualitative")
            bridge.refresh()
            proposal = bridge.prepare_proposal("shared")
            self.assertEqual(proposal["status"], "REVIEW_REQUIRED")
            self.assertTrue((Path(tmp) / "qualitative" / "proposals" /
                             (proposal["proposal_id"] + ".json")).is_file())
            self.assertEqual((a.read_bytes(), b.read_bytes()), before)
            self.assertEqual(len(bridge.proposal_history()), 1)


if __name__ == "__main__":
    unittest.main()
