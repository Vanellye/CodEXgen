import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from eria_oprozal import OprozalAdvisor, classify
from eria_repository_conversation import Conversation


class FakeRepository:
    root = Path("/synthetic/eria")

    def git(self, *args):
        if args[:2] == ("rev-parse", "HEAD"):
            return "abc123\n"
        if args and args[0] == "ls-files":
            return ""
        return ""

    def search(self, query):
        return []

    def files(self):
        return []


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

    def test_conversation_ask_attaches_oprozal_reaction(self):
        conversation = Conversation(FakeRepository())
        answer = conversation.ask("The runtime is lagging.")
        self.assertIn("Oprozal advisory", answer)
        self.assertEqual(conversation.last_oprozal_advice["source_revision"], "abc123")
        self.assertEqual(conversation.last_oprozal_advice["pons"]["status"], "HOLD")

    def test_conversation_keeps_normal_questions_unmodified_by_oprozal(self):
        conversation = Conversation(FakeRepository())
        answer = conversation.ask("Show me all files.")
        self.assertNotIn("Oprozal advisory", answer)
        self.assertIsNone(conversation.last_oprozal_advice)


if __name__ == "__main__":
    unittest.main()
