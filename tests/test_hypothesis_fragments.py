import sys
import unittest
from dataclasses import replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "python"))
from hypothesis_fragments import MiniBiggerRecord, validate_mini_bigger
from codexgen_contracts.envelope import validate_record


class MiniBiggerRecordTests(unittest.TestCase):
    def record(self):
        return MiniBiggerRecord(
            record_id="mini-001",
            parent_record_id="hypothesis-001",
            label="Subcomponent placeholder",
            description="A small placeholder for a larger hypothetical entity.",
            source_ref="hypotheticals/BRIDGE.md",
            created_at="2026-11-13T12:00:00+00:00",
        )

    def test_emits_parent_linked_non_authorizing_envelope(self):
        envelope = self.record().to_envelope()
        validate_record(envelope)
        self.assertEqual(envelope["payload"]["record_kind"], "mini_bigger")
        self.assertEqual(envelope["payload"]["parent_record_id"], "hypothesis-001")
        self.assertEqual(envelope["payload"]["relationship"], "placeholder_child_of")
        self.assertTrue(envelope["payload"]["is_placeholder"])
        self.assertFalse(envelope["payload"]["runtime_injection_allowed"])
        self.assertEqual(envelope["authorization"]["status"], "not_authorized")
        self.assertEqual(envelope["payload"]["evidence_status"], "not_empirical_evidence")

    def test_rejects_self_parent(self):
        with self.assertRaises(ValueError):
            validate_mini_bigger(replace(self.record(), parent_record_id="mini-001"))

    def test_rejects_empty_parent_identifier(self):
        with self.assertRaises(ValueError):
            validate_mini_bigger(replace(self.record(), parent_record_id=" "))


if __name__ == "__main__":
    unittest.main()
