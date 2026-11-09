import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))
from stride_core.job_engine import JobError, JobMetric, JobStore


class JobEngineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.store = JobStore(Path(self.temp.name) / "jobs.sqlite3")

    def tearDown(self):
        self.temp.cleanup()

    def test_create_and_persist_job(self):
        job = self.store.create_job("Geometry study", "Compare projections", "geometry-lab")
        loaded = self.store.get_job(job["id"])
        self.assertEqual(loaded["state"], "open")
        self.assertEqual(loaded["stage"], "notice")
        self.assertEqual(loaded["purpose"], "Compare projections")

    def test_lifecycle_and_pause_recovery(self):
        job = self.store.create_job("Build", "Explore a feature", "stride")
        self.store.transition(job["id"], "active", stage="make")
        paused = self.store.transition(job["id"], "paused", reason="Contributor chose to pause")
        self.assertEqual(paused["state"], "paused")
        resumed = self.store.transition(job["id"], "active", stage="examine")
        self.assertEqual(resumed["stage"], "examine")

    def test_branch_keeps_independent_identity(self):
        parent = self.store.create_job("Main exploration", "Explore options", "user")
        child = self.store.add_branch(parent["id"], "Alternative path", "Test a different method")
        self.assertNotEqual(parent["id"], child["id"])
        self.assertEqual(child["parent_id"], parent["id"])
        self.assertEqual(self.store.list_children(parent["id"])[0]["id"], child["id"])

    def test_completed_job_requires_explicit_reopen(self):
        job = self.store.create_job("Close", "Finish a task", "user")
        self.store.transition(job["id"], "completed")
        with self.assertRaises(JobError):
            self.store.transition(job["id"], "active")
        self.assertEqual(self.store.transition(job["id"], "active", reopen=True)["state"], "active")

    def test_metric_requires_context_and_never_aggregates_worth(self):
        job = self.store.create_job("Experiment", "Measure runtime", "lab")
        metric = JobMetric("elapsed", 2.5, "seconds", "monotonic clock",
                           "single run", "local test", "single observation; not a quality score")
        self.store.record_metric(job["id"], metric)
        self.assertEqual(self.store.list_metrics(job["id"])[0], metric)
        self.assertEqual(len(self.store.events(job["id"])), 2)

    def test_invalid_transition_and_nonfinite_metric_rejected(self):
        job = self.store.create_job("Archived", "Keep record", "user")
        self.store.transition(job["id"], "archived")
        with self.assertRaises(JobError):
            self.store.transition(job["id"], "active")
        active = self.store.create_job("Metric", "Test bounds", "user")
        bad = JobMetric("bad", float("nan"), "x", "test", "now", "test", "invalid")
        with self.assertRaises(JobError):
            self.store.record_metric(active["id"], bad)


if __name__ == "__main__":
    unittest.main()
