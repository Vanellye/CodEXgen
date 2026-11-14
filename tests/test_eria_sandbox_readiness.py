import tempfile
import unittest
from pathlib import Path

from eria_sandbox_readiness import probe


class SandboxReadinessTests(unittest.TestCase):
    def make_host(self, root: Path, *, namespaces="userns", controllers="cpu memory pids"):
        (root / "proc/sys/user").mkdir(parents=True)
        (root / "proc/sys/user/max_user_namespaces").write_text(namespaces)
        (root / "sys/fs/cgroup").mkdir(parents=True)
        (root / "sys/fs/cgroup/cgroup.controllers").write_text(controllers)

    def test_complete_host_is_review_required_not_enabled(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_host(root, namespaces="15000")
            result = probe(root, platform="linux", bwrap_path="/usr/bin/bwrap")
        self.assertEqual(result["status"], "HOST_PREREQUISITES_PRESENT_REVIEW_REQUIRED")
        self.assertFalse(result["execution_enabled"])
        self.assertFalse(result["candidate_code_executed"])
        self.assertEqual(result["pons_decision"], "HOLD")

    def test_missing_capabilities_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_host(root, namespaces="0", controllers="cpu")
            result = probe(root, platform="linux", bwrap_path=None)
        self.assertEqual(result["status"], "HOST_NOT_READY")
        self.assertIn("FAIL", result["checks"].values())
        self.assertFalse(result["execution_enabled"])

    def test_non_linux_host_is_not_ready(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_host(root)
            result = probe(root, platform="darwin", bwrap_path="/usr/bin/bwrap")
        self.assertEqual(result["checks"]["linux_host"], "FAIL")
        self.assertEqual(result["status"], "HOST_NOT_READY")

    def test_probe_never_claims_to_test_isolation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_host(root)
            result = probe(root, platform="linux", bwrap_path="/usr/bin/bwrap")
        self.assertTrue(any("No bubblewrap command" in item for item in result["limitations"]))


if __name__ == "__main__":
    unittest.main()
