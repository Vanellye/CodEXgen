import unittest
from tools.eria_pantheon.approval import ApprovalError, sign_grant, verify_signed_grant


class SignedPonsGrantTests(unittest.TestCase):
    def setUp(self):
        self.key = "k" * 48
        self.payload = {
            "grant_id": "grant-test-001",
            "capability": "eria.acquire",
            "scope": "storage/inbox/",
            "issued_at": 1000,
            "expires_at": 1600,
            "nonce": "nonce-test-001",
        }

    def test_valid_exact_scope_grant(self):
        signed = sign_grant(self.payload, self.key)
        result = verify_signed_grant(signed, self.key,
            capability="eria.acquire", scope="storage/inbox/", now=1100)
        self.assertEqual(result["grant_id"], "grant-test-001")

    def test_wrong_scope_is_held(self):
        signed = sign_grant(self.payload, self.key)
        with self.assertRaises(ApprovalError):
            verify_signed_grant(signed, self.key,
                capability="eria.acquire", scope="storage/", now=1100)

    def test_tampered_signature_is_held(self):
        signed = sign_grant(self.payload, self.key)
        signed["scope"] = "storage/"
        with self.assertRaises(ApprovalError):
            verify_signed_grant(signed, self.key,
                capability="eria.acquire", scope="storage/", now=1100)

    def test_expired_grant_is_held(self):
        signed = sign_grant(self.payload, self.key)
        with self.assertRaises(ApprovalError):
            verify_signed_grant(signed, self.key,
                capability="eria.acquire", scope="storage/inbox/", now=1600)

    def test_patch_hash_must_match_exactly(self):
        patch = "a" * 64
        payload = dict(self.payload, capability="eria.source.write",
                       scope="tools/example.py", patch_sha256=patch)
        signed = sign_grant(payload, self.key)
        verify_signed_grant(signed, self.key,
            capability="eria.source.write", scope="tools/example.py",
            patch_sha256=patch, now=1100)
        with self.assertRaises(ApprovalError):
            verify_signed_grant(signed, self.key,
                capability="eria.source.write", scope="tools/example.py",
                patch_sha256="b" * 64, now=1100)

    def test_short_key_is_rejected(self):
        with self.assertRaises(ApprovalError):
            sign_grant(self.payload, "short")


if __name__ == "__main__":
    unittest.main()
