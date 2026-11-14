import sys
import tempfile
import unittest
from pathlib import Path

TOOLS_ROOT = Path(__file__).resolve().parents[1]
if str(TOOLS_ROOT) not in sys.path:
    sys.path.insert(0, str(TOOLS_ROOT))

from eria_pantheon.accuracy import AccuracyValidationService, EvidenceRejected, LedgerIntegrityError
from eria_pantheon.pons import Pons


class AccuracyValidationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "avs" / "evidence.jsonl"
        self.pons = Pons()
        self.pons.install_accuracy_service(str(self.path))

    def tearDown(self):
        self.tmp.cleanup()

    def test_no_evidence_is_not_evaluated(self):
        result = self.pons.evaluate_accuracy(["claim-1"])
        self.assertEqual(result["status"], "INCOMPLETE")
        self.assertIsNone(result["accuracy_score"])

    def test_self_certification_is_rejected(self):
        with self.assertRaises(EvidenceRejected):
            self.pons.submit_accuracy_evidence(
                claim_id="claim-1", subject_component="translator",
                verifier_id="translator", evidence_ref="test:1", outcome=True,
            )

    def test_independent_evidence_scores_and_ledger_verifies(self):
        self.avs.submit_evidence(
            claim_id="claim-1", subject_component="translator",
            verifier_id="reviewer-a", evidence_ref="test:1", outcome=True,
        )
        result = self.avs.evaluate(["claim-1"])
        self.assertEqual(result["status"], "EVIDENCE_VALIDATED")
        self.assertEqual(result["accuracy_score"], 100.0)
        self.assertTrue(result["ledger"]["valid"])

    def test_partial_claim_coverage_never_looks_complete(self):
        self.avs.submit_evidence(
            claim_id="claim-1", subject_component="translator",
            verifier_id="reviewer-a", evidence_ref="test:1", outcome=True,
        )
        result = self.pons.evaluate_accuracy(["claim-1", "claim-2"])
        self.assertEqual(result["status"], "INCOMPLETE")
        self.assertEqual(result["unverified_claims"], ["claim-2"])

    def test_ledger_tampering_is_detected(self):
        self.avs.submit_evidence(
            claim_id="claim-1", subject_component="translator",
            verifier_id="reviewer-a", evidence_ref="test:1", outcome=True,
        )
        self.path.write_text(self.path.read_text().replace('"outcome":true', '"outcome":false'))
        with self.assertRaises(LedgerIntegrityError):
            self.pons.accuracy_ledger_status()


if __name__ == "__main__":
    unittest.main()
