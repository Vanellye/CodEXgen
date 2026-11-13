import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "python"))
from ic_verification import ICVerification, summarize_verification


class ICVerificationTests(unittest.TestCase):
    def test_instrument_connection_pass_requires_evidence_and_reviewer(self):
        with self.assertRaises(ValueError):
            ICVerification(
                "v-1", "instrument_connection", "sensor-1",
                "loop_continuity", "procedure/loop-check", outcome="pass"
            ).to_record()

    def test_integrated_circuit_pass_is_check_scoped_and_non_authorizing(self):
        record = ICVerification(
            "v-2", "integrated_circuit", "ic-17", "clock_and_reset",
            "procedure/clock-reset", ("lab-report:sha256:abc",),
            "pass", "reviewer:independent-1",
        ).to_record()
        self.assertEqual(record["outcome"], "pass")
        self.assertFalse(record["hardware_operated_by_this_record"])
        self.assertFalse(record["release_authorized"])

    def test_summary_never_authorizes_release_or_actuation(self):
        summary = summarize_verification("instrument_connection", ())
        self.assertFalse(summary["evidence_complete"])
        self.assertFalse(summary["release_authorized"])
        self.assertFalse(summary["physical_actuation_authorized"])
        self.assertFalse(summary["potability_claim_authorized"])

    def test_rejects_wrong_domain_check(self):
        with self.assertRaises(ValueError):
            ICVerification(
                "v-3", "integrated_circuit", "ic-1",
                "loop_continuity", "procedure/test"
            ).to_record()

    def test_duplicate_checks_rejected(self):
        item = ICVerification(
            "v-4", "integrated_circuit", "ic-1", "clock_and_reset",
            "procedure/test"
        )
        with self.assertRaises(ValueError):
            summarize_verification("integrated_circuit", (item, item))


if __name__ == "__main__":
    unittest.main()
