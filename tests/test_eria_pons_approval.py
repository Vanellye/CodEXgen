import subprocess
import tempfile
import unittest
from pathlib import Path

from tools.eria_quality_bridge import QualityBridge
from tools.eria_pons_approval import PonsApprovalService


class PonsApprovalTests(unittest.TestCase):
    def make_repo(self, root):
        root.mkdir()
        subprocess.run(["git", "init", "-q", str(root)], check=True)
        subprocess.run(["git", "-C", str(root), "config", "user.email", "eria-test@example.invalid"], check=True)
        subprocess.run(["git", "-C", str(root), "config", "user.name", "ERIA Test"], check=True)
        (root / "a.py").write_text("def shared():\n    return 1\n", encoding="utf-8")
        (root / "b.py").write_text("def shared():\n    return 2\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(root), "add", "a.py", "b.py"], check=True)
        subprocess.run(["git", "-C", str(root), "commit", "-qm", "fixture"], check=True)

    def setup_services(self, tmp):
        root = Path(tmp) / "repo"
        self.make_repo(root)
        quality = QualityBridge(root, Path(tmp) / "source.sqlite3", Path(tmp) / "qualitative")
        quality.refresh()
        return root, quality, PonsApprovalService(quality, root)

    def test_exact_scope_confirmation_grants_review_ready_without_modifying_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, quality, service = self.setup_services(tmp)
            proposal = quality.prepare_proposal("shared")
            before = {p.name: p.read_bytes() for p in (root / "a.py", root / "b.py")}
            request = service.create_request(proposal["proposal_id"])
            with self.assertRaises(ValueError):
                service.approve(request["request_id"], request["scope_sha256"], "yes")
            result = service.approve(
                request["request_id"], request["scope_sha256"],
                request["confirmation_phrase"],
            )
            self.assertEqual(result["decision"], "REVIEW_READY")
            self.assertFalse(result["source_modified"])
            self.assertEqual(before, {p.name: p.read_bytes() for p in (root / "a.py", root / "b.py")})
            self.assertEqual(len(service.history()["grants"]), 1)

    def test_source_fingerprint_mismatch_keeps_request_on_hold(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, quality, service = self.setup_services(tmp)
            proposal = quality.prepare_proposal("shared")
            request = service.create_request(proposal["proposal_id"])
            (root / "a.py").write_text("def shared():\n    return 99\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "fingerprint changed"):
                service.approve(
                    request["request_id"], request["scope_sha256"],
                    request["confirmation_phrase"],
                )
            self.assertEqual(service.history()["grants"], [])


if __name__ == "__main__":
    unittest.main()
