import sys, tempfile, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))
from stride_core.medium_signal_engine import (HAZE, WATER, ModelSafetyError, SignalSpec,
    acoustic_interaction, gamma_detector_model, optical_interaction, run_medium_suite,
    simulate_digital_signal)
from olpirt.rise_wisdom_bridge import RiseWisdomBridge

class MediumSignalTests(unittest.TestCase):
    def test_haze_water_and_both_signal_bands(self):
        result = run_medium_suite({"event": "rise"}, 2.0)
        self.assertIn("haze", result["media"]); self.assertIn("water", result["media"])
        self.assertEqual(result["signals"]["11_hz"]["frequency_hz"], 11.0)
        self.assertEqual(result["signals"]["1111_hz"]["frequency_hz"], 1111.0)
    def test_optical_path_attenuation(self):
        self.assertLess(optical_interaction(HAZE, 2).transmittance, optical_interaction(HAZE, 1).transmittance)
    def test_acoustic_absorption(self):
        self.assertLess(acoustic_interaction(WATER, 10).amplitude_ratio, 1.0)
    def test_passive_gamma_detector_estimate(self):
        result = gamma_detector_model(662, 0.08, 2, 10000, 0.3)
        self.assertGreater(result.expected_detected_counts, 0)
        self.assertLess(result.uncollided_transmission, 1)
    def test_bounds(self):
        with self.assertRaises(ModelSafetyError):
            simulate_digital_signal({"x": 1}, SignalSpec(frequency_hz=5000, sample_rate_hz=10000))
    def test_deterministic_payload_digest(self):
        self.assertEqual(simulate_digital_signal({"a": 1}).digest_sha256,
                         simulate_digital_signal({"a": 1}).digest_sha256)
    def test_bridge_is_idempotent(self):
        with tempfile.TemporaryDirectory() as td:
            calls = []
            bridge = RiseWisdomBridge(Path(td) / "wisdom.db", wisdom_sink=calls.append)
            bridge.record_revision("worker-1", 1, "RISING", "RECOVERED", "health check passed")
            bridge.record_revision("worker-1", 1, "RISING", "RECOVERED", "health check passed")
            self.assertEqual(bridge.count(), 1)
            self.assertEqual(len(calls), 1)

if __name__ == "__main__": unittest.main()
