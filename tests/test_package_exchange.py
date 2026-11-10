import hashlib
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from python.pantheon.package_exchange import (
    PackageVerificationError, canonical_manifest_bytes, verify_bundle,
)


class PackageExchangeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.bundle = self.root / "bundle"
        self.bundle.mkdir()
        self.private = self.root / "private.pem"
        self.public = self.root / "trusted-public.pem"
        subprocess.run(["openssl", "genpkey", "-algorithm", "ED25519", "-out", str(self.private)],
                       check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        subprocess.run(["openssl", "pkey", "-in", str(self.private), "-pubout", "-out", str(self.public)],
                       check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.key_digest = hashlib.sha256(self.public.read_bytes()).hexdigest()
        self.payload = b"approved payload bytes\n"
        payload_path = self.bundle / "payload" / "module.bin"
        payload_path.parent.mkdir()
        payload_path.write_bytes(self.payload)
        self.manifest = {
            "schema_version": 1,
            "package_id": "eria-module",
            "version": "1.0.0",
            "source": {
                "repository": "Vanellye/CodEXgen",
                "ref": "refs/heads/pantheon/signed-package-exchange",
                "commit": "a" * 40,
            },
            "files": [{
                "path": "payload/module.bin",
                "size_bytes": len(self.payload),
                "sha256": hashlib.sha256(self.payload).hexdigest(),
            }],
        }
        (self.bundle / "manifest.json").write_bytes(canonical_manifest_bytes(self.manifest))
        self._sign()

    def tearDown(self):
        self.temp.cleanup()

    def _sign(self):
        subprocess.run([
            "openssl", "pkeyutl", "-sign", "-inkey", str(self.private), "-rawin",
            "-in", str(self.bundle / "manifest.json"), "-out", str(self.bundle / "manifest.sig"),
        ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def test_verifies_pinned_ed25519_manifest_and_payload(self):
        report = verify_bundle(self.bundle, self.public, self.key_digest)
        self.assertEqual(report["status"], "verified")
        self.assertEqual(report["file_count"], 1)
        self.assertFalse(report["contents_executed"])
        self.assertFalse(report["adoption_authorized"])

    def test_rejects_wrong_public_key_pin(self):
        with self.assertRaises(PackageVerificationError):
            verify_bundle(self.bundle, self.public, "0" * 64)

    def test_rejects_payload_tampering(self):
        (self.bundle / "payload" / "module.bin").write_bytes(b"tampered")
        with self.assertRaises(PackageVerificationError):
            verify_bundle(self.bundle, self.public, self.key_digest)

    def test_rejects_unlisted_files(self):
        (self.bundle / "extra.txt").write_text("unlisted", encoding="utf-8")
        with self.assertRaises(PackageVerificationError):
            verify_bundle(self.bundle, self.public, self.key_digest)

    def test_rejects_noncanonical_manifest(self):
        manifest_path = self.bundle / "manifest.json"
        manifest_path.write_text(json.dumps(self.manifest, indent=2), encoding="utf-8")
        with self.assertRaises(PackageVerificationError):
            verify_bundle(self.bundle, self.public, self.key_digest)

    def test_rejects_path_traversal_before_payload_access(self):
        self.manifest["files"][0]["path"] = "../escape.bin"
        manifest_path = self.bundle / "manifest.json"
        manifest_path.write_bytes(canonical_manifest_bytes(self.manifest))
        self._sign()
        with self.assertRaises(PackageVerificationError):
            verify_bundle(self.bundle, self.public, self.key_digest)


if __name__ == "__main__":
    unittest.main()
