import json
import unittest
from unittest.mock import patch

from tools.eria_github_conversation_translator import (
    Evidence,
    GitHubReadError,
    GitHubReader,
    fetch_file,
    repo_path,
    translate_evidence,
)


class GitHubTranslatorTests(unittest.TestCase):
    def test_repo_path_validates_owner_repo(self):
        self.assertEqual(repo_path("octo/demo", "/issues/7"),
                         "/repos/octo/demo/issues/7")
        with self.assertRaises(GitHubReadError):
            repo_path("../bad/repo")

    def test_translation_keeps_evidence_provenance_and_limitations(self):
        evidence = Evidence(
            kind="github_api",
            url="https://api.github.com/repos/octo/demo/issues/7",
            retrieved_unix=1.0,
            sha256="abc",
            payload={"number": 7, "title": "Test", "state": "open", "body": "hello"},
        )
        result = translate_evidence("octo/demo", "issue #7", [evidence])
        self.assertEqual(result.schema, "eria.github-conversation.v1")
        self.assertIn("Test", result.answer)
        self.assertEqual(result.evidence[0].sha256, "abc")
        self.assertTrue(result.limitations)

    def test_http_request_is_get_only(self):
        reader = GitHubReader()
        with patch("urllib.request.urlopen") as urlopen:
            response = urlopen.return_value.__enter__.return_value
            response.read.return_value = json.dumps({"ok": True}).encode()
            reader.get("/repos/octo/demo")
            request = urlopen.call_args.args[0]
            self.assertEqual(request.method, "GET")

    def test_file_path_traversal_is_rejected(self):
        reader = GitHubReader()
        with self.assertRaises(GitHubReadError):
            fetch_file(reader, "octo/demo", "../secret.txt")


if __name__ == "__main__":
    unittest.main()
