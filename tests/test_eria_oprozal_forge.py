import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from eria_oprozal_forge import build_packet
from eria_oprozal_preflight import PreflightError, inspect_python
from eria_quality_analyzer import analyze


class OprozalForgeTests(unittest.TestCase):
    def test_valid_candidate_produces_static_report_and_pons_hold(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "candidate.py").write_text("def answer():\n    return 42\n", encoding="utf-8")
            packet = build_packet(root, "Runtime latency needs profiling.", "candidate.py")
            self.assertEqual(packet["status"], "STATIC_REVIEW_READY")
            self.assertEqual(packet["preflight"]["checks"]["python_ast_parse"], "PASS")
            self.assertEqual(packet["quality_report"]["gates"]["pons_authorization"], "HOLD")
            self.assertFalse(packet["mutation"]["execution"])
            self.assertFalse(packet["mutation"]["source_write"])

    def test_invalid_python_fails_static_quality_gate(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "candidate.py").write_text("def broken(:\n", encoding="utf-8")
            packet = build_packet(root, "Missing capability.", "candidate.py")
            self.assertEqual(packet["preflight"]["status"], "STATIC_CHECKS_FAILED")
            self.assertEqual(packet["quality_report"]["overall"], "STATIC_CHECKS_FAILED")
            self.assertEqual(packet["quality_report"]["gates"]["python_syntax"], "FAIL")

    def test_path_traversal_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            with self.assertRaises(PreflightError):
                inspect_python(root, "../outside.py", "rev")

    def test_binary_file_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "candidate.py").write_bytes(b"\x00binary")
            with self.assertRaises(PreflightError):
                inspect_python(root, "candidate.py", "rev")

    def test_no_deficiency_signal_does_not_create_proposal(self):
        with tempfile.TemporaryDirectory() as td:
            packet = build_packet(Path(td), "List the Git branches.", "")
            self.assertEqual(packet["status"], "NO_DEFICIENCY_SIGNAL")
            self.assertIsNone(packet["proposal"])

    def test_quality_report_hash_is_stable_for_same_evidence(self):
        preflight = {
            "schema": "eria.oprozal.preflight/1.0",
            "source_path": "candidate.py",
            "source_sha256": "a" * 64,
            "source_revision": "abc123",
            "status": "STATIC_CHECKS_PASSED",
            "execution_performed": False,
            "source_write_performed": False,
            "checks": {"path_containment": "PASS", "python_ast_parse": "PASS"},
        }
        proposal = {"proposal_id": "p1", "faculty": "TEST_GENERATION"}
        first = analyze(preflight, proposal)
        second = analyze(preflight, proposal)
        self.assertEqual(first["report_sha256"], second["report_sha256"])


if __name__ == "__main__":
    unittest.main()
