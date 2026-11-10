import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))
from stride_core.job_engine import JobError, JobStore
from stride_core.job_integrations import (
    connect_faculty_run, connect_geometry_experiment, export_job_snapshot,
    export_android_job_transfer, import_android_job_transfer, import_job_snapshot,
    list_artifacts,
)


class JobIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.store = JobStore(Path(self.temp.name) / "source.sqlite3")
        self.job = self.store.create_job("Integrated journey", "Connect faculties and experiments", "tests")

    def tearDown(self):
        self.temp.cleanup()

    def test_faculty_engine_report_attaches_to_job(self):
        result = connect_faculty_run(
            self.store, self.job["id"], {"signal": 2, "noise": 1},
            ["light", "geometry", "sound"], 3, 4,
            [{"name": "baseband", "carrier_hz": 11.0}],
        )
        self.assertTrue(result["report"]["governance"]["human_review_required"])
        self.assertEqual(list_artifacts(self.store, self.job["id"])[0]["kind"], "faculty_engine_report")

    def test_geometry_experiment_attaches_with_digest_and_job_link(self):
        experiment = {
            "schema": "codexgen-geometry-experiment-v1",
            "workspace": "curvature",
            "title": "Flat-space check",
            "linkedJobId": self.job["id"],
            "parameters": {"curvature": 0.0, "radius": 1.0},
            "diagram": "<svg viewBox='0 0 10 10'></svg>",
        }
        artifact = connect_geometry_experiment(self.store, self.job["id"], experiment)
        self.assertEqual(len(artifact["sha256"]), 64)
        self.assertEqual(list_artifacts(self.store, self.job["id"])[0]["content"], experiment)

    def test_geometry_wrong_job_link_rejected(self):
        experiment = {"schema": "codexgen-geometry-experiment-v1", "workspace": "fractal",
                      "linkedJobId": "another-job", "parameters": {}, "diagram": ""}
        with self.assertRaises(JobError):
            connect_geometry_experiment(self.store, self.job["id"], experiment)

    def test_snapshot_round_trip_and_integrity(self):
        self.store.transition(self.job["id"], "active", stage="make")
        connect_faculty_run(self.store, self.job["id"], {"x": 1}, ["a", "b"], 1, 2,
                            [{"name": "digital", "carrier_hz": 11}])
        snapshot = export_job_snapshot(self.store, self.job["id"])
        target = JobStore(Path(self.temp.name) / "recovered.sqlite3")
        restored = import_job_snapshot(target, snapshot)
        self.assertEqual(restored["id"], self.job["id"])
        self.assertEqual(restored["state"], "active")
        self.assertEqual(len(list_artifacts(target, restored["id"])), 1)
        envelope = json.loads(snapshot)
        envelope["payload"]["job"]["title"] = "tampered"
        with self.assertRaises(JobError):
            import_job_snapshot(target, envelope)

    def test_android_transfer_round_trip(self):
        child = self.store.add_branch(self.job["id"], "Independent path", "Try another route")
        target = JobStore(Path(self.temp.name) / "android-recovered.sqlite3")
        count = import_android_job_transfer(target, export_android_job_transfer(self.store))
        self.assertEqual(count, 2)
        self.assertEqual(target.get_job(child["id"])["parent_id"], self.job["id"])
        with self.assertRaises(JobError):
            import_android_job_transfer(target, export_android_job_transfer(self.store))

    def test_import_never_overwrites_existing_job(self):
        snapshot = export_job_snapshot(self.store, self.job["id"])
        with self.assertRaises(JobError):
            import_job_snapshot(self.store, snapshot)


if __name__ == "__main__":
    unittest.main()
