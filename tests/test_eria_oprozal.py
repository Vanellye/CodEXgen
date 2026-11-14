import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from eria_oprozal import OprozalAdvisor, classify


class OprozalTests(unittest.TestCase):
    def setUp(self):
        self.advisor = OprozalAdvisor()

    def test_latency_gets_profile_first_advice(self):
        advice = self.advisor.assess("The runtime has lag and latency.")
        self.assertEqual(advice["gap"], "RUNTIME_LATENCY")
        self.assertIn("PERFORMANCE_PROFILING", advice["faculty_candidates"])
        self.assertIn("baseline latency", " ".join(advice["verification_steps"]))

    def test_build_failure_gets_reproducible_diagnostics(self):
        advice = self.advisor.assess("Gradle build failed with a compile error.")
        self.assertEqual(advice["gap"], "BUILD_FAILURE")
        self.assertIn("BUILD_DIAGNOSTICS", advice["faculty_candidates"])

    def test_missing_capability_proposes_faculty_without_execution(self):
        advice = self.advisor.assess("This module has a missing capability.")
        self.assertEqual(advice["gap"], "MISSING_CAPABILITY")
        self.assertTrue(advice["execution"]["proposal_only"])
        self.assertFalse(advice["execution"]["code_executed"])
        self.assertFalse(advice["execution"]["repository_mutated"])
        self.assertEqual(advice["pons"]["status"], "HOLD")

    def test_unknown_lack_is_low_confidence(self):
        advice = self.advisor.assess("There is a lack in the design.")
        self.assertEqual(advice["gap"], "UNKNOWN")
        self.assertEqual(advice["confidence"], "LOW")

    def test_ordinary_question_has_no_advisory(self):
        self.assertIsNone(self.advisor.assess("Show me the branch list."))

    def test_source_revision_is_carried_into_advice(self):
        advice = self.advisor.assess("Missing evidence in this result.", "abc123")
        self.assertEqual(advice["source_revision"], "abc123")
        self.assertEqual(advice["source_authority"], "NON_AUTHORITATIVE")

    def test_classifier_handles_each_supported_gap(self):
        cases = {
            "runtime lag": "RUNTIME_LATENCY",
            "build failed": "BUILD_FAILURE",
            "missing test": "TEST_COVERAGE_GAP",
            "dependency conflict": "DEPENDENCY_RISK",
            "security flaw": "SECURITY_CONCERN",
            "no evidence": "MISSING_EVIDENCE",
            "not implemented": "MISSING_CAPABILITY",
            "inconsistent results": "CONTRADICTION",
            "storage full": "STORAGE_PRESSURE",
        }
        for text, expected in cases.items():
            self.assertEqual(classify(text), expected, text)


if __name__ == "__main__":
    unittest.main()
