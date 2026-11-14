import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from tools.eria_repository_conversation import Repository
from tools.eria_repository_forge import forge_repository, write_forge


class RepositoryForgeTests(unittest.TestCase):
    def git(self, root: Path, *args: str) -> None:
        subprocess.run(
            ["git", "-C", str(root), *args],
            check=True, capture_output=True, text=True,
        )

    def repository(self, root: Path) -> Repository:
        root.mkdir(parents=True, exist_ok=True)
        self.git(root, "init")
        self.git(root, "config", "user.name", "ERIA test")
        self.git(root, "config", "user.email", "eria-test@example.invalid")
        (root / "helper.py").write_text("VALUE = 3\n", encoding="utf-8")
        (root / "sample.py").write_text(
            'import helper\napi_key = "secret_value_123456"\n'
            "class Engine:\n    pass\n",
            encoding="utf-8",
        )
        (root / ".env").write_text("TOKEN=secret_env_value\n", encoding="utf-8")
        (root / "README.md").write_text("# Repository\n\n## Design\n", encoding="utf-8")
        self.git(root, "add", "helper.py", "sample.py", ".env", "README.md")
        self.git(root, "commit", "-m", "test fixture")
        return Repository(root)

    def test_forges_hashes_structure_and_local_import_edges_without_source_mutation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            repo = self.repository(root)
            before = {
                name: (root / name).read_bytes()
                for name in ("helper.py", "sample.py", ".env", "README.md")
            }
            head_before = repo.git("rev-parse", "HEAD").strip()
            report = forge_repository(repo)

            self.assertEqual(report["schema"], "eria.repository-forge/1")
            self.assertEqual(report["summary"]["files_seen"], 4)
            sample = next(item for item in report["files"] if item["path"] == "sample.py")
            self.assertEqual(sample["classification"], "OBSERVED")
            self.assertTrue(sample["sha256"])
            self.assertEqual(sample["structure"]["parse_status"],
                             "python-ast-parsed-without-execution")
            self.assertTrue(any(edge["from"] == "sample.py" and edge["to"] == "helper.py"
                                for edge in report["relationships"]))
            self.assertNotIn("secret_value_123456", json.dumps(report))
            restricted = next(item for item in report["files"] if item["path"] == ".env")
            self.assertEqual(restricted["classification"], "RESTRICTED")
            self.assertNotIn("sha256", restricted)

            after = {name: (root / name).read_bytes() for name in before}
            self.assertEqual(before, after)
            self.assertEqual(repo.git("rev-parse", "HEAD").strip(), head_before)
            self.assertFalse(report["safety"]["source_files_modified"])
            self.assertFalse(report["safety"]["git_history_modified"])
            self.assertFalse(report["safety"]["code_executed"])

    def test_external_output_is_exclusive_and_internal_output_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            repo = self.repository(root)
            report = forge_repository(repo)
            with self.assertRaises(ValueError):
                write_forge(report, root / "inside.json", root)

            output = Path(tmp) / "representation.json"
            write_forge(report, output, root)
            saved = json.loads(output.read_text(encoding="utf-8"))
            self.assertTrue(saved["safety"]["output_written"])
            with self.assertRaises(FileExistsError):
                write_forge(report, output, root)


if __name__ == "__main__":
    unittest.main()
