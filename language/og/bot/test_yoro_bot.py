import unittest
from language.og.bot.yoro_bot import transform

class YoroBotTests(unittest.TestCase):
    def test_reversible_profile(self):
        self.assertEqual(transform(bytes([0x41]), "reversible"), "Ɣơ/2:☆k☆☆☆☆☆k")

    def test_lossy_profile(self):
        self.assertEqual(transform(bytes([0x41]), "lossy"), "Ɣơ/L1:kk")

    def test_unknown_profile_rejected(self):
        with self.assertRaises(ValueError):
            transform(b"x", "unknown")

if __name__ == "__main__":
    unittest.main()
