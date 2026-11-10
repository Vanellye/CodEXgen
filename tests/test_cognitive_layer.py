"""Tests for the append-only CodEXgen cognitive layer."""
import sqlite3
import tempfile
import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "python"))

from cognitive_layer import LedgerError, MemoryEntry, TemporalCognitiveLayer
from codexgen_contracts.envelope import validate_record


def entry(entry_id, statement, *, start=None, end=None, parents=()):
    return MemoryEntry(
        entry_id=entry_id,
        subject="project-direction",
        statement=statement,
        source_ref=f"conversation://{entry_id}",
        recorded_at="2026-11-09T12:00:00Z",
        effective_from=start,
        effective_until=end,
        derived_from=tuple(parents),
    )


class TemporalCognitiveLayerTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.db_path = Path(self.temp_dir.name) / "memory.sqlite3"
        self.layer = TemporalCognitiveLayer(self.db_path)

    def test_appends_and_preserves_lineage(self):
        self.layer.append(entry("origin", "Preserve provenance."))
        self.layer.append(entry("derived", "Add a review stage.", parents=("origin",)))
        self.assertEqual(self.layer.lineage("derived"), ("origin",))
        self.assertEqual(len(self.layer.entries()), 2)


    def test_memory_entry_maps_to_true_north_envelope_without_claim_adjudication(self):
        record = entry("envelope-claim", "A preserved statement.").to_envelope()
        validate_record(record)
        self.assertEqual(record["quality"], "UNKNOWN")
        self.assertEqual(record["authorization"]["status"], "not_authorized")
        self.assertEqual(record["payload"]["statement"], "A preserved statement.")
        self.assertEqual(record["retention"]["policy"], "append_only")

    def test_duplicate_identifier_is_rejected_without_overwrite(self):
        self.layer.append(entry("same-id", "Original statement."))
        with self.assertRaises(LedgerError):
            self.layer.append(entry("same-id", "Replacement statement."))
        self.assertEqual(self.layer.entries()[0].statement, "Original statement.")

    def test_conflicting_overlapping_claims_are_flagged_not_resolved(self):
        self.layer.append(entry(
            "claim-a", "The interface is stable.",
            start="2026-01-01T00:00:00Z", end="2026-12-31T23:59:59Z",
        ))
        self.layer.append(entry(
            "claim-b", "The interface is deprecated.",
            start="2026-06-01T00:00:00Z", end="2027-01-01T00:00:00Z",
        ))
        report = self.layer.reconcile("project-direction")
        self.assertEqual(report.status, "REVIEW_REQUIRED")
        self.assertEqual(report.conflicting_pairs, (("claim-a", "claim-b"),))
        self.assertEqual(len(report.entries), 2)

    def test_non_overlapping_periods_are_not_flagged_as_conflict(self):
        self.layer.append(entry(
            "old", "The interface is experimental.",
            start="2025-01-01T00:00:00Z", end="2025-12-31T23:59:59Z",
        ))
        self.layer.append(entry(
            "new", "The interface is stable.",
            start="2026-01-01T00:00:00Z", end="2026-12-31T23:59:59Z",
        ))
        self.assertEqual(
            self.layer.reconcile("project-direction").status,
            "NO_OVERLAP_CONFLICTS",
        )

    def test_unknown_time_bounds_are_reviewed_conservatively(self):
        self.layer.append(entry("one", "Claim one."))
        self.layer.append(entry("two", "Claim two."))
        self.assertEqual(
            self.layer.reconcile("project-direction").status,
            "REVIEW_REQUIRED",
        )

    def test_missing_parent_is_rejected(self):
        with self.assertRaises(LedgerError):
            self.layer.append(entry("orphan", "Derived claim.", parents=("missing",)))

    def test_timezone_is_required(self):
        bad = MemoryEntry(
            entry_id="bad", subject="s", statement="x", source_ref="src",
            recorded_at="2026-11-09T12:00:00",
        )
        with self.assertRaises(LedgerError):
            self.layer.append(bad)

    def test_database_triggers_reject_mutation(self):
        self.layer.append(entry("protected", "Historical evidence."))
        with sqlite3.connect(self.db_path) as connection:
            with self.assertRaises(sqlite3.IntegrityError):
                connection.execute(
                    "UPDATE memory_entries SET statement = 'rewritten' WHERE entry_id = 'protected'"
                )
            with self.assertRaises(sqlite3.IntegrityError):
                connection.execute(
                    "DELETE FROM memory_entries WHERE entry_id = 'protected'"
                )
        self.assertEqual(self.layer.entries()[0].statement, "Historical evidence.")


if __name__ == "__main__":
    unittest.main()
