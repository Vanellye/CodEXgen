import sys
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))
from yoro_star_codec import decode_bytes, encode_bytes, validate_vectors

class SharedVectorTests(unittest.TestCase):
    def test_shared_vectors(self):
        self.assertEqual(validate_vectors(ROOT / "test-vectors" / "yoro-star-v2.tsv"), 8)
    def test_all_single_bytes(self):
        for value in range(256):
            raw = bytes([value])
            self.assertEqual(decode_bytes(encode_bytes(raw)), raw)
    def test_rejects_bad_group(self):
        with self.assertRaises(ValueError):
            decode_bytes("Ɣơ/2:kkkk")

if __name__ == "__main__":
    unittest.main()
