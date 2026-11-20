"""Expose the ERIA evidence-gate suite to the repository's root CI discovery."""
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUITE_DIR = ROOT / "eria" / "evidence-execution-boundary" / "tests"
import sys
sys.path.insert(0, str(SUITE_DIR))
from test_evidence_gate import EvidenceGateTests  # noqa: F401


class BashAdapterSyntaxTests(unittest.TestCase):
    def test_bash_adapter_parses_without_running(self):
        script = ROOT / "eria" / "evidence-execution-boundary" / "verify_evidence.sh"
        result = subprocess.run(["bash", "-n", str(script)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
