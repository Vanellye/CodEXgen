import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))

from stride_core.job_engine import JobStore
from stride_core.job_reconciliation import (
    CorrectionLedger, ReconciliationError,
)


class JobReconciliationTests(unittest.TestCase):
    def setUp(self):
        self.jobs = JobStore(":memory:")
        self.jobs.create_job(
            "Reconciliation", "Preserve original event", "test", job_id="reconcile-job"
        )
        self.event = self.jobs.events("reconcile-job")[0]
        self.source_ref = f"job:reconcile-job:event:{self.event['sequence']}"
        self.ledger = CorrectionLedger(":memory:")

    def propose(self, value="Corrected title"):
        return self.ledger.append_correction(
            job_id="reconcile-job",
            source_ref=self.source_ref,
            field="title",
            proposed_value=value,
            evidence="Signed source document ref: evidence-17",
            rationale="The original title was transcribed incorrectly.",
            author="reviewer-a",
            authorized=True,
        )

    def test_correction_requires_explicit_authorization(self):
        with self.assertRaises(PermissionError):
            self.ledger.append_correction(
                job_id="reconcile-job", source_ref=self.source_ref,
                field="title", proposed_value="X", evidence="E",
                rationale="R", author="A"
            )

    def test_proposal_is_visible_but_does_not_change_derived_view(self):
        original_before = self.jobs.events("reconcile-job")
        correction = self.propose()
        view = self.ledger.reconcile(
            self.jobs, "reconcile-job", self.source_ref
        )
        self.assertEqual(view.interpretation_status[correction.correction_id], "proposed")
        self.assertEqual(view.derived_payload["title"], view.source_event["payload"]["title"])
        self.assertEqual(self.jobs.events("reconcile-job"), original_before)
        self.assertTrue(view.source_preserved)

    def test_accepted_correction_changes_overlay_not_original_event(self):
        correction = self.propose()
        self.ledger.append_review(
            correction.correction_id, decision="accepted",
            evidence="Evidence checked against source document.",
            rationale="The cited source supports the proposed value.",
            reviewer="reviewer-b", authorized=True,
        )
        view = self.ledger.reconcile(
            self.jobs, "reconcile-job", self.source_ref
        )
        self.assertEqual(view.derived_payload["title"], "Corrected title")
        self.assertNotEqual(
            view.source_event["payload"]["title"], "Corrected title"
        )
        self.assertEqual(
            self.jobs.events("reconcile-job")[0]["payload"]["title"],
            view.source_event["payload"]["title"],
        )

    def test_declined_correction_remains_visible_but_not_applied(self):
        correction = self.propose()
        self.ledger.append_review(
            correction.correction_id, decision="declined",
            evidence="Evidence does not support the change.",
            rationale="Insufficient corroboration.",
            reviewer="reviewer-b", authorized=True,
        )
        view = self.ledger.reconcile(
            self.jobs, "reconcile-job", self.source_ref
        )
        self.assertEqual(view.interpretation_status[correction.correction_id], "declined")
        self.assertNotEqual(view.derived_payload["title"], "Corrected title")

    def test_review_history_is_append_only_and_can_reverse_a_decision(self):
        correction = self.propose()
        first = self.ledger.append_review(
            correction.correction_id, decision="accepted",
            evidence="Evidence A", rationale="Accept for now.",
            reviewer="reviewer-b", authorized=True,
        )
        second = self.ledger.append_review(
            correction.correction_id, decision="declined",
            evidence="New evidence B", rationale="New evidence changes assessment.",
            reviewer="reviewer-c", authorized=True,
        )
        view = self.ledger.reconcile(
            self.jobs, "reconcile-job", self.source_ref
        )
        self.assertEqual(len(view.reviews), 2)
        self.assertEqual(view.reviews[0].review_id, first.review_id)
        self.assertEqual(view.reviews[1].review_id, second.review_id)
        self.assertEqual(view.interpretation_status[correction.correction_id], "declined")

    def test_wrong_source_reference_is_rejected(self):
        with self.assertRaises(ReconciliationError):
            self.ledger.reconcile(self.jobs, "reconcile-job", "job:wrong:event:9")


if __name__ == "__main__":
    unittest.main()
