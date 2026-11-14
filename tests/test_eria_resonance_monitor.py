import json
import tempfile
import time
import unittest
from pathlib import Path

from eria_pantheon.resonance import (
    InboxMonitor, ResonanceHold, acquire_inbox, synthesize_tone
)


class ResonanceMonitorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "storage" / "inbox").mkdir(parents=True)
        (self.root / "storage" / "acquisitions").mkdir()
        self.settings = self.root / "storage" / "settings.json"
        self.settings.write_text(json.dumps({
            "schema": "eria.resonance-console/1.0",
            "mode": "both",
            "requested_volume_percent": 777,
            "maximum_playback_volume_percent": 50,
            "automatic_capture": {
                "preference": "requested", "approval_required": True,
                "enabled": True, "scope": "storage/inbox/",
                "poll_interval_seconds": 2
            }
        }))

    def tearDown(self):
        self.temp.cleanup()

    def grant(self):
        return {"capability": "eria.acquire", "scope": "storage/inbox/",
                "approved": True, "approval_reference": "test-approval"}

    def test_approved_scan_accumulates_with_hash_and_keeps_source(self):
        source = self.root / "storage" / "inbox" / "one.txt"
        source.write_text("original bytes")
        original = source.read_bytes()
        result = acquire_inbox(self.root, approval_grant=self.grant())
        self.assertEqual(len(result["acquired"]), 1)
        self.assertEqual(source.read_bytes(), original)
        index = self.root / "storage" / "acquisitions" / "index.jsonl"
        record = json.loads(index.read_text().splitlines()[0])
        self.assertEqual(record["source_sha256"], __import__("hashlib").sha256(original).hexdigest())
        self.assertEqual(record["authority"], "NON_AUTHORITATIVE")

    def test_duplicate_is_not_accumulated_twice(self):
        (self.root / "storage" / "inbox" / "one.txt").write_text("same")
        acquire_inbox(self.root, approval_grant=self.grant())
        result = acquire_inbox(self.root, approval_grant=self.grant())
        self.assertEqual(len(result["duplicates"]), 1)
        self.assertEqual(len((self.root / "storage" / "acquisitions" / "index.jsonl").read_text().splitlines()), 1)

    def test_missing_approval_is_held(self):
        with self.assertRaises(ResonanceHold):
            acquire_inbox(self.root)

    def test_monitor_pause_and_resume(self):
        (self.root / "storage" / "inbox" / "one.txt").write_text("watch")
        monitor = InboxMonitor(self.root)
        self.assertEqual(monitor.status()["state"], "paused")
        started = monitor.start("explicit-test-approval")
        self.assertEqual(started["state"], "running")
        time.sleep(.2)
        paused = monitor.pause()
        self.assertEqual(paused["state"], "paused")
        self.assertEqual(len((self.root / "storage" / "acquisitions" / "index.jsonl").read_text().splitlines()), 1)

    def test_tone_limit_rejects_777_percent(self):
        with self.assertRaises(ValueError):
            synthesize_tone(440, .1, 777)


if __name__ == "__main__":
    unittest.main()
