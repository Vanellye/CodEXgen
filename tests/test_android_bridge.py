import json
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))

from stride_core.job_engine import JobError, JobStore
from stride_core.job_integrations import (
    export_job_snapshot, import_job_snapshot, list_artifacts,
)
from stride_core.android_bridge import make_server


class AndroidBridgeEndToEndTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp.name) / "stride.sqlite3"
        self.store = JobStore(self.db_path)
        self.token = "bridge-test-token-with-at-least-24-chars"
        self.server = make_server(self.store, self.token, host="127.0.0.1", port=0)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.base = "http://127.0.0.1:%d" % self.server.server_address[1]

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=3)
        self.temp.cleanup()

    def request(self, method, path, payload=None, token=None):
        data = None if payload is None else json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(self.base + path, data=data, method=method)
        request.add_header("Authorization", "Bearer " + (token or self.token))
        request.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(request, timeout=5) as response:
                return response.status, json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as error:
            return error.code, json.loads(error.read().decode("utf-8"))

    def test_authenticated_bridge_artifact_persistence_and_snapshot_recovery(self):
        transfer = {
            "schema": "codexgen.android.jobs.v1",
            "jobs": [{
                "id": "android-job-001", "title": "Bridge verification",
                "purpose": "Exercise Faculty and Geometry handoffs",
                "state": "active", "stage": "make", "parent_id": None,
                "created_at": 1794240000000, "updated_at": 1794240000000,
            }],
            "events": [{
                "job_id": "android-job-001", "event_type": "created",
                "detail": "Android dashboard fixture", "created_at": 1794240000000,
            }],
        }
        status, denied = self.request("POST", "/v1/jobs/import-android", transfer,
                                      token="incorrect-token")
        self.assertEqual(status, 401)
        status, imported = self.request("POST", "/v1/jobs/import-android", transfer)
        self.assertEqual(status, 201)
        self.assertEqual(imported["imported_jobs"], 1)

        faculty = {
            "observations": {"signal": 2.0, "noise": 1.0},
            "concepts": ["light", "geometry"],
            "prediction": 3.0, "measured": 4.0,
            "channels": [{"name": "baseband", "carrier_hz": 11.0}],
        }
        status, faculty_result = self.request(
            "POST", "/v1/jobs/android-job-001/faculty", faculty)
        self.assertEqual(status, 200)
        self.assertEqual(faculty_result["artifact"]["kind"], "faculty_engine_report")
        self.assertTrue(faculty_result["report"]["governance"]["human_review_required"])

        geometry = {
            "schema": "codexgen-geometry-experiment-v1",
            "workspace": "curvature", "title": "Persistence fixture",
            "linkedJobId": "android-job-001",
            "parameters": {"curvature": 0.0, "radius": 2.0},
            "diagram": "<svg viewBox='0 0 10 10'></svg>",
        }
        status, geometry_result = self.request(
            "POST", "/v1/jobs/android-job-001/geometry", geometry)
        self.assertEqual(status, 201)
        self.assertEqual(geometry_result["artifact"]["kind"], "geometry_experiment")

        status, listing = self.request("GET", "/v1/jobs/android-job-001/artifacts")
        self.assertEqual(status, 200)
        self.assertEqual(len(listing["artifacts"]), 2)
        digests = {item["kind"]: item["sha256"] for item in listing["artifacts"]}
        self.assertEqual(len(digests["faculty_engine_report"]), 64)
        self.assertEqual(len(digests["geometry_experiment"]), 64)

        # Restart the service over the same SQLite file: artifacts must survive.
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=3)
        self.store = JobStore(self.db_path)
        self.server = make_server(self.store, self.token, host="127.0.0.1", port=0)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.base = "http://127.0.0.1:%d" % self.server.server_address[1]
        status, after_restart = self.request("GET", "/v1/jobs/android-job-001/artifacts")
        self.assertEqual(status, 200)
        self.assertEqual(
            {item["kind"]: item["sha256"] for item in after_restart["artifacts"]},
            digests,
        )

        snapshot = export_job_snapshot(self.store, "android-job-001")
        recovered = JobStore(Path(self.temp.name) / "recovered.sqlite3")
        restored = import_job_snapshot(recovered, snapshot)
        self.assertEqual(restored["id"], "android-job-001")
        self.assertEqual(len(list_artifacts(recovered, restored["id"])), 2)
        envelope = json.loads(snapshot)
        envelope["payload"]["artifacts"][0]["content"]["tampered"] = True
        with self.assertRaises(JobError):
            import_job_snapshot(JobStore(Path(self.temp.name) / "tampered.sqlite3"), envelope)


if __name__ == "__main__":
    unittest.main()
