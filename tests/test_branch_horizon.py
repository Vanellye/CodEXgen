import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from tools.branch_horizon import LENSES, build_report, stable_lens


def git(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


class StableLensTests(unittest.TestCase):
    def test_same_depth_is_reproducible(self):
        self.assertEqual(stable_lens(19), stable_lens(19))

    def test_successive_heads_rotate(self):
        selections = [stable_lens(depth)[1] for depth in range(1, len(LENSES) + 1)]
        self.assertEqual(list(LENSES), selections)

    def test_rotation_wraps_after_all_dimensions(self):
        self.assertEqual(stable_lens(1)[1], stable_lens(len(LENSES) + 1)[1])

    def test_zero_or_negative_depth_is_safe(self):
        self.assertEqual(stable_lens(0), stable_lens(-10))
        self.assertEqual(stable_lens(0)[1], LENSES[0])


class ReadOnlyReportTests(unittest.TestCase):
    def make_repo(self, root: Path) -> str:
        git(root, "init")
        git(root, "config", "user.name", "Branch Horizon Test")
        git(root, "config", "user.email", "branch-horizon@example.invalid")
        (root / "module.py").write_text("class Example:\n    pass\n", encoding="utf-8")
        (root / "tests").mkdir()
        (root / "tests" / "test_module.py").write_text("def test_example():\n    assert True\n", encoding="utf-8")
        git(root, "add", "module.py", "tests/test_module.py")
        git(root, "commit", "-m", "fixture head")
        return git(root, "rev-parse", "HEAD")

    def test_report_is_bound_to_head_and_does_not_mutate_repo(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            head = self.make_repo(repo)
            before = git(repo, "status", "--porcelain")
            report = build_report(repo, "fixture", "0" * 40, head)
            after = git(repo, "status", "--porcelain")
            self.assertEqual(before, after)
            self.assertEqual(report["head_sha"], head)
            self.assertEqual(report["status"], "complete")
            self.assertIn(report["selected_lens"], LENSES)
            self.assertEqual(report["mutations_performed"], [])

    def test_symlink_blob_is_not_read_as_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            head = self.make_repo(repo)
            (repo / "outside-link.py").symlink_to("/etc/passwd")
            git(repo, "add", "outside-link.py")
            git(repo, "commit", "-m", "add symlink")
            head = git(repo, "rev-parse", "HEAD")
            report = build_report(repo, "fixture", "", head)
            self.assertNotIn("outside-link.py", report["files_inspected"])


if __name__ == "__main__":
    unittest.main()
