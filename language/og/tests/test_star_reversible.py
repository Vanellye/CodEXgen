import unittest
from language.og.reference.star_reversible import encode_bytes, decode_bytes

class StarCodecTests(unittest.TestCase):
    def test_round_trip_all_byte_values(self):
        data = bytes(range(256))
        self.assertEqual(decode_bytes(encode_bytes(data)), data)

    def test_empty(self):
        self.assertEqual(decode_bytes(encode_bytes(b"")), b"")

    def test_rejects_bad_prefix(self):
        with self.assertRaises(ValueError):
            decode_bytes("bad:")

    def test_rejects_bad_group(self):
        with self.assertRaises(ValueError):
            decode_bytes("Ɣơ/2:☆k")

if __name__ == "__main__":
    unittest.main()
