import unittest
from language.og.reference.star_lossy import encode_bytes_lossy

class LossyStarCodecTests(unittest.TestCase):
    def test_zero_bits_are_removed(self):
        self.assertEqual(encode_bytes_lossy(bytes([0b01000001])), "Ɣơ/L1:kk")

    def test_byte_boundaries_are_retained_as_groups(self):
        self.assertEqual(encode_bytes_lossy(bytes([0, 255])), "Ɣơ/L1:.kkkkkkkk")

    def test_empty_input(self):
        self.assertEqual(encode_bytes_lossy(b""), "Ɣơ/L1:")

if __name__ == "__main__":
    unittest.main()
