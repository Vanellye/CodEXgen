import subprocess
import tempfile
import unittest
from pathlib import Path

from tools.branch_horizon import (
    LENSES,
    ROTATING_LENSES,
    SACRED_DIMENSION,
    _cross_branch_peering,
    build_report,
    stable_lens,
)


def git(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


class StableLensTests(unittest.TestCase):
    def test_same_depth_is_reproducible(self):
        self.assertEqual(stable_lens(19), stable_lens(19))

    def test_successive_heads_rotate_six_operational_lenses(self):
        selections = [stable_lens(depth)[1] for depth in range(1, len(ROTATING_LENSES) + 1)]
        self.assertEqual(list(ROTATING_LENSES), selections)

    def test_rotation_wraps_without_rotating_sacred_dimension(self):
        self.assertEqual(stable_lens(1)[1], stable_lens(len(ROTATING_LENSES) + 1)[1])
        self.assertEqual(LENSES[-1], SACRED_DIMENSION)
        self.assertNotIn(SACRED_DIMENSION, [stable_lens(n)[1] for n in range(1, 20)])

    def test_zero_or_negative_depth_is_safe(self):
        self.assertEqual(stable_lens(0), stable_lens(-10))
        self.assertEqual(stable_lens(0)[1], ROTATING_LENSES[0])


class ReadOnlyReportTests(unittest.TestCase):
    def make_repo(self, root: Path) -> str:
        git(root, "init")
        git(root, "config", "user.name", "Branch Horizon Test")
        git(root, "config", "user.email", "branch-horizon@example.invalid")
        (root / "module.py").write_text("class Example:\n    pass\n", encoding="utf-8")
        (root / "requirements.txt").write_text("requests==2.31.0\n", encoding="utf-8")
        (root / "tests").mkdir()
        (root / "tests" / "test_module.py").write_text("def test_example():\n    assert True\n", encoding="utf-8")
        git(root, "add", "module.py", "requirements.txt", "tests/test_module.py")
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
            self.assertIn(report["selected_lens"], ROTATING_LENSES)
            self.assertEqual(report["mutations_performed"], [])
            self.assertEqual(report["sacred_dimension"]["mode"], "always_on_invariant")

    def test_peer_comparison_flags_different_interface_and_dependency_signals(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            head = self.make_repo(repo)
            git(repo, "checkout", "-b", "peer")
            (repo / "module.py").write_text("class Example(Base):\n    pass\n", encoding="utf-8")
            (repo / "requirements.txt").write_text("requests==3.0.0\n", encoding="utf-8")
            git(repo, "add", "module.py", "requirements.txt")
            git(repo, "commit", "-m", "peer variant")
            peer_sha = git(repo, "rev-parse", "HEAD")
            git(repo, "update-ref", "refs/remotes/origin/peer", peer_sha)
            report = _cross_branch_peering(repo, "main", head)
            self.assertEqual(report["peer_count"], 1)
            peer = report["comparisons"][0]
            self.assertEqual(peer["peer_sha"], peer_sha)
            self.assertEqual(peer["classification"], "review_required")
            self.assertEqual(peer["dependency_signals"]["different_specs"], ["requests"])
            self.assertEqual(peer["proposal"]["adoption_authorized"], False)
            self.assertEqual(peer["sacred_guard"]["status"], "preserved")

    def test_peer_comparison_never_changes_refs_or_worktree(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            head = self.make_repo(repo)
            git(repo, "branch", "peer")
            peer_sha = git(repo, "rev-parse", "peer")
            git(repo, "update-ref", "refs/remotes/origin/peer", peer_sha)
            refs_before = git(repo, "for-each-ref", "--format=%(refname) %(objectname)")
            status_before = git(repo, "status", "--porcelain")
            report = _cross_branch_peering(repo, "main", head)
            refs_after = git(repo, "for-each-ref", "--format=%(refname) %(objectname)")
            status_after = git(repo, "status", "--porcelain")
            self.assertEqual(refs_before, refs_after)
            self.assertEqual(status_before, status_after)
            self.assertFalse(report["adoption_authorized"])

    def test_symlink_blob_is_not_read_as_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.make_repo(repo)
            (repo / "outside-link.py").symlink_to("/etc/passwd")
            git(repo, "add", "outside-link.py")
            git(repo, "commit", "-m", "add symlink")
            head = git(repo, "rev-parse", "HEAD")
            report = build_report(repo, "fixture", "", head)
            self.assertNotIn("outside-link.py", report["files_inspected"])


if __name__ == "__main__":
    unittest.main()
