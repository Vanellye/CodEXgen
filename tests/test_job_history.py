import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))

from stride_core.job_engine import JobStore
from stride_core.job_history import JobHistoryAccessError, recall_job_history


class JobHistoryTests(unittest.TestCase):
    def setUp(self):
        self.store = JobStore(":memory:")
        self.job = self.store.create_job(
            "Historical reader", "Test opt-in history", "unit-test", job_id="job-history"
        )

    def test_access_requires_explicit_authorization_before_store_reads(self):
        class NoReadStore:
            def get_job(self, job_id):
                raise AssertionError("store must not be read before authorization")
            def events(self, job_id):
                raise AssertionError("store must not be read before authorization")

        with self.assertRaises(JobHistoryAccessError):
            recall_job_history(NoReadStore(), ["job-history"])

    def test_selected_job_events_are_recalled_with_provenance(self):
        report = recall_job_history(
            self.store, ["job-history"], authorized=True
        )
        self.assertTrue(report.events)
        self.assertEqual(report.events[0].job_id, "job-history")
        self.assertEqual(
            report.events[0].source_ref,
            f"job:job-history:event:{report.events[0].sequence}",
        )
        self.assertTrue(report.governance["source_mutation"] is False)

    def test_reverse_recall_is_exact_reverse_of_forward_event_order(self):
        self.store.transition("job-history", "active", reason="start")
        self.store.transition("job-history", "paused", reason="pause")
        forward = recall_job_history(
            self.store, ["job-history"], authorized=True
        )
        backward = recall_job_history(
            self.store, ["job-history"], authorized=True, reverse=True
        )
        self.assertEqual(
            [event.source_ref for event in backward.events],
            list(reversed([event.source_ref for event in forward.events])),
        )

    def test_changed_recorded_field_is_reported_without_adjudication(self):
        self.store.transition("job-history", "active", reason="start")
        self.store.transition("job-history", "paused", reason="pause")
        report = recall_job_history(
            self.store, ["job-history"], authorized=True
        )
        state_conflicts = [
            conflict for conflict in report.contradictions
            if conflict.field == "to"
        ]
        self.assertTrue(state_conflicts)
        self.assertEqual(state_conflicts[0].status, "conflicting_recorded_values")
        self.assertEqual(state_conflicts[0].earlier_value, "active")
        self.assertEqual(state_conflicts[0].later_value, "paused")
        reversed_report = recall_job_history(
            self.store, ["job-history"], authorized=True, reverse=True
        )
        reverse_conflict = next(
            item for item in reversed_report.contradictions if item.field == "to"
        )
        self.assertEqual(reverse_conflict.earlier_value, "active")
        self.assertEqual(reverse_conflict.later_value, "paused")

    def test_history_reader_does_not_change_source_event_count(self):
        before = self.store.events("job-history")
        recall_job_history(self.store, ["job-history"], authorized=True)
        after = self.store.events("job-history")
        self.assertEqual(before, after)

    def test_explicit_job_selection_and_bounds_are_required(self):
        with self.assertRaises(ValueError):
            recall_job_history(self.store, [], authorized=True)
        with self.assertRaises(ValueError):
            recall_job_history(
                self.store, ["job-history"], authorized=True, limit_per_job=0
            )


if __name__ == "__main__":
    unittest.main()
