import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from tacs import (
    TacsError,
    collect_tags,
    serialize_language_cadence,
    verify_ed25519_signature,
)


def git(repo, *args):
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    ).stdout.strip()


class TacsCollectorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.repo = Path(self.temp.name)
        git(self.repo, "init", "-q")
        git(self.repo, "config", "user.name", "TACS Test")
        git(self.repo, "config", "user.email", "tacs@example.invalid")
        (self.repo / "seed.txt").write_text("ancestry\n", encoding="utf-8")
        git(self.repo, "add", "seed.txt")
        git(self.repo, "commit", "-qm", "seed")
        git(self.repo, "tag", "lightweight")
        git(self.repo, "tag", "-a", "annotated", "-m", "annotated message")

    def tearDown(self):
        self.temp.cleanup()

    def test_collects_lightweight_and_annotated_without_moving_refs(self):
        before = git(self.repo, "for-each-ref", "--format=%(refname) %(objectname)", "refs/tags")
        manifest = collect_tags(self.repo)
        after = git(self.repo, "for-each-ref", "--format=%(refname) %(objectname)", "refs/tags")
        self.assertEqual(before, after)
        self.assertEqual([x["ref"] for x in manifest["tags"]], [
            "refs/tags/annotated", "refs/tags/lightweight"
        ])
        by_kind = {item["kind"]: item for item in manifest["tags"]}
        self.assertEqual(set(by_kind), {"annotated", "lightweight"})
        self.assertEqual(by_kind["annotated"]["annotation"]["message"], "annotated message")
        self.assertEqual(by_kind["lightweight"]["tag_object_id"], by_kind["lightweight"]["target_object_id"])
        self.assertEqual(len(by_kind["annotated"]["record_sha256"]), 64)

    def test_remote_identity_does_not_leak_credentials(self):
        git(self.repo, "remote", "add", "origin", "https://user:secret@example.com/org/repo.git")
        identity = collect_tags(self.repo)["repository"]
        self.assertEqual(identity["url"], "https://example.com/org/repo")
        self.assertNotIn("secret", json.dumps(identity))


class TacsSerializerTests(unittest.TestCase):
    def valid_metadata(self):
        return {
            "schema_version": 1,
            "language": {
                "schema_version": 1,
                "tokens": [
                    {"token_id": "rise", "glyph": "ơ", "pronunciation": "oh",
                     "gloss": "emergence", "role": "state"},
                    {"token_id": "ward", "glyph": "ward", "pronunciation": "ward",
                     "gloss": "hold for review", "role": "state"},
                ],
            },
            "cadence": {
                "schema_version": 1,
                "phases": [
                    {"index": 1, "token_ids": ["ward"], "beats": 2},
                    {"index": 0, "token_ids": ["rise"], "beats": 1},
                ],
                "tempo": {"numerator": 60, "denominator": 1, "unit": "bpm"},
            },
        }

    def test_deterministic_sorted_serialization_and_digest(self):
        first, digest = serialize_language_cadence(self.valid_metadata())
        second, digest2 = serialize_language_cadence(self.valid_metadata())
        self.assertEqual(first, second)
        self.assertEqual(digest, digest2)
        self.assertEqual(digest, hashlib.sha256(first).hexdigest())
        parsed = json.loads(first)
        self.assertEqual([p["index"] for p in parsed["cadence"]["phases"]], [0, 1])
        self.assertEqual([t["token_id"] for t in parsed["language"]["tokens"]], ["rise", "ward"])

    def test_rejects_duplicate_token_ids_and_unknown_token_references(self):
        data = self.valid_metadata()
        data["language"]["tokens"].append(dict(data["language"]["tokens"][0]))
        with self.assertRaises(TacsError):
            serialize_language_cadence(data)
        data = self.valid_metadata()
        data["cadence"]["phases"][0]["token_ids"] = ["missing"]
        with self.assertRaises(TacsError):
            serialize_language_cadence(data)

    def test_rejects_floats_and_noncontiguous_cadence(self):
        data = self.valid_metadata()
        data["cadence"]["tempo"]["numerator"] = 60.5
        with self.assertRaises(TacsError):
            serialize_language_cadence(data)
        data = self.valid_metadata()
        data["cadence"]["phases"][0]["index"] = 3
        with self.assertRaises(TacsError):
            serialize_language_cadence(data)


@unittest.skipUnless(shutil.which("openssl"), "OpenSSL is required for Ed25519 signature test")
class TacsSignatureTests(unittest.TestCase):
    def test_ed25519_signature_validates_exact_manifest_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            private = root / "private.pem"
            public = root / "public.pem"
            manifest = root / "manifest.json"
            signature = root / "manifest.sig"
            manifest.write_bytes(b'{"schema_version":1}\n')
            subprocess.run(
                ["openssl", "genpkey", "-algorithm", "ED25519", "-out", str(private)],
                check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            )
            subprocess.run(
                ["openssl", "pkey", "-in", str(private), "-pubout", "-out", str(public)],
                check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            )
            subprocess.run(
                ["openssl", "pkeyutl", "-sign", "-inkey", str(private), "-rawin",
                 "-in", str(manifest), "-out", str(signature)],
                check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            )
            self.assertTrue(verify_ed25519_signature(manifest, signature, public))
            manifest.write_bytes(b'{"schema_version":2}\n')
            self.assertFalse(verify_ed25519_signature(manifest, signature, public))
            self.assertTrue(private.exists(), "verification must not delete or modify the private key")


if __name__ == "__main__":
    unittest.main()
