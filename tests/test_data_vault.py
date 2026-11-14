import subprocess
import tempfile
import unittest
from pathlib import Path

from tools.eria_pantheon.data_vault import acquire_commit, verify_vault, VaultError


class DataVaultTests(unittest.TestCase):
    def make_repo(self, root):
        (root / "src").mkdir()
        (root / "src" / "hello.py").write_text(
            "from pathlib import Path\n\ndef preserve_provenance():\n    return 'source stays whole'\n",
            encoding="utf-8",
        )
        (root / ".env").write_text("TOKEN=must-not-be-acquired\n", encoding="utf-8")
        subprocess.run(["git", "init", "-q", str(root)], check=True)
        subprocess.run(["git", "-C", str(root), "config", "user.email", "test@example.invalid"], check=True)
        subprocess.run(["git", "-C", str(root), "config", "user.name", "ERIA test"], check=True)
        subprocess.run(["git", "-C", str(root), "add", "src/hello.py"], check=True)
        subprocess.run(["git", "-C", str(root), "commit", "-qm", "vault fixture"], check=True)
        return subprocess.check_output(
            ["git", "-C", str(root), "rev-parse", "HEAD"], text=True
        ).strip()

    def test_commit_capture_is_idempotent_and_verifiable(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "repo"
            vault = Path(temporary) / "vault"
            root.mkdir()
            commit = self.make_repo(root)
            first = acquire_commit(root, commit, vault)
            second = acquire_commit(root, commit, vault)
            self.assertEqual(first["status"], "CAPTURED")
            self.assertEqual(second["status"], "ALREADY_PRESENT")
            self.assertGreaterEqual(first["new_records"], 1)
            self.assertEqual(verify_vault(vault)["status"], "VERIFIED")
            index = __import__("json").loads(
                (vault / "wordplay" / (commit + ".json")).read_text(encoding="utf-8")
            )
            self.assertTrue(index["records"])
            self.assertIn("top_terms", index["records"][0]["wordplay"])
            self.assertEqual(
                subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip(),
                commit,
            )

    def test_sensitive_paths_are_not_captured(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "repo"
            vault = Path(temporary) / "vault"
            root.mkdir()
            commit = self.make_repo(root)
            acquire_commit(root, commit, vault)
            manifest = (vault / "manifest.jsonl").read_text(encoding="utf-8")
            self.assertNotIn(".env", manifest)
            self.assertNotIn("must-not-be-acquired", manifest)

    def test_manifest_tampering_is_detected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "repo"
            vault = Path(temporary) / "vault"
            root.mkdir()
            commit = self.make_repo(root)
            acquire_commit(root, commit, vault)
            manifest = vault / "manifest.jsonl"
            manifest.write_text(manifest.read_text(encoding="utf-8").replace('"size_bytes":', '"size_bytes": 999, "original_size_bytes":'), encoding="utf-8")
            with self.assertRaises(VaultError):
                verify_vault(vault)

    def test_anchor_must_be_full_commit_sha(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            with self.assertRaises(VaultError):
                acquire_commit(root, "bf492e", root / "vault")


if __name__ == "__main__":
    unittest.main()
