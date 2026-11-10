import sys
import unittest
from dataclasses import replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "python"))
from hypothesis_contract import HypothesisError, HypothesisRecord, validate_hypothesis
from codexgen_contracts.envelope import validate_record


class HypothesisContractTests(unittest.TestCase):
    def record(self):
        return HypothesisRecord(
            record_id="hypothesis-001",
            topic="signal-and-cellular-response",
            claim="A hypothetical model proposes a relationship.",
            assumptions=("model input is controlled",),
            unknowns=("mechanism is not established",),
            source_ref="hypotheticals/model.md",
            created_at="2026-11-09T19:00:00-06:00",
        )

    def test_maps_to_unknown_non_authorizing_envelope(self):
        envelope = self.record().to_envelope()
        validate_record(envelope)
        self.assertEqual(envelope["quality"], "UNKNOWN")
        self.assertEqual(envelope["authorization"]["status"], "not_authorized")
        self.assertEqual(envelope["payload"]["evidence_status"], "not_empirical_evidence")

    def test_cannot_self_promote_to_validated(self):
        with self.assertRaises(HypothesisError):
            validate_hypothesis(replace(self.record(), validation_status="validated"))

    def test_timezone_is_required(self):
        with self.assertRaises(HypothesisError):
            validate_hypothesis(replace(self.record(), created_at="2026-11-09T19:00:00"))

    def test_assumptions_and_unknowns_are_preserved(self):
        envelope = self.record().to_envelope()
        self.assertEqual(envelope["payload"]["assumptions"], ["model input is controlled"])
        self.assertEqual(envelope["payload"]["unknowns"], ["mechanism is not established"])


if __name__ == "__main__":
    unittest.main()
