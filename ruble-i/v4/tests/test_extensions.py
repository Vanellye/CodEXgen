import sys
import tempfile
import unittest
from pathlib import Path
from datetime import datetime, timezone, timedelta

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from crypto_reviewer import Ed25519ReviewerVerifier
from interpret import interpret_transfer
from history_journal import append_event, verify_journal


class ExtensionTests(unittest.TestCase):
    def test_missing_key_and_revoked_key_fail_closed(self):
        prepared = {"intent_sha256":"a"*64,"policy_version":"v4.0.0",
                    "provider":"wise_platform","rail":"IBAN_SEPA",
                    "beneficiary_id":"ben-12345678","asset":"EUR",
                    "amount_minor":100,"fee_limit_minor":5}
        artifact = {"key_id":"reviewer-key-1","reviewer_id":"reviewer",
                    "intent_sha256":"a"*64,"policy_version":"v4.0.0",
                    "scope":{"intent_sha256":"a"*64,"provider":"wise_platform",
                             "rail":"IBAN_SEPA","beneficiary_id":"ben-12345678",
                             "asset":"EUR","amount_minor":100,"fee_limit_minor":5},
                    "issued_at":datetime.now(timezone.utc).isoformat(),
                    "expires_at":(datetime.now(timezone.utc)+timedelta(minutes=5)).isoformat(),
                    "nonce":"1234567890abcdef","signature_b64":"AA=="}
        self.assertFalse(Ed25519ReviewerVerifier({}).verify(prepared, artifact))
        self.assertFalse(Ed25519ReviewerVerifier({"reviewer-key-1":"AA=="},{"reviewer-key-1"}).verify(prepared, artifact))

    def test_three_in_one_interpretation_never_transmits(self):
        result = interpret_transfer({"amount_minor":100,"asset":"EUR",
                                     "provider":"wise_platform","rail":"IBAN_SEPA",
                                     "beneficiary_id":"ben-12345678"})
        self.assertIn("Prepared a 100", result["english_interpretation"])
        self.assertFalse(result["funds_moved"])
        self.assertEqual(result["provider_transmission"],"DISABLED_IN_V4_PREPARE_MODE")

    def test_hash_chained_history(self):
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory)/"events.jsonl")
            first = append_event(path, {"event_id":"event-0001",
                "event_type":"AUTHENTICATION_SUCCEEDED","actor_ref":"reviewer-ref",
                "provider":"wise_platform","intent_sha256":"a"*64,"result":"SUCCESS"})
            second = append_event(path, {"event_id":"event-0002",
                "event_type":"INTENT_PREPARED","actor_ref":"service-ref",
                "provider":"plaid_transfer","intent_sha256":"b"*64,"result":"SUCCESS"})
            self.assertIsNone(first["previous_event_hash"])
            self.assertEqual(second["previous_event_hash"],first["event_hash"])
            self.assertTrue(verify_journal(path))


if __name__ == "__main__":
    unittest.main()
