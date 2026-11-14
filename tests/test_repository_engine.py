import subprocess
import tempfile
import unittest
from pathlib import Path

from tools.eria_pantheon.repository_engine import run_repository_review


class RepositoryEngineTests(unittest.TestCase):
    def test_repository_wide_inventory_and_execution_hold(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "tests").mkdir()
            (root / "tests" / "test_sample.py").write_text("def test_ok():\n    assert True\n", encoding="utf-8")
            (root / "pyproject.toml").write_text("[tool.pytest.ini_options]\n", encoding="utf-8")
            (root / ".github" / "workflows").mkdir(parents=True)
            (root / ".github" / "workflows" / "ci.yml").write_text("name: CI\n", encoding="utf-8")
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            subprocess.run(["git", "-C", str(root), "config", "user.email", "test@example.invalid"], check=True)
            subprocess.run(["git", "-C", str(root), "config", "user.name", "ERIA test"], check=True)
            subprocess.run(["git", "-C", str(root), "add", "."], check=True)
            subprocess.run(["git", "-C", str(root), "commit", "-qm", "fixture"], check=True)
            result = run_repository_review(root)
            self.assertEqual(result["inventory"]["summary"]["file_count"], 3)
            self.assertEqual(result["quality"]["coverage"]["test_candidates"], ["tests/test_sample.py"])
            self.assertEqual(result["quality"]["coverage"]["workflow_files"], [".github/workflows/ci.yml"])
            self.assertFalse(result["execution_plan"]["executed"])
            self.assertEqual(result["execution_plan"]["execution_state"], "HOLD")
            self.assertFalse(result["inventory"]["git"]["dirty"])

    def test_sensitive_paths_are_not_acquired(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / ".env").write_text("TOKEN=not-for-indexing\n", encoding="utf-8")
            (root / "safe.py").write_text("print('safe')\n", encoding="utf-8")
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            subprocess.run(["git", "-C", str(root), "config", "user.email", "test@example.invalid"], check=True)
            subprocess.run(["git", "-C", str(root), "config", "user.name", "ERIA test"], check=True)
            subprocess.run(["git", "-C", str(root), "add", "safe.py"], check=True)
            subprocess.run(["git", "-C", str(root), "commit", "-qm", "fixture"], check=True)
            result = run_repository_review(root)
            paths = [item["path"] for item in result["inventory"]["files"]]
            self.assertEqual(paths, ["safe.py"])
            self.assertEqual(result["inventory"]["limits"]["skipped_sensitive_paths"], 1)


if __name__ == "__main__":
    unittest.main()
