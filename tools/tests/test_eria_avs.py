import base64
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

TOOLS_ROOT = Path(__file__).resolve().parents[1]
if str(TOOLS_ROOT) not in sys.path:
    sys.path.insert(0, str(TOOLS_ROOT))

from eria_pantheon.accuracy import AccuracyValidationService, EvidenceRejected, LedgerIntegrityError
from eria_pantheon.reviewer_identity import canonical_json
from eria_pantheon.pons import Pons


def raw_public(key):
    return key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )


def b64(value):
    return base64.b64encode(value).decode("ascii")


class AuthenticatedAVSTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "avs" / "evidence.jsonl"
        self.root_key = Ed25519PrivateKey.generate()
        self.reviewer_key = Ed25519PrivateKey.generate()
        self.pons = Pons(reviewer_root_public_key_b64=b64(raw_public(self.root_key)))
        self.pons.install_accuracy_service(str(self.path))
        now = datetime.now(timezone.utc)
        body = {
            "reviewer_id": "reviewer:alice",
            "key_id": "key:alice:01",
            "public_key": b64(raw_public(self.reviewer_key)),
            "role": "evidence_reviewer",
            "issuer": "ERIA-Test-Trust-Root",
            "not_before": (now - timedelta(minutes=1)).isoformat(),
            "expires_at": (now + timedelta(days=1)).isoformat(),
            "permissions": ["avs:evidence:submit"],
        }
        self.certificate = dict(body)
        self.certificate["root_signature"] = b64(self.root_key.sign(canonical_json(body)))

    def tearDown(self):
        self.tmp.cleanup()

    def signed_submission(self, *, subject="translator", outcome=True):
        challenge = self.pons.issue_reviewer_challenge(self.certificate)
        payload = {
            "challenge_id": challenge["challenge_id"],
            "nonce": challenge["nonce"],
            "claim_id": "claim-1",
            "subject_component": subject,
            "evidence_ref": "test:evidence:1",
            "outcome": outcome,
            "weight": 1.0,
            "method": "independent_review",
            "signed_at": datetime.now(timezone.utc).isoformat(),
        }
        signature = b64(self.reviewer_key.sign(canonical_json(payload)))
        return challenge, payload, signature

    def test_signed_external_reviewer_evidence_is_scored(self):
        challenge, payload, signature = self.signed_submission()
        record = self.pons.submit_accuracy_evidence(
            certificate=self.certificate, challenge_id=challenge["challenge_id"],
            signed_payload=payload, signature_b64=signature,
        )
        self.assertEqual(record["reviewer_id"] if "reviewer_id" in record else record["verifier_id"], "reviewer:alice")
        result = self.pons.evaluate_accuracy(["claim-1"])
        self.assertEqual(result["status"], "EVIDENCE_VALIDATED")
        self.assertEqual(result["accuracy_score"], 100.0)
        self.assertEqual(result["verifier_identity"], "ED25519_CERTIFICATE_AND_SIGNATURE_VERIFIED")

    def test_forged_signature_is_rejected(self):
        challenge, payload, _ = self.signed_submission()
        with self.assertRaises(PermissionError):
            self.pons.submit_accuracy_evidence(
                certificate=self.certificate, challenge_id=challenge["challenge_id"],
                signed_payload=payload, signature_b64=b64(b"0" * 64),
            )

    def test_challenge_cannot_be_replayed(self):
        challenge, payload, signature = self.signed_submission()
        args = dict(certificate=self.certificate, challenge_id=challenge["challenge_id"],
                    signed_payload=payload, signature_b64=signature)
        self.pons.submit_accuracy_evidence(**args)
        with self.assertRaises(PermissionError):
            self.pons.submit_accuracy_evidence(**args)

    def test_certificate_tampering_is_rejected(self):
        challenge, payload, signature = self.signed_submission()
        tampered = dict(self.certificate)
        tampered["reviewer_id"] = "reviewer:mallory"
        with self.assertRaises(PermissionError):
            self.pons.submit_accuracy_evidence(
                certificate=tampered, challenge_id=challenge["challenge_id"],
                signed_payload=payload, signature_b64=signature,
            )

    def test_self_certification_is_rejected(self):
        challenge, payload, signature = self.signed_submission(subject="reviewer:alice")
        with self.assertRaises(PermissionError):
            self.pons.submit_accuracy_evidence(
                certificate=self.certificate, challenge_id=challenge["challenge_id"],
                signed_payload=payload, signature_b64=signature,
            )

    def test_untrusted_root_disables_submission_and_scoring(self):
        unconfigured = Pons()
        unconfigured.install_accuracy_service(str(self.path.parent / "other.jsonl"))
        with self.assertRaises(PermissionError):
            unconfigured.issue_reviewer_challenge(self.certificate)
        with self.assertRaises(PermissionError):
            unconfigured.evaluate_accuracy(["claim-1"])

    def test_direct_avs_construction_is_rejected(self):
        with self.assertRaises(PermissionError):
            AccuracyValidationService(self.path)

    def test_partial_claim_coverage_remains_incomplete(self):
        challenge, payload, signature = self.signed_submission()
        self.pons.submit_accuracy_evidence(
            certificate=self.certificate, challenge_id=challenge["challenge_id"],
            signed_payload=payload, signature_b64=signature,
        )
        result = self.pons.evaluate_accuracy(["claim-1", "claim-2"])
        self.assertEqual(result["status"], "INCOMPLETE")
        self.assertEqual(result["unverified_claims"], ["claim-2"])

    def test_ledger_tampering_is_detected(self):
        challenge, payload, signature = self.signed_submission()
        self.pons.submit_accuracy_evidence(
            certificate=self.certificate, challenge_id=challenge["challenge_id"],
            signed_payload=payload, signature_b64=signature,
        )
        self.path.write_text(self.path.read_text().replace('"outcome":true', '"outcome":false'))
        with self.assertRaises(LedgerIntegrityError):
            self.pons.evaluate_accuracy(["claim-1"])


if __name__ == "__main__":
    unittest.main()
