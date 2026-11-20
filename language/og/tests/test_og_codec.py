import random
import unittest

from language.og.reference.og_codec import (
    OgCodecError,
    decode,
    encode,
)


class OgCodecTests(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(decode(encode(b"")), b"")

    def test_all_byte_values(self):
        original = bytes(range(256))
        self.assertEqual(decode(encode(original)), original)

    def test_zero_and_leading_zero_bytes(self):
        original = bytes.fromhex("0000000100007fff")
        self.assertEqual(decode(encode(original)), original)

    def test_single_zero_is_explicit(self):
        encoded = encode(b"\x00")
        self.assertIn("ba-ba-ba-ba", encoded)
        self.assertEqual(decode(encoded), b"\x00")

    def test_random_round_trips(self):
        rng = random.Random(20261119)
        for length in (1, 2, 3, 16, 127, 1024):
            original = bytes(rng.randrange(256) for _ in range(length))
            with self.subTest(length=length):
                self.assertEqual(decode(encode(original)), original)

    def test_non_canonical_spacing_rejected(self):
        # Two bytes are required to produce the canonical byte separator.
        encoded = encode(b"\x01\x02")
        self.assertIn(", ", encoded)
        malformed = encoded.replace(", ", ",")
        self.assertNotEqual(malformed, encoded)
        with self.assertRaises(OgCodecError):
            decode(malformed)

    def test_length_mismatch_rejected(self):
        encoded = encode(b"\x01").replace("length:1", "length:2")
        with self.assertRaises(OgCodecError):
            decode(encoded)

    def test_unknown_profile_rejected(self):
        encoded = encode(b"\x01").replace("0.1", "9.9")
        with self.assertRaises(OgCodecError):
            decode(encoded)

    def test_unknown_glyph_rejected(self):
        encoded = encode(b"\x01").replace("be", "bx")
        with self.assertRaises(OgCodecError):
            decode(encoded)

    def test_byte_overflow_rejected(self):
        # uuuu is base-5 624, above the byte range.
        encoded = encode(b"\x01").replace("ba-ba-ba-be", "bu-bu-bu-bu")
        with self.assertRaises(OgCodecError):
            decode(encoded)

    def test_bad_header_rejected(self):
        with self.assertRaises(OgCodecError):
            decode("OG/1\nkind:BYTES\nlength:0\npayload:empty\ncodec:og-base5-syllables/0.1")

    def test_declared_resource_limit_rejected(self):
        oversized = "OG/0\nkind:BYTES\nlength:1000001\npayload:empty\ncodec:og-base5-syllables/0.1"
        with self.assertRaises(OgCodecError):
            decode(oversized)

    def test_repository_examples_decode(self):
        from pathlib import Path
        root = Path(__file__).resolve().parents[1]
        for filename in ("empty.og", "zero-and-one.og", "sample-bytes.og"):
            with self.subTest(filename=filename):
                self.assertIsInstance(decode((root / "examples" / filename).read_text(encoding="utf-8")), bytes)

    def test_no_extra_whitespace_or_duplicate_lines(self):
        encoded = encode(b"\x00")
        with self.assertRaises(OgCodecError):
            decode(encoded + "\n\n")
        with self.assertRaises(OgCodecError):
            decode(encoded.replace("kind:BYTES", "kind:BYTES\nkind:BYTES"))

    def test_non_ascii_length_rejected(self):
        encoded = encode(bytes([0])).replace("length:1", "length:１")
        with self.assertRaises(OgCodecError):
            decode(encoded)

    def test_every_byte_round_trips_individually(self):
        for value in range(256):
            with self.subTest(value=value):
                original = bytes([value])
                self.assertEqual(decode(encode(original)), original)

    def test_payload_with_wrong_token_count_rejected(self):
        encoded = encode(bytes([0, 1]))
        shortened = encoded.replace(", ba-ba-ba-be", "")
        with self.assertRaises(OgCodecError):
            decode(shortened)

    def test_payload_with_extra_token_rejected(self):
        encoded = encode(bytes([0]))
        extra = encoded.replace(
            "payload:ba-ba-ba-ba",
            "payload:ba-ba-ba-ba, ba-ba-ba-ba",
        )
        with self.assertRaises(OgCodecError):
            decode(extra)

    def test_payload_with_invalid_digit_count_rejected(self):
        encoded = encode(bytes([0])).replace(
            "ba-ba-ba-ba",
            "ba-ba-ba",
        )
        with self.assertRaises(OgCodecError):
            decode(encoded)

    def test_payload_with_noncanonical_token_space_rejected(self):
        encoded = encode(bytes([0, 1])).replace(", ", ",  ")
        with self.assertRaises(OgCodecError):
            decode(encoded)


if __name__ == "__main__":
    unittest.main()
