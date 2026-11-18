import json
import unittest
from pathlib import Path

from eria_invention_events import build_brief

ROOT = Path(__file__).resolve().parents[1]
CATALOG = json.loads((ROOT / "shared/eria-invention-events/events.json").read_text())


class InventionEventTests(unittest.TestCase):
    def test_dial_three_emits_three_seeds(self):
        brief = build_brief("push", {}, CATALOG, "owner/repo", "refs/heads/core", "abc123")
        self.assertEqual(brief.count("\n1. ") + brief.count("\n2. ") + brief.count("\n3. "), 3)
        self.assertIn("Invention basis dial:** 3/3", brief)

    def test_workflow_failure_is_contextualized(self):
        payload = {"workflow_run": {"name": "CI", "conclusion": "failure"}}
        brief = build_brief("workflow_run", payload, CATALOG, "owner/repo", "refs/heads/core", "abc123")
        self.assertIn("**Conclusion:** failure", brief)
        self.assertIn("minimal reproduction", brief)

    def test_unknown_event_fails_safe_to_generic_proposal(self):
        brief = build_brief("unknown_event", {}, CATALOG, "owner/repo", "ref", "sha")
        self.assertIn("Unclassified forge event", brief)
        self.assertIn("human reviewer", brief)

    def test_proposal_only_guardrails_are_explicit(self):
        guard = CATALOG["guardrails"]
        self.assertFalse(guard["may_commit_or_push"])
        self.assertFalse(guard["may_deploy_or_publish"])
        self.assertTrue(guard["human_review_required_before_implementation"])


if __name__ == "__main__":
    unittest.main()
