import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "python"))
from mirror_oscillation import analyze_oscillation, audit_round_robin, mirror_multiply


class MirrorOscillationTests(unittest.TestCase):
    def test_mirror_multiplication_matches_both_directions(self):
        result = mirror_multiply(7, 9, 63, 63)
        self.assertTrue(result.commutative_match)
        self.assertFalse(result.defect_detected)

    def test_detects_directional_arithmetic_defect(self):
        result = mirror_multiply(7, 9, 63, 62)
        self.assertTrue(result.defect_detected)
        self.assertFalse(result.reverse_matches_expected)

    def test_rejects_non_finite_operands(self):
        with self.assertRaises(ValueError):
            mirror_multiply(float("nan"), 2, 0, 0)

    def test_detects_alternating_samples(self):
        result = analyze_oscillation((1, -1, 1, -1, 1))
        self.assertTrue(result["oscillation_detected"])
        self.assertFalse(result["cause_determined"])

    def test_does_not_flag_constant_samples(self):
        result = analyze_oscillation((4, 4, 4, 4))
        self.assertFalse(result["oscillation_detected"])

    def test_main_round_master_cycles_are_logical_and_read_only(self):
        result = audit_round_robin(("main", "round", "master", "main", "round", "master"))
        self.assertTrue(result["order_valid"])
        self.assertEqual(result["complete_cycles"], 2)
        self.assertFalse(result["branch_mutation_performed"])
        self.assertFalse(result["main_modified"])
        self.assertFalse(result["master_modified"])

    def test_rejects_wrong_lane_order(self):
        result = audit_round_robin(("main", "master", "round"))
        self.assertFalse(result["order_valid"])


if __name__ == "__main__":
    unittest.main()
