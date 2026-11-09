import sys
from pathlib import Path
import unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))
from stride_core.faculty_engine import (
    FacultyInputError, adapt_prediction, assess_perception, coordinate_channels,
    generate_ideas, run_faculty_suite,
)

class FacultyEngineTests(unittest.TestCase):
    def test_perception_ranks_weighted_features(self):
        result = assess_perception({"signal": 3, "noise": 2}, {"signal": 2})
        self.assertEqual(result.strongest_feature, "signal")
        self.assertGreater(result.confidence, 0.5)

    def test_creativity_is_deterministic_and_bounded(self):
        a = generate_ideas(["light", "water", "sound"], 2)
        b = generate_ideas(["light", "water", "sound"], 2)
        self.assertEqual(a.seed_digest, b.seed_digest)
        self.assertEqual(len(a.combinations), 2)

    def test_adaptation_reduces_error(self):
        result = adapt_prediction(10, 14, 0.5)
        self.assertLess(result.posterior_error, result.prior_error)
        self.assertEqual(result.corrected_prediction, 12)

    def test_channel_plan_is_metadata_only(self):
        plan = coordinate_channels([
            {"name": "perception", "carrier_hz": 11},
            {"name": "creativity", "carrier_hz": 1111, "mode": "digital"},
        ])
        self.assertEqual(plan[0].phase_degrees, 0)
        self.assertEqual(plan[1].phase_degrees, 180)

    def test_suite_governance(self):
        result = run_faculty_suite({"signal": 1}, ["art", "science"], 2, 3,
                                   [{"name": "core", "carrier_hz": 11}])
        self.assertFalse(result["governance"]["physical_emission"])
        self.assertTrue(result["governance"]["human_review_required"])

    def test_rejects_invalid_gain_and_emitter_mode(self):
        with self.assertRaises(FacultyInputError):
            adapt_prediction(1, 2, 1.5)
        with self.assertRaises(FacultyInputError):
            coordinate_channels([{"name": "unsafe", "carrier_hz": 11, "mode": "emitter"}])

if __name__ == "__main__":
    unittest.main()
