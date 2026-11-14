import json
import tempfile
import unittest
from pathlib import Path

from eria_pantheon.resonance import (
    ResonanceHold, acquire_inbox, load_config, synthesize_tone
)


class ResonanceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "storage").mkdir()
        config = {
            "schema": "eria.resonance-console/1.0",
            "mode": "both",
            "requested_volume_percent": 777,
            "maximum_playback_volume_percent": 50,
            "automatic_capture": {
                "preference": "requested", "approval_required": True,
                "enabled": False, "scope": "storage/inbox/"
            }
        }
        (self.root / "storage" / "settings.json").write_text(json.dumps(config))

    def tearDown(self):
        self.temp.cleanup()

    def test_tone_is_wav_and_bounded(self):
        wav = synthesize_tone(440, .1, 50)
        self.assertTrue(wav.startswith(b"RIFF"))
        self.assertIn(b"WAVE", wav[:16])

    def test_rejects_volume_above_hard_limit(self):
        with self.assertRaises(ValueError):
            synthesize_tone(440, .1, 777)

    def test_rejects_out_of_range_frequency(self):
        with self.assertRaises(ValueError):
            synthesize_tone(0, .1, 25)

    def test_acquisition_is_held_until_approved_and_enabled(self):
        (self.root / "storage" / "inbox").mkdir()
        (self.root / "storage" / "inbox" / "sample.txt").write_text("sample")
        with self.assertRaises(ResonanceHold):
            acquire_inbox(self.root)

    def test_settings_preserve_symbolic_request(self):
        config = load_config(self.root)
        self.assertEqual(config["requested_volume_percent"], 777)
        self.assertEqual(config["maximum_playback_volume_percent"], 50)


if __name__ == "__main__":
    unittest.main()
