import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))

from stride_core.holified_inception import (
    ContextItem, HolifiedInputError, read_beyond_present,
)


class HolifiedInceptionTests(unittest.TestCase):
    def test_reads_present_and_preserves_origin_labels(self):
        source = ContextItem(
            "origin-1", "Original observation", "observed", "local-note"
        )
        report = read_beyond_present("Current question", [source])
        self.assertEqual(report.present, "Current question")
        self.assertEqual(report.origins[0]["item_id"], "origin-1")
        self.assertEqual(report.origins[0]["evidence"], "observed")
        self.assertFalse(report.governance["source_mutation"])

    def test_explicit_links_are_mapped_without_inventing_relationships(self):
        items = [
            ContextItem("a", "First", "observed", "note-a", ("b",)),
            ContextItem("b", "Second", "verified", "test-b"),
        ]
        report = read_beyond_present("Now", items)
        self.assertEqual(len(report.connections), 1)
        self.assertEqual(report.connections[0].relationship, "explicit_context_reference")
        self.assertEqual(report.connections[0].evidence, "observed")

    def test_missing_link_target_remains_unknown(self):
        report = read_beyond_present(
            "Now", [ContextItem("a", "First", "observed", "note", ("missing",))]
        )
        self.assertEqual(len(report.connections), 0)
        self.assertIn("remains unknown", report.tensions[0])

    def test_disputed_and_unknown_context_are_not_promoted(self):
        report = read_beyond_present("Now", [
            ContextItem("u", "Unresolved claim", "disputed", "archive"),
        ])
        self.assertEqual(report.discernment[0]["status"], "disputed")
        self.assertIn("not settled", report.tensions[0])

    def test_existing_perception_helper_is_used_as_read_only_input(self):
        report = read_beyond_present(
            "Now", observations={"signal": 3, "noise": 1}
        )
        self.assertEqual(report.perception["strongest_feature"], "signal")
        self.assertFalse(report.governance["external_actions"])

    def test_existing_creativity_helper_is_used_but_labeled_hypothesis(self):
        report = read_beyond_present(
            "Now", creative_concepts=["light", "water", "sound"]
        )
        self.assertTrue(report.possibilities[0].startswith("[hypothesis]"))
        self.assertIsNotNone(report.creativity_seed)
        self.assertFalse(report.governance["fiction_promoted_to_fact"])

    def test_no_context_is_reported_as_a_limitation(self):
        report = read_beyond_present("Only the present")
        self.assertIn("No additional context", report.tensions[0])

    def test_duplicate_ids_and_bad_evidence_are_rejected(self):
        with self.assertRaises(HolifiedInputError):
            read_beyond_present("Now", [
                ContextItem("same", "One"),
                ContextItem("same", "Two"),
            ])
        with self.assertRaises(HolifiedInputError):
            read_beyond_present("Now", [
                ContextItem("bad", "Claim", "certain", "unknown-source"),
            ])

    def test_report_is_json_ready_and_does_not_mutate_context(self):
        original = ContextItem("x", "Keep me", "observed", "user")
        report = read_beyond_present("Now", [original])
        self.assertEqual(original.content, "Keep me")
        self.assertEqual(report.to_dict()["governance"]["mode"], "read_only_context_analysis")


if __name__ == "__main__":
    unittest.main()
