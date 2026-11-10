import unittest

from tools.branch_horizon import LENSES, stable_lens


class StableLensTests(unittest.TestCase):
    def test_same_depth_is_reproducible(self):
        self.assertEqual(stable_lens(19), stable_lens(19))

    def test_successive_heads_rotate(self):
        selections = [stable_lens(depth)[1] for depth in range(1, len(LENSES) + 1)]
        self.assertEqual(list(LENSES), selections)

    def test_rotation_wraps_after_all_dimensions(self):
        self.assertEqual(stable_lens(1)[1], stable_lens(len(LENSES) + 1)[1])

    def test_zero_or_negative_depth_is_safe(self):
        self.assertEqual(stable_lens(0), stable_lens(-10))
        self.assertEqual(stable_lens(0)[1], LENSES[0])


if __name__ == "__main__":
    unittest.main()
