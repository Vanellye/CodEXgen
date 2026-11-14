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



    def test_patch_hash_requires_second_approval_and_verifies_exact_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, quality, service = self.setup_services(tmp)
            proposal = quality.prepare_proposal("shared")
            request = service.create_request(proposal["proposal_id"])
            parent = service.approve(request["request_id"], request["scope_sha256"],
                                     request["confirmation_phrase"])
            patch = ("diff --git a/a.py b/a.py\\n--- a/a.py\\n+++ b/a.py\\n"
                     "@@ -1,2 +1,2 @@\\n def shared():\\n-    return 1\\n+    return 3\\n")
            patch_request = service.create_patch_request(parent["grant_id"], patch)
            with self.assertRaisesRegex(ValueError, "confirmation phrase"):
                service.approve_patch(patch_request["patch_request_id"],
                                      patch_request["patch_sha256"], "yes")
            grant = service.approve_patch(patch_request["patch_request_id"],
                patch_request["patch_sha256"], patch_request["confirmation_phrase"])
            checked = service.verify_patch_grant(grant["patch_grant_id"], patch)
            self.assertTrue(checked["authorized"])
            self.assertFalse(checked["executor_enabled"])
            with self.assertRaisesRegex(ValueError, "differ from the human-approved hash"):
                service.verify_patch_grant(grant["patch_grant_id"], patch + "# altered\\n")
            self.assertEqual((root / "a.py").read_text(), "def shared():\\n    return 1\\n")

    def test_patch_cannot_expand_parent_scope(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, quality, service = self.setup_services(tmp)
            proposal = quality.prepare_proposal("shared")
            request = service.create_request(proposal["proposal_id"])
            parent = service.approve(request["request_id"], request["scope_sha256"],
                                     request["confirmation_phrase"])
            patch = ("diff --git a/outsider.py b/outsider.py\\n--- a/outsider.py\\n"
                     "+++ b/outsider.py\\n@@ -0,0 +1 @@\\n+unauthorized\\n")
            with self.assertRaisesRegex(ValueError, "expands beyond"):
                service.create_patch_request(parent["grant_id"], patch)

if __name__ == "__main__":
    unittest.main()
