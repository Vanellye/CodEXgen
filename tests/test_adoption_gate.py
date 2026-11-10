import subprocess
import tempfile
import unittest
from pathlib import Path

from tools.adoption_gate import evaluate_candidate


def git(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


class AdoptionGateTests(unittest.TestCase):
    def make_repo(self, root: Path) -> str:
        git(root, "init", "-b", "main")
        git(root, "config", "user.name", "Adoption Gate Test")
        git(root, "config", "user.email", "adoption-gate@example.invalid")
        (root / "tools").mkdir()
        (root / "tools" / "branch_horizon.py").write_text("VERSION = '1'\n", encoding="utf-8")
        (root / "PANTHEON_BRANCH_HORIZON.md").write_text("# Horizon\n", encoding="utf-8")
        git(root, "add", ".")
        git(root, "commit", "-m", "base")
        return git(root, "rev-parse", "HEAD")

    def test_explicit_opt_in_and_allowlisted_additive_change_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            base = self.make_repo(repo)
            (repo / "tools" / "branch_horizon.py").write_text("VERSION = '2'\n", encoding="utf-8")
            git(repo, "commit", "-am", "candidate")
            head = git(repo, "rev-parse", "HEAD")
            report = evaluate_candidate(repo, repo, "divergence/auto/observer", head, head, base)
            self.assertTrue(report["eligible"], report["reasons"])
            self.assertFalse(report["direct_target_mutation"])

    def test_non_opted_in_branch_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            base = self.make_repo(repo)
            (repo / "tools" / "branch_horizon.py").write_text("VERSION = '2'\n", encoding="utf-8")
            git(repo, "commit", "-am", "candidate")
            head = git(repo, "rev-parse", "HEAD")
            report = evaluate_candidate(repo, repo, "feature/observer", head, head, base)
            self.assertIn("branch_not_explicitly_opted_in", report["reasons"])

    def test_workflow_and_dependency_changes_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            base = self.make_repo(repo)
            (repo / ".github").mkdir()
            (repo / ".github" / "workflow.yml").write_text("name: unsafe\n", encoding="utf-8")
            git(repo, "add", ".")
            git(repo, "commit", "-m", "workflow change")
            head = git(repo, "rev-parse", "HEAD")
            report = evaluate_candidate(repo, repo, "divergence/auto/workflow", head, head, base)
            self.assertTrue(any("path_not_allowlisted" in item for item in report["reasons"]))

    def test_branch_head_must_match_observed_head(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            base = self.make_repo(repo)
            (repo / "tools" / "branch_horizon.py").write_text("VERSION = '2'\n", encoding="utf-8")
            git(repo, "commit", "-am", "candidate")
            head = git(repo, "rev-parse", "HEAD")
            report = evaluate_candidate(repo, repo, "divergence/auto/observer", head, "f" * 40, base)
            self.assertIn("branch_head_does_not_match_observed_sha", report["reasons"])


    def test_adoption_workflow_proposes_pr_but_never_auto_merges(self):
        workflow = (Path(__file__).resolve().parents[1] /
                    ".github" / "workflows" / "pantheon-auto-adopt.yml").read_text(encoding="utf-8")
        self.assertIn("gh pr create", workflow)
        self.assertIn("receiver review and approval", workflow)
        self.assertNotIn("gh pr merge", workflow)
        self.assertNotIn("--auto --squash", workflow)

    def test_deletions_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            base = self.make_repo(repo)
            (repo / "tools" / "branch_horizon.py").unlink()
            git(repo, "add", "-u")
            git(repo, "commit", "-m", "delete tool")
            head = git(repo, "rev-parse", "HEAD")
            report = evaluate_candidate(repo, repo, "divergence/auto/delete", head, head, base)
            self.assertTrue(any("non_additive_change" in item for item in report["reasons"]))


if __name__ == "__main__":
    unittest.main()
