import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from tools.eria_pantheon.storage import AeiStorage
from tools.eria_pantheon.aei import AeiError


class AeiStorageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.source_bytes = b'{"stream":"flowing","records":[1,2,3]}\n'
        (self.root / "stream.json").write_bytes(self.source_bytes)
        self.storage = AeiStorage(self.root)

    def tearDown(self):
        self.temp.cleanup()

    def test_compiles_derived_copy_and_provenance_manifest(self):
        result = self.storage.compile("stream.json")
        artifact = self.root / result["artifact"]
        manifest = self.root / result["manifest"]
        self.assertTrue(artifact.is_file())
        self.assertTrue(manifest.is_file())
        data = json.loads(artifact.read_text(encoding="utf-8"))
        meta = json.loads(manifest.read_text(encoding="utf-8"))
        self.assertEqual(data["source"]["sha256"], hashlib.sha256(self.source_bytes).hexdigest())
        self.assertEqual(data["derived"]["data"]["value"]["stream"], "flowing")
        self.assertEqual(meta["artifact_sha256"], hashlib.sha256(artifact.read_bytes()).hexdigest())
        self.assertEqual(meta["source"]["path"], "stream.json")
        self.assertEqual((self.root / "stream.json").read_bytes(), self.source_bytes)

    def test_each_compilation_creates_a_new_artifact(self):
        first = self.storage.compile("stream.json")
        second = self.storage.compile("stream.json")
        self.assertNotEqual(first["artifact"], second["artifact"])

    def test_credential_like_paths_are_refused(self):
        (self.root / ".env").write_text("TOKEN=dummy", encoding="utf-8")
        with self.assertRaises(AeiError):
            self.storage.compile(".env")

    def test_symlink_storage_directory_is_refused(self):
        outside = self.root.parent / (self.root.name + "-outside")
        outside.mkdir()
        (self.root / "storage").symlink_to(outside, target_is_directory=True)
        with self.assertRaises(AeiError):
            self.storage.compile("stream.json")
        self.assertEqual(list(outside.iterdir()), [])
        outside.rmdir()


if __name__ == "__main__":
    unittest.main()
